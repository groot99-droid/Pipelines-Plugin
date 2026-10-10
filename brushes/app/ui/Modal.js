/**
 * Modal.js - in-page replacement for window.prompt()/confirm()
 *
 * window.prompt()/confirm() throw ("prompt() is not supported") in several
 * embedded/automated browser contexts, and the app's only two prompt() call
 * sites were outside their surrounding try/catch -- so Save Preset threw an
 * unhandled promise rejection with zero visible feedback. Not just a bug in
 * this environment: native dialogs also block the render thread and look
 * out of place in a themed UI. This is a real component, not a workaround.
 */

const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
}[c]));

function scaffold(title) {
  const overlay = document.createElement('div');
  overlay.className = 'modal-overlay';
  const box = document.createElement('div');
  box.className = 'modal-box';
  box.innerHTML = `<h3 class="modal-title">${esc(title)}</h3>`;
  overlay.appendChild(box);
  return { overlay, box };
}

export class Modal {
  static prompt({ title = 'Enter a value', label = '', defaultValue = '', placeholder = '' } = {}) {
    return new Promise((resolve) => {
      const { overlay, box } = scaffold(title);
      box.insertAdjacentHTML('beforeend', `
        <label class="modal-label">${esc(label)}</label>
        <input type="text" class="modal-input" value="${esc(defaultValue)}" placeholder="${esc(placeholder)}">
        <div class="modal-actions">
          <button type="button" class="btn modal-cancel">Cancel</button>
          <button type="button" class="btn btn-primary modal-ok">OK</button>
        </div>
      `);

      const input = box.querySelector('.modal-input');
      const done = (value) => { overlay.remove(); resolve(value); };

      box.querySelector('.modal-cancel').addEventListener('click', () => done(null));
      box.querySelector('.modal-ok').addEventListener('click', () => done(input.value));
      input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') done(input.value);
        if (e.key === 'Escape') done(null);
      });
      overlay.addEventListener('click', (e) => { if (e.target === overlay) done(null); });

      document.body.appendChild(overlay);
      input.focus();
      input.select();
    });
  }

  static confirm({ title = 'Are you sure?', message = '', okLabel = 'Confirm', danger = false } = {}) {
    return new Promise((resolve) => {
      const { overlay, box } = scaffold(title);
      box.insertAdjacentHTML('beforeend', `
        <p class="modal-message">${esc(message)}</p>
        <div class="modal-actions">
          <button type="button" class="btn modal-cancel">Cancel</button>
          <button type="button" class="btn ${danger ? 'btn-danger' : 'btn-primary'} modal-ok">${esc(okLabel)}</button>
        </div>
      `);

      const done = (value) => { overlay.remove(); document.removeEventListener('keydown', onKey); resolve(value); };
      const onKey = (e) => { if (e.key === 'Escape') done(false); };

      box.querySelector('.modal-cancel').addEventListener('click', () => done(false));
      box.querySelector('.modal-ok').addEventListener('click', () => done(true));
      overlay.addEventListener('click', (e) => { if (e.target === overlay) done(false); });
      document.addEventListener('keydown', onKey);

      document.body.appendChild(overlay);
      box.querySelector('.modal-ok').focus();
    });
  }
}

export default Modal;
