import json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import pymupdf as fitz
import layout_reader,native_job
from page_pipeline import process_pages

class LayoutRecoveryTest(unittest.TestCase):
    def test_bad_layout_json_continues_then_retries(self):
        calls=[]
        geometry={'regions':[]}
        def process(n,attempt):
            calls.append(n)
            if n==2:layout_reader.parse_layout('{broken',n,geometry)
        result=process_pages([1,2,3],process,lambda n:False,progress=lambda s:None)
        self.assertEqual(calls,[1,2,3,2,2])
        self.assertEqual(result['completed_pages'],[1,3]);self.assertEqual(result['status'],'partial')

    def test_render_failure_keeps_page_mapping_and_next_translation(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);source=root/'source.pdf';doc=fitz.open()
            for n in [1,2,3]:doc.new_page().insert_text((50,60),f'Original page {n}')
            doc.save(source);doc.close()
            for n in [1,2,3]:(root/f'page-{n:04}.json').write_text('{}')
            manifest={'source_path':str(source),'source_name':source.name,'requested_pages':[1,2,3],'completed_pages':[1,2,3],'total_pages':3}
            calls=[]
            def translator(src,n,data,qa):
                calls.append(n)
                if n==2:raise ValueError('forced layout failure')
                out=fitz.open();out.insert_pdf(src,from_page=n-1,to_page=n-1)
                out[0].insert_text((50,90),'已完成',fontname='china-s');return out
            with patch.object(layout_reader,'translated_page',side_effect=translator):
                result=layout_reader.write_aligned_pdf(root,manifest,progress=lambda s:None)
            out=fitz.open(result)
            self.assertEqual(len(out),3);self.assertEqual(calls,[1,2,3])
            self.assertIn('中文待补',out[1].get_text());self.assertIn('已完成',out[2].get_text())
            self.assertEqual(json.loads((root/'layout-qa.json').read_text(encoding='utf-8'))['render_failed_pages'],{'2':'forced layout failure'})
            out.close()

    def test_native_job_partial_is_terminal_and_retains_later_pages(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);job=root/'job.json';job.write_text(json.dumps({'pdf':'source.pdf'}))
            m={'status':'partial','requested_pages':[1,2,3],'completed_pages':[1,3],'total_pages':3,'failed_pages':{'2':{'error':'JSON','attempts':3}}}
            (root/'layout-qa.json').write_text(json.dumps({'render_failed_pages':{}}))
            with patch.object(native_job,'run_layout',return_value=(root,m)),patch.object(native_job,'write_aligned_pdf',return_value=root/'output.pdf'):
                native_job.main(job)
            state=json.loads(job.with_suffix('.status.json').read_text(encoding='utf-8'))
            self.assertEqual(state['status'],'partial');self.assertTrue(state['partial'])
            self.assertEqual(state['source_pages'],[1,3]);self.assertEqual(state['requested_pages'],[1,2,3]);self.assertIn('2',state['failed_pages'])

if __name__=='__main__':unittest.main()
