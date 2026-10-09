var bridge;
async function startup({id,rootURI}) {
  await Zotero.uiReadyPromise;
  Services.scriptloader.loadSubScript(rootURI+'bridge.js');
  bridge = createCodexBilingual(id);
  Zotero.ZoteroBilingualReader = bridge;
  bridge.register();
}
function shutdown() { bridge?.shutdown(); delete Zotero.ZoteroBilingualReader; }
function install() {}
function uninstall() {}
