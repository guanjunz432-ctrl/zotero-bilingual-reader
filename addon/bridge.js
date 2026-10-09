function createCodexBilingual(pluginID) {
  const dataRoot=Services.env.get('LOCALAPPDATA')+'\\ZoteroBilingualReader';
  const ids=[];
  let active=null;
  let lastMessage='';
  function alert(text) { Services.prompt.alert(Zotero.getMainWindow(),'Codex 中英对照',String(text)); }
  function notify(text, finished=false) {
    if (!active) return;
    if (!active.progress) {
      active.progress=new Zotero.ProgressWindow({closeOnClick:true});
      active.progress.changeHeadline('Codex 中英对照');
      active.line=new active.progress.ItemProgress('chrome://zotero/skin/treeitem-attachment-pdf.png',text);
      active.progress.show();
    }
    active.line.setText(text);
    if (finished) {active.line.setProgress(100);active.progress.startCloseTimer(12000);}
  }
  async function selectedPDF(items) {
    if(items.length!==1)throw Error('请先选中一篇文献，或选中它下面的英文 PDF 附件。');
    let item=items[0];
    if(item.isRegularItem()) {
      const candidates=Zotero.Items.get(item.getAttachments()).filter(a=>a.isPDFAttachment()&&!a.hasTag('codex-bilingual-generated'));
      const best=await item.getBestAttachment();
      item=candidates.find(a=>a.id===best?.id)||candidates[0];
    }
    if(!item?.isPDFAttachment())throw Error('所选条目没有 PDF 附件。请先为文献添加或下载英文 PDF。');
    if(item.hasTag('codex-bilingual-generated'))throw Error('这是已生成的双语版。请选择原始英文 PDF 或上级文献。');
    if(!Zotero.Libraries.get(item.libraryID).editable)throw Error('当前文库只读，无法添加双语附件。');
    const path=await item.getFilePathAsync();
    if(!path||!await IOUtils.exists(path))throw Error('原 PDF 不在本机。请先在 Zotero 中打开附件完成下载，再重试。');
    return {item,path};
  }
  async function start(items, pages, interactive=true) {
    if(active) {alert('已有任务正在进行：'+(active.message||'准备中')+'\n右键 → Codex 中英对照 → 查看进度，或在当前页后停止。');return;}
    try {
      const {item,path}=await selectedPDF(items);
      if(interactive) {
        const value={value:''};
        if(!Services.prompt.prompt(Zotero.getMainWindow(),'生成原版式中英对照',
          '文献：'+(item.parentItem?.getField('title')||item.getField('title'))+'\n\n页码留空＝全文；也可输入 1-2 或 1,3-5。\n所选页面的文字与图像将发送到 OpenAI，使用你登录的账户额度。AI 译文及图中文字定位需要核对。\n完成后双语 PDF 自动添加到原文献，并在 Zotero 中打开。',value,null,{})) return;
        pages=value.value.trim();
      }
      pages=(pages||'').trim();
      if(pages&&!/^\d+(?:-\d+)?(?:\s*,\s*\d+(?:-\d+)?)*$/.test(pages))throw Error('页码格式应为 1-2 或 1,3-5；留空为全文。');
      const settingsPath=dataRoot+'\\settings.json';
      if(!await IOUtils.exists(settingsPath))throw Error('后端尚未安装。请按 README 运行 setup.ps1，然后运行 login.ps1 登录。');
      const settings=await IOUtils.readJSON(settingsPath);
      if(!settings.root||!settings.python_path)throw Error('后端配置不完整，请重新运行 setup.ps1。');
      const root=settings.root,python=settings.python_path;
      if(!await IOUtils.exists(python)||!await IOUtils.exists(root+'\\backend\\native_job.py'))throw Error('后端文件已移动或未安装，请重新运行 setup.ps1。');
      await IOUtils.makeDirectory(dataRoot+'\\jobs',{ignoreExisting:true});
      const jobPath=dataRoot+'\\jobs\\'+Date.now()+'-'+item.key+'.json';
      const job={pdf:path,pages,sourceItemID:item.id,sourceKey:item.key,parentItemID:item.parentID||null,libraryID:item.libraryID,created:new Date().toISOString()};
      await IOUtils.writeJSON(jobPath,job);
      active={jobPath,item,job,message:'正在启动云端翻译',started:Date.now()};
      notify(active.message);
      const {Subprocess}=ChromeUtils.importESModule('resource://gre/modules/Subprocess.sys.mjs');
      active.process=await Subprocess.call({command:python,arguments:[root+'\\backend\\native_job.py',jobPath],environmentAppend:true,stderr:'pipe'});
      const current=active;
      // Drain both pipes to prevent a subprocess deadlock; no conversation or account data is logged.
      const drain=async pipe=>{try{while(await pipe.readString()) {}}catch(e){}};
      drain(current.process.stdout);drain(current.process.stderr);
      current.done=current.process.wait().then(x=>{current.exit=x;});
      current.completion=monitor(current);
      return {jobPath,sourceItemID:item.id};
    } catch(e) { if(active)notify('未完成：'+e.message,true); active=null;alert(e.message);return {error:e.message}; }
  }
  async function attach(current,status) {
    const source=Zotero.Items.get(current.item.id);
    if(!source||source.deleted)throw Error('原文献已删除；译文已保存在 '+status.pdf);
    const parent=source.parentItem;
    if(parent?.deleted)throw Error('上级文献已删除；译文已保存在 '+status.pdf);
    const label=status.partial?'未完成 '+status.source_pages.length+'/'+(status.requested_pages?.length||status.total_pages)+' 页':(status.source_pages.length===status.total_pages?'全文':'原文第 '+current.job.pages+' 页');
    const title='中英对照 · 原版式 · '+label+'（Codex，含图中文字）';
    const opts={file:Zotero.File.pathToFile(status.pdf),libraryID:source.libraryID,
      title,fileBaseName:'Codex中英对照_'+source.key+'_原版式_'+label.replace(/[\\/:*?"<>|]/g,'_')};
    if(parent)opts.parentItemID=parent.id;else opts.collections=source.getCollections();
    const result=await Zotero.Attachments.importFromFile(opts);
    result.setField('title',title);
    result.addTag('codex-bilingual-generated');
    result.addRelation('http://purl.org/dc/terms/isVersionOf',Zotero.URI.getItemURI(source));
    await result.saveTx();
    await IOUtils.writeJSON(current.jobPath.replace(/\.json$/,'.attached.json'),{
      attachmentID:result.id,attachmentKey:result.key,parentItemID:result.parentID||null,
      sourceItemID:source.id,pdf:await result.getFilePathAsync(),pages:status.source_pages,
      sourcePages:status.total_pages,partial:!!status.partial,completed:new Date().toISOString()});
    await Zotero.Reader.open(result.id);
    return result;
  }
  async function monitor(current) {
    let last=null;
    try {
      while(active===current) {
        const statusPath=current.jobPath.replace(/\.json$/,'.status.json');
        if(await IOUtils.exists(statusPath)) {
          const s=await IOUtils.readJSON(statusPath);last=s;
          if(current.message!==s.message){current.message=s.message;notify(s.message);}
          if(s.status==='complete') {
            await attach(current,s);lastMessage='完成：双语 PDF 已添加到原文献，并在 Zotero 中打开。';notify(lastMessage,true);active=null;return;
          }
          if(['error','stopped','partial'].includes(s.status)) {
            if(s.pdf&&s.partial)await attach(current,s);
            lastMessage=s.message;
            notify(s.message,true);active=null;
            if(['error','partial'].includes(s.status))alert('翻译尚未完成：'+s.message+'\n已完成页面保留；再次选择相同文献和页码可继续。');
            return;
          }
        }
        if(current.exit)throw Error('后台程序意外退出（'+current.exit.exitCode+'）。已有译文保留；可重试。');
        await Zotero.Promise.delay(1500);
      }
    } catch(e) {notify('未完成：'+e.message,true);active=null;alert(e.message);}
  }
  const action=(label,command,enabled)=>({menuType:'menuitem',onShowing:(e,c)=>{
    c.menuElem.label=label;c.setEnabled(enabled?enabled(c):true);
  },onCommand:command});
  return {
    start,
    get active(){return active?{jobPath:active.jobPath,message:active.message,sourceItemID:active.item.id}:null;},
    register() {
      ids.push(Zotero.MenuManager.registerMenu({menuID:'zotero-bilingual-reader',pluginID,target:'main/library/item',menus:[{
        menuType:'submenu',onShowing:(e,c)=>{c.menuElem.label='Codex 中英对照';c.setVisible(true);},menus:[
          action('生成原版式中英对照（含图中文字）…',(e,c)=>start(c.items||Zotero.getActiveZoteroPane().getSelectedItems(),null,true),c=>(c.items||[]).length===1&&!active),
          action('查看翻译进度',()=>alert(active?active.message:(lastMessage||'目前没有正在运行的翻译。完成的双语版在原文献的附件中。'))),
          action('当前页完成后停止',async()=>{if(active){await IOUtils.writeUTF8(active.jobPath.replace(/\.json$/,'.stop'),'stop');alert('将在当前页完成后停止。已完成页面保留，重新生成可继续。');}},()=>!!active)
        ]
      }]}));
    },
    shutdown() {
      for(const id of ids)Zotero.MenuManager.unregisterMenu(id);
      if(active) {IOUtils.writeUTF8(active.jobPath.replace(/\.json$/,'.stop'),'stop').catch(()=>{});active.progress?.close();}
      active=null;
    }
  };
}
