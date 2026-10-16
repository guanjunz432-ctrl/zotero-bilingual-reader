"""Finish the forward pass before retrying failed pages; no false full success."""
def process_pages(pages, process, cached, progress=print, stop=None, checkpoint=None, attempts=3):
    result={'requested_pages':list(pages),'completed_pages':[],'failed_pages':{},'attempts':{},'status':'in_progress'}
    def save():
        result['completed_pages'].sort()
        if checkpoint:checkpoint(result)
    # Preserve later cached pages even if login/quota fails on an earlier page.
    result['completed_pages']=[p for p in pages if cached(p)]
    save()
    pending=list(pages)
    for round_index in range(attempts):
        for page in pending:
            if stop and stop.is_set():
                result['status']='stopped';save();return result
            if cached(page):
                if page not in result['completed_pages']:result['completed_pages'].append(page)
                result['failed_pages'].pop(str(page),None)
                progress(f'第 {page} 页：读取已有结果（不重复请求）');save();continue
            result['attempts'][str(page)]=round_index+1
            try:
                process(page,round_index+1)
                result['completed_pages'].append(page)
                result['failed_pages'].pop(str(page),None)
            except Exception as exc:
                result['failed_pages'][str(page)]={'error':str(exc),'attempts':round_index+1}
                if getattr(exc,'fatal',False):
                    result.update(status='error',service_error=str(exc))
                    progress(str(exc));save();return result
                progress(f'第 {page} 页未完成：{exc}；继续处理其他页，稍后单独补试')
            save()
        pending=[p for p in pages if p not in result['completed_pages']]
        if not pending:break
        if round_index+1<attempts:progress('后续页面已处理，开始补试失败页：'+','.join(map(str,pending)))
    result['status']='complete' if not pending else 'partial'
    save()
    return result
