import json,subprocess,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from codex_translation import CodexTranslation,TranslationServiceError
from page_pipeline import process_pages

class TranslationClientTests(unittest.TestCase):
    def test_bootstrap_reports_missing_dependencies_before_importing_pipeline(self):
        import sys
        script=Path(__file__).resolve().parents[1]/'backend/native_job.py'
        with tempfile.TemporaryDirectory() as d:
            job=Path(d)/'job.json';job.write_text('{}')
            # -S deliberately hides site-packages in this same dedicated runtime.
            result=subprocess.run([sys.executable,'-S',str(script),str(job)],capture_output=True)
            state=json.loads(job.with_suffix('.status.json').read_text(encoding='utf-8'))
            self.assertEqual(result.returncode,1)
            self.assertEqual(state['status'],'error')
            self.assertIn('setup.ps1',state['message'])

    def test_model_routing_uses_luna_for_text_and_sol_for_complex_or_scanned_pages(self):
        from layout_reader import LayoutACP
        client=LayoutACP.__new__(LayoutACP);client.config={};client.last_metadata={}
        defaults={'model':'gpt-6-luna','vision_model':'gpt-6.1-sol'}
        geometry={'width':100,'height':100,'images':[], 'regions':[
            {'id':'t1','bbox':[1,1,9,9],'en':'Flood','size':8,'angle':0}]}
        response=json.dumps({'page':1,'translations':[{'id':'t1','zh':'洪水'}],'raster':[]})
        with patch('layout_reader.settings',return_value=defaults),patch.object(client,'request',return_value=response):
            client.layout(1,geometry,None,{},None,None)
            self.assertEqual(client.config['model'],'gpt-6-luna')
            geometry['complex_graphics']=True
            client.layout(1,geometry,None,{},None,None)
            self.assertEqual(client.config['model'],'gpt-6.1-sol')
            geometry.update(regions=[],complex_graphics=False)
            with patch('layout_reader.parse_layout',return_value={}):
                client.layout(1,geometry,None,{},None,None)
            self.assertEqual(client.config['model'],'gpt-6.1-sol')

    def client(self,root):
        with patch('codex_translation.find_codex',return_value='codex.exe'), \
             patch('codex_translation.load_settings',return_value={'codex_path':'codex.exe'}), \
             patch('codex_translation.cloud_environment',return_value={'CODEX_HOME':'isolated-test'}):
            return CodexTranslation(root)

    def test_result_metadata_and_ephemeral_command(self):
        with tempfile.TemporaryDirectory() as d:
            c=self.client(d)
            def run(args,**kw):
                self.assertIn('--ephemeral',args)
                self.assertIn('--ignore-user-config',args)
                self.assertIn('read-only',args)
                self.assertNotIn('--dangerously-bypass-approvals-and-sandbox',args)
                self.assertEqual(kw['input'],'translate')
                self.assertEqual(kw['env']['CODEX_HOME'],'isolated-test')
                Path(args[args.index('--output-last-message')+1]).write_text('{"zh":"洪水"}',encoding='utf-8')
                events=[{'type':'thread.started','thread_id':'temporary'},
                        {'type':'turn.completed','usage':{'input_tokens':9,'output_tokens':4}}]
                return SimpleNamespace(returncode=0,stdout='\n'.join(map(json.dumps,events)),stderr='')
            with patch('codex_translation.subprocess.run',side_effect=run):
                self.assertEqual(json.loads(c.request('translate'))['zh'],'洪水')
            self.assertEqual(c.last_metadata['usage']['output_tokens'],4)
            self.assertEqual(list(Path(d).iterdir()),[])

    def test_timeout_is_bounded_and_temporary_files_cleaned(self):
        with tempfile.TemporaryDirectory() as d:
            c=self.client(d)
            with patch('codex_translation.subprocess.run',side_effect=subprocess.TimeoutExpired('codex',240)):
                with self.assertRaises(TimeoutError):c.request('translate')
            self.assertEqual(list(Path(d).iterdir()),[])

    def test_global_failure_stops_spending_on_remaining_pages(self):
        calls=[]
        def run(page,attempt):
            calls.append(page)
            if page==2:raise TranslationServiceError('quota')
        state=process_pages([1,2,3],run,lambda p:False,progress=lambda s:None)
        self.assertEqual(calls,[1,2]);self.assertEqual(state['completed_pages'],[1])
        self.assertEqual(state['status'],'error')

    def test_auth_error_not_exposed_or_retried(self):
        with tempfile.TemporaryDirectory() as d:
            c=self.client(d)
            result=SimpleNamespace(returncode=1,stdout=json.dumps({'type':'error','message':'401 unauthorized'}),stderr='private diagnostic')
            with patch('codex_translation.subprocess.run',return_value=result):
                with self.assertRaises(TranslationServiceError) as exc:c.request('x')
            self.assertIn('登录',str(exc.exception));self.assertNotIn('private',str(exc.exception))

    def test_service_failure_preserves_later_cached_pages(self):
        def fail(page,attempt):raise TranslationServiceError('quota')
        state=process_pages([1,2,3],fail,lambda p:p==3,progress=lambda s:None)
        self.assertEqual(state['completed_pages'],[3])
        self.assertEqual(state['status'],'error')

    def test_diagonal_label_does_not_erase_graphics(self):
        import pymupdf as f
        from layout_reader import translated_page
        src=f.open();p=src.new_page(width=300,height=300)
        p.draw_line((20,20),(150,150),color=(1,0,0),width=3)
        data={'geometry':{'regions':[]},'translations':[],
              'raster':[{'bbox':[60,60,510,510],'en':'City of Leicester boundary','zh':'莱斯特市边界','lines':1,'angle':0}]}
        qa=[];out=translated_page(src,1,data,qa)
        self.assertEqual(src[0].get_pixmap().samples,out[0].get_pixmap().samples)
        self.assertEqual(qa[0]['source'],'raster_preserved')
        out.close();src.close()

    def test_tiny_label_is_preserved_instead_of_failing_whole_page(self):
        import pymupdf as f
        from layout_reader import translated_page
        src=f.open();src.new_page(width=595,height=785)
        data={'geometry':{'regions':[]},'translations':[],
              'raster':[{'bbox':[164,150,190,153],'en':'Glenfield Hospital','zh':'格伦菲尔德医院','lines':1,'angle':0}]}
        qa=[];out=translated_page(src,1,data,qa)
        self.assertEqual(qa[0]['source'],'raster_preserved')
        out.close();src.close()

    def test_pdf_cache_is_reused_and_invalidated_on_translation_change(self):
        import pymupdf as f
        import layout_reader
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);source=root/'source.pdf';doc=f.open();doc.new_page();doc.save(source);doc.close()
            jp=root/'page-0001.json';jp.write_text('{}')
            manifest={'source_path':str(source),'source_name':source.name,'requested_pages':[1],'completed_pages':[1],'total_pages':1}
            calls=[]
            def render(src,n,data,qa):
                calls.append(n);out=f.open();out.insert_pdf(src);return out
            with patch.object(layout_reader,'translated_page',side_effect=render):
                first=layout_reader.write_aligned_pdf(root,manifest,progress=lambda s:None)
                before=first.read_bytes()
                layout_reader.write_aligned_pdf(root,manifest,progress=lambda s:None)
                self.assertEqual(calls,[1]);self.assertEqual(before,first.read_bytes())
                jp.write_text('{"changed":true}')
                layout_reader.write_aligned_pdf(root,manifest,progress=lambda s:None)
                self.assertEqual(calls,[1,1])

if __name__=='__main__':unittest.main()
