// library/basket.js - the set basket as seen from the Library tab: the brushes
// added with "Add to set", a name, and "Export .brushset". The basket itself
// (exporter.js createBasket) is shared with the Designer's export section.

import {el, clear} from '../dom.js';
import {exportBasket, renderExportResult} from '../exporter.js';
import {prefs} from '../ui.js';

export function createBasketView({basket, toast}) {
  const dialog = el('dialog', {class: 'drawer basket-dialog', 'aria-labelledby': 'basket-title'});
  const list = el('div', {class: 'basket'});
  const result = el('div', {class: 'export-result', 'aria-live': 'polite'});
  const name = el('input', {type: 'text', class: 'text', id: 'lib-set-name', maxLength: 120, value: prefs.get('set.name', 'My brush set'), 'aria-label': 'Set name'});
  const exportBtn = el('button', {class: 'btn btn-primary', type: 'button', text: 'Export .brushset', onclick: () => run()});
  const button = el('button', {class: 'btn', type: 'button', 'aria-haspopup': 'dialog', onclick: () => open()});
  let busy = false;

  dialog.addEventListener('click', (e) => { if (e.target === dialog) dialog.close(); });
  dialog.append(el('div', {class: 'drawer-frame'},
    el('div', {class: 'drawer-head'}, el('h2', {id: 'basket-title', class: 'drawer-title', text: 'Set basket'}),
      el('button', {class: 'btn btn-small', type: 'button', text: 'Close', onclick: () => dialog.close()})),
    el('p', {class: 'small muted', text: 'Brushes you add here go into one .brushset. They are exported exactly as they are in the library; to edit one first, open it in the Designer and add its edited copy from the Export section there.'}),
    el('div', {class: 'field'}, el('label', {htmlFor: 'lib-set-name', text: 'Set name'}), name),
    list, el('div', {class: 'btn-row'}, exportBtn, el('button', {class: 'btn btn-quiet', type: 'button', text: 'Empty the set', onclick: () => basket.clear()})),
    result));

  function render() {
    clear(list);
    const n = basket.items.length;
    button.textContent = `Set basket: ${n}`;
    button.setAttribute('aria-label', `Set basket, ${n} brush${n === 1 ? '' : 'es'}`);
    exportBtn.disabled = busy || !n;
    if (!n) { list.append(el('p', {class: 'muted small', text: 'The set is empty. Use “Add to set” on a brush.'})); return; }
    list.append(el('ol', {class: 'basket-list'}, basket.items.map((item) => el('li', {}, el('span', {text: item.label}),
      el('button', {class: 'btn btn-small btn-quiet', type: 'button', text: 'Remove', 'aria-label': `Remove ${item.label} from the set`, onclick: () => basket.remove(item.key)})))));
  }

  async function run() {
    const setName = name.value.trim();
    if (!setName) { toast('Give the set a name.', 'warn'); name.focus(); return; }
    if (!basket.items.length || busy) return;
    prefs.set('set.name', setName);
    busy = true; exportBtn.disabled = true;
    clear(result); result.append(el('p', {class: 'muted', text: 'Building the .brushset…'}));
    try {
      const done = await exportBasket({basket, name: setName});
      renderExportResult(result, done, {edited: basket.items.some((i) => i.kind === 'edited'), what: 'brushset'});
    } catch (error) {
      clear(result);
      result.append(el('div', {class: 'notice notice-bad', role: 'alert'}, el('strong', {text: `Export refused: ${error.code || 'error'}`}), el('p', {text: error.message || String(error)}),
        error.hint ? el('p', {class: 'small', text: error.hint}) : null));
    } finally { busy = false; render(); }
  }

  function open() {
    render();
    if (typeof dialog.showModal === 'function') dialog.showModal(); else dialog.setAttribute('open', '');
  }

  const unsubscribe = basket.subscribe(render);
  render();
  return {el: dialog, button, open, run, destroy() { unsubscribe(); }};
}
