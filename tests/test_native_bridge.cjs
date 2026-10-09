const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
async function scenario(status) {
  const records={},imports=[],opened=[],alerts=[];
  const source={id:101,key:'DEMO0001',libraryID:1,parentID:100,parentItem:{id:100},
    isRegularItem:()=>false,isPDFAttachment:()=>true,hasTag:()=>false,
    getFilePathAsync:async()=> 'C:\\source.pdf'};
  function Progress(){}
  Progress.prototype={changeHeadline(){},show(){},startCloseTimer(){},
    ItemProgress:function(){this.setText=()=>{};this.setProgress=()=>{};}};
  const context={Date,Error,String,console,
    Services:{env:{get:()=> 'C:\\SyntheticAppData'},prompt:{alert:(w,t,s)=>alerts.push(s)}},
    IOUtils:{exists:async()=>true,makeDirectory:async()=>{},writeJSON:async(p,v)=>{records[p]=v;},readJSON:async p=>p.endsWith('settings.json')?{root:'C:\\SyntheticBackend',python_path:'C:\\pythonw.exe'}:status},
    ChromeUtils:{importESModule:()=>({Subprocess:{call:async()=>({stdout:{readString:async()=>null},stderr:{readString:async()=>null},wait:()=>new Promise(()=>{})})}})},
    Zotero:{getMainWindow:()=>({}),ProgressWindow:Progress,Libraries:{get:()=>({editable:true})},
      Items:{get:()=>source},File:{pathToFile:p=>p},URI:{getItemURI:()=> 'zotero://test-source'},
      Attachments:{importFromFile:async opts=>{imports.push(opts);return{id:102,key:'TESTONLY',parentID:opts.parentItemID,setField(){},addTag(){},addRelation(){},saveTx:async()=>{},getFilePathAsync:async()=> 'C:\\generated.pdf'};}},
      Reader:{open:async id=>opened.push(id)},Promise:{delay:async()=>{}}}
  };
  vm.createContext(context);
  vm.runInContext(fs.readFileSync(__dirname+'/../addon/bridge.js','utf8'),context);
  const bridge=context.createCodexBilingual('test-only');
  await bridge.start([source],'',false);
  for(let i=0;i<30&&bridge.active;i++)await new Promise(setImmediate);
  assert.equal(bridge.active,null,'monitor must finish');
  return{imports,opened,alerts,records};
}
(async()=>{
  for(const state of ['error','stopped','partial']){
    const r=await scenario({status:state,message:'interrupted',pdf:'C:\\partial.pdf',partial:true,source_pages:[1,2],requested_pages:[1,2,3],total_pages:21});
    assert.equal(r.imports.length,1);assert.equal(r.imports[0].parentItemID,100);
    assert.match(r.imports[0].title,/未完成 2\/3 页/);assert.match(r.imports[0].fileBaseName,/^Codex中英对照_/);
    assert.doesNotMatch(r.imports[0].fileBaseName,/[\\/:*?"<>|]/);
    assert.equal(Object.values(r.records).find(v=>v.attachmentID)?.partial,true);
  }
  const complete=await scenario({status:'complete',message:'done',pdf:'C:\\full.pdf',source_pages:[1,2],total_pages:2});
  assert.match(complete.imports[0].title,/原版式 · 全文/);
  const empty=await scenario({status:'error',message:'login failed'});assert.equal(empty.imports.length,0);
  console.log('PASS: complete attachment, partial error/stop attachment, parent identity, filename exclusion, no fake success');
})().catch(e=>{console.error(e);process.exitCode=1;});
