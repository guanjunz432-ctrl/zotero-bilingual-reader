"""Zotero job: cloud translation, per-page recovery and source-position PDF layout."""
import argparse,json,subprocess,sys
from pathlib import Path

def startup_error(jobfile, message):
    path=Path(jobfile).with_suffix('.status.json')
    tmp=path.with_suffix('.json.tmp')
    tmp.write_text(json.dumps({'status':'error','message':message},ensure_ascii=False),encoding='utf-8')
    tmp.replace(path)

# stdlib-only bootstrap; works with the old, already-loaded Zotero bridge.
if __name__=='__main__':
    runtime=Path(__file__).resolve().parents[1]/'.venv/Scripts/python.exe'
    try:
        if not runtime.exists():
            raise RuntimeError('插件独立运行环境缺失，请运行 setup.ps1。')
        if Path(sys.executable).resolve()!=runtime.resolve():
            result=subprocess.run([str(runtime),str(Path(__file__).resolve()),*sys.argv[1:]],
                                  creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
            if result.returncode and len(sys.argv)>1:
                startup_error(sys.argv[1],f'独立翻译后台启动失败（{result.returncode}）；请运行 setup.ps1。')
            sys.exit(result.returncode)
    except Exception as exc:
        if len(sys.argv)>1:startup_error(sys.argv[1],str(exc))
        sys.exit(1)

try:
    import pymupdf,reportlab,PIL
except ImportError as exc:
    if __name__=='__main__' and len(sys.argv)>1:
        startup_error(sys.argv[1],f'插件运行依赖缺失：{exc.name}；请运行 setup.ps1。')
        sys.exit(1)
    raise
from bilingual_reader import save_json,output_folder
from layout_reader import run_layout,write_aligned_pdf

def main(jobfile):
    path=Path(jobfile);job=json.loads(path.read_text(encoding='utf-8-sig'))
    status=path.with_suffix('.status.json')
    def update(message,state='running',**extra):
        save_json(status,dict(status=state,message=message,**extra))
    class Stop:
        def is_set(self):return path.with_suffix('.stop').exists()
    def export(folder,manifest,state=None,message=None):
        update('正在按原版式排版，完成后自动添加至原文献')
        pdf=write_aligned_pdf(folder,manifest,progress=update)
        qa=json.loads((folder/'layout-qa.json').read_text(encoding='utf-8'))
        render_failed=qa.get('render_failed_pages',{})
        completed=[n for n in manifest.get('completed_pages',[]) if str(n) not in render_failed]
        failed=dict(manifest.get('failed_pages',{}))
        failed.update({n:{'error':err,'stage':'layout'} for n,err in render_failed.items()})
        state=state or manifest['status']
        if render_failed and state=='complete':state='partial'
        partial=state!='complete'
        if message is None:
            if state=='complete':message='原版式中英对照已完成'
            elif state=='stopped':message='已停止；再次选择相同文献可接着运行。'
            elif manifest.get('service_error'):message=manifest['service_error']
            else:message='后续页已继续处理；待补页：'+', '.join(sorted(failed,key=int))+'。再次生成可补试。'
        update(message,state,pdf=str(pdf),layout='source-matched',partial=partial,
               source_pages=completed,requested_pages=manifest['requested_pages'],
               total_pages=manifest['total_pages'],failed_pages=failed)
    try:
        update('正在读取所选文献')
        folder,manifest=run_layout(job['pdf'],job.get('pages',''),update,Stop())
        export(folder,manifest)
    except Exception as exc:
        folder=output_folder(job['pdf'])/'layout'
        try:
            manifest=json.loads((folder/'manifest.json').read_text(encoding='utf-8'))
            if not manifest.get('completed_pages'):raise ValueError('尚无完成页面')
            export(folder,manifest,state='error',message=str(exc)+'；已有结果已保留，未翻译页标注为“中文待补”。')
        except Exception as export_error:
            update(str(exc)+'；结果导出未完成：'+str(export_error),'error')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('job');main(p.parse_args().job)
