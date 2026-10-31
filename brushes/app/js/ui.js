// ui.js - toast, confirm dialog, clipboard, download: small shared UI helpers.

import {el, clear} from './dom.js';

let toastHost = null;

export function initUi(host) {
  toastHost = host;
}

/** A transient message. kind: info | ok | warn | error. Text only. */
export function toast(message, kind = 'info', ms = 4500) {
  if (!toastHost) return;
  const node = el('div', {class: `toast toast-${kind}`, role: kind === 'error' ? 'alert' : null}, el('span', {text: message}));
  const close = el('button', {class: 'toast-x', type: 'button', 'aria-label': 'Dismiss message', text: '×',
    onclick: () => node.remove()});
  node.append(close);
  toastHost.append(node);
  if (ms > 0) setTimeout(() => node.remove(), ms);
  while (toastHost.children.length > 5) toastHost.firstChild.remove();
}

/** A modal yes/no that returns a Promise<boolean>. Built on <dialog>. */
export function confirmDialog(dialog, {title, message, yes = 'Continue', no = 'Cancel'}) {
  return new Promise((resolve) => {
    clear(dialog);
    let answer = false;
    const done = (value) => { answer = value; dialog.close(); };
    dialog.setAttribute('aria-labelledby', 'dlg-title');
    dialog.append(
      el('h2', {id: 'dlg-title', text: title}),
      el('p', {text: message}),
      el('div', {class: 'btn-row'},
        el('button', {class: 'btn', type: 'button', text: no, onclick: () => done(false)}),
        el('button', {class: 'btn btn-primary', type: 'button', text: yes, onclick: () => done(true)})));
    dialog.addEventListener('close', () => resolve(answer), {once: true});
    if (typeof dialog.showModal === 'function') dialog.showModal();
    else resolve(window.confirm(message));
  });
}

/** Copy text. Uses the async clipboard, falls back to a selection + execCommand. */
export async function copyText(text, fallbackTextarea = null) {
  try {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(text);
      return true;
    }
  } catch (_) { /* fall through */ }
  const area = fallbackTextarea || el('textarea', {readOnly: true, class: 'offscreen', 'aria-hidden': 'true'});
  if (!fallbackTextarea) { area.value = text; document.body.append(area); }
  area.focus();
  area.select();
  let ok = false;
  try { ok = document.execCommand('copy'); } catch (_) { ok = false; }
  if (!fallbackTextarea) area.remove();
  return ok;
}

/** Offer a Blob to the user as a download. */
export function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob);
  const link = el('a', {href: url, download: filename, class: 'offscreen'});
  document.body.append(link);
  link.click();
  link.remove();
  setTimeout(() => URL.revokeObjectURL(url), 30000);
}

/** View preference storage. Never tokens, never brush data. */
export const prefs = {
  get(key, fallback = null) {
    try { const v = window.localStorage.getItem(`rosw.brushes.${key}`); return v === null ? fallback : v; } catch (_) { return fallback; }
  },
  set(key, value) {
    try { window.localStorage.setItem(`rosw.brushes.${key}`, String(value)); } catch (_) { /* private mode */ }
  },
};
