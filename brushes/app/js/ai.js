// ai.js - the "AI assist" tab (group `ai`): Ask Claude, paste the reply back,
// offline suggestions, and an honest note about local models.
//
// F10 "The app": the Claude route is paste only. There is no model behind this
// page, no patch inbox on the server and no proxy to Ollama (the page may not
// make requests to anything but its own server). So:
//   1. Ask Claude   - a request is built from the open brush (ai/prompt.js)
//                     and copied; the user pastes it into a chat.
//   2. Paste back   - the reply goes to the Patch box (patchbox.js), where the
//                     server validates it and the user reviews the diff.
//   3. Suggestions  - preset nudges (ai/nudges.js) made on this page, each
//                     checked by the server and shown as a diff before Apply.
// Registered with panels.js: registerGroupPanel('ai', {mode: 'replace', render: renderAiTab}).

import {el, clear} from './dom.js';
import {api} from './api.js';
import {toast, copyText} from './ui.js';
import {shorten, dropResolution, diffRows, REJECT_TEXT, WARNING_TEXT} from './patch.js';
import {validateBody} from './patchbox.js';
import {buildRequest, extractPatch, sizeText, REQUEST_LIMIT, WISH_LIMIT} from './ai/prompt.js';
import {NUDGES, STRENGTHS, makeNudge} from './ai/nudges.js';

// what the user typed survives switching tabs (this session only; never stored)
const memory = {wish: '', reply: '', all: false, strength: 'normal'};

export const OLLAMA_NEEDS = [
  'A route in app_server.py that forwards a prompt to an Ollama running on this machine (for example POST /api/assist). The page cannot call Ollama itself.',
  'A fixed, loopback-only target and a model allow-list set when the server starts, so the page cannot point the server at another host.',
  'A size cap on the prompt and the reply, a time limit, and one request at a time.',
  'The same token check as every /api route; the token and the prompt are never logged.',
  'The page would send the request built here, and the reply would still go through the Patch box and the server’s validation. Nothing is applied without the diff.',
];

function note(kind, text) {
  return el('div', {class: `notice notice-${kind}`, role: kind === 'bad' ? 'alert' : null}, el('p', {text}));
}

/** Hand text to the Patch box of the Designer and run its check. */
async function handToPatchBox(text, ctx) {
  const box = window.__brushApp && window.__brushApp.designer && window.__brushApp.designer.patchBox;
  const area = box ? box.area : document.getElementById('patch-paste');
  if (!area) return false;
  area.value = text;
  if (ctx.focusPatchBox) ctx.focusPatchBox();
  if (box && box.check) await box.check();
  return true;
}

export function renderAiTab(container, ctx) {
  const {doc, schema} = ctx;
  const root = el('div', {class: 'mount ai-tab', id: 'ai-mount', dataset: {mount: 'ai'}});
  container.append(root);

  const settings = () => doc.effective('main');
  const requestText = () => buildRequest({
    schema, settings: settings(), patch: doc.patch('main'), era: doc.era, name: doc.value('name', 'main') || doc.name,
    libraryId: doc.libraryId, wish: wish.value, all: allBox.checked});

  // ── 1. ask Claude ──
  const wish = el('textarea', {class: 'patch-area', id: 'ai-wish', rows: 3, maxLength: WISH_LIMIT, spellcheck: true, value: memory.wish,
    placeholder: 'For example: make this softer and grainier, like charcoal', oninput: () => { memory.wish = wish.value; refreshPreview(); }});
  const allBox = el('input', {type: 'checkbox', id: 'ai-all', class: 'switch', checked: memory.all, onchange: () => { memory.all = allBox.checked; refreshPreview(); }});
  const preview = el('textarea', {class: 'patch-area mono', id: 'ai-request', rows: 10, readOnly: true, spellcheck: false, 'aria-label': 'The request to copy'});
  const sizeOut = el('p', {class: 'small muted', 'aria-live': 'polite'});
  const copyBtn = el('button', {class: 'btn btn-primary', type: 'button', text: 'Copy request', onclick: async () => {
    const text = requestText();
    preview.value = text; sizeOut.textContent = sizeText(text);
    if (text.length > REQUEST_LIMIT) toast('The request is long; some chats may cut it. Untick “every editable setting”.', 'warn');
    toast((await copyText(text, preview)) ? 'Request copied. Paste it into a chat with Claude.' : 'Copy failed: the text is selected, copy it by hand.', 'info');
  }});
  const details = el('details', {class: 'ai-request', ontoggle: (e) => { if (e.target.open) refreshPreview(); }},
    el('summary', {text: 'Show the request'}), preview, sizeOut);
  function refreshPreview() {
    if (!details.open) return;
    const text = requestText();
    preview.value = text; sizeOut.textContent = sizeText(text);
  }

  // ── 2. paste the reply back ──
  const reply = el('textarea', {class: 'patch-area mono', id: 'ai-reply', rows: 6, spellcheck: false, autocomplete: 'off', value: memory.reply,
    placeholder: 'Paste Claude’s whole reply here. The patch is found inside it.', oninput: () => { memory.reply = reply.value; judge(); }});
  const replyStatus = el('p', {class: 'small', 'aria-live': 'polite'});
  const sendBtn = el('button', {class: 'btn btn-primary', type: 'button', text: 'Check in the Patch box', disabled: true, onclick: async () => {
    const found = extractPatch(reply.value);
    if (!found.ok) return;
    const sent = await handToPatchBox(found.text, ctx);
    if (sent) toast('The patch is in the Patch box. The server checks it; review the list, then Apply.', 'info', 6000);
    else toast('The Patch box was not found on this page.', 'error');
  }});
  function judge() {
    if (!reply.value.trim()) { replyStatus.textContent = ''; replyStatus.className = 'small muted'; sendBtn.disabled = true; return; }
    const found = extractPatch(reply.value);
    sendBtn.disabled = !found.ok;
    replyStatus.className = `small ${found.ok ? 'ok-text' : 'bad-text'}`;
    replyStatus.textContent = found.ok ? `Found a patch that changes ${found.keys.length} setting${found.keys.length === 1 ? '' : 's'}${found.summary ? `: ${found.summary}` : ''}.` : found.error;
  }

  // ── 3. suggestions made here ──
  const strength = el('select', {class: 'select', id: 'ai-strength', 'aria-label': 'How strong the nudge is', onchange: () => { memory.strength = strength.value; }},
    STRENGTHS.map((s) => el('option', {value: s.id, text: s.label, selected: s.id === memory.strength})));
  const nudgeReport = el('div', {class: 'patch-report ai-nudge-report', 'aria-live': 'polite'});
  let busy = false;

  async function tryNudge(nudge) {
    if (busy) return;
    busy = true;
    clear(nudgeReport);
    nudgeReport.append(el('p', {class: 'muted', text: `Working out “${nudge.label}” and asking the server to check it…`}));
    try {
      const factor = (STRENGTHS.find((s) => s.id === strength.value) || STRENGTHS[1]).factor;
      const made = makeNudge(nudge.id, {schema, settings: settings(), era: doc.era, strength: factor});
      clear(nudgeReport);
      if (!Object.keys(made.changes).length) {
        nudgeReport.append(el('div', {class: 'notice'}, el('strong', {text: `“${made.label}” has nothing to change on this brush.`}),
          skippedList(made.skipped)));
        return;
      }
      const result = await api.validatePatch(validateBody(doc, made.changes));
      showNudge(made, result);
    } catch (error) {
      clear(nudgeReport);
      nudgeReport.append(note('bad', `${error.code || 'error'}: ${error.message || error}`));
    } finally { busy = false; }
  }

  function skippedList(skipped) {
    if (!skipped.length) return null;
    return el('details', {class: 'ai-skipped'}, el('summary', {text: `Left alone (${skipped.length})`}),
      el('ul', {}, skipped.map((s) => el('li', {}, el('code', {text: s.key}), ` ${s.reason}.`))));
  }

  function showNudge(made, result) {
    clear(nudgeReport);
    const applied = result.applied || {};
    const keys = Object.keys(applied);
    nudgeReport.append(el('p', {}, el('strong', {text: made.label}), ` — ${made.about}`),
      el('p', {class: 'small muted', text: 'A starting point from fixed rules on this page, not a prediction of how the stroke will look. Checked by the server against this brush.'}),
      el('p', {class: result.ok ? 'ok-text small' : 'bad-text small', text: `${keys.length} to apply, ${(result.rejected || []).length} rejected, ${(result.clamped || []).length} clamped, ${(result.unchanged || []).length} unchanged.`}));
    if (keys.length) {
      const rows = diffRows(schema, doc, applied);
      nudgeReport.append(el('table', {class: 'table diff'},
        el('thead', {}, el('tr', {}, ['Setting', 'Now', 'After'].map((h) => el('th', {text: h})))),
        el('tbody', {}, rows.map((r) => el('tr', {}, el('td', {}, el('strong', {text: r.label}), el('div', {class: 'small muted mono', text: r.key})), el('td', {text: r.now}), el('td', {class: 'after', text: r.after}))))));
    }
    if ((result.rejected || []).length) {
      nudgeReport.append(el('div', {class: 'notice notice-bad'}, el('strong', {text: 'Rejected by the server (not applied)'}),
        el('ul', {}, result.rejected.map((r) => el('li', {}, el('code', {text: r.key}), ` ${r.code}: ${REJECT_TEXT[r.code] || r.reason || ''}`)))));
    }
    if ((result.warnings || []).length) {
      nudgeReport.append(el('div', {class: 'notice notice-warn'}, el('strong', {text: 'Warnings'}),
        el('ul', {}, result.warnings.map((w) => el('li', {}, el('code', {text: w.key}), ` ${WARNING_TEXT[w.code] || w.code}`)))));
    }
    const left = skippedList(made.skipped);
    if (left) nudgeReport.append(left);
    if (keys.length) {
      nudgeReport.append(el('div', {class: 'btn-row'},
        el('button', {class: 'btn btn-primary', type: 'button', text: `Apply ${keys.length} change${keys.length === 1 ? '' : 's'}`, onclick: () => {
          const touched = doc.setMany(dropResolution(shorten(applied)), {label: `suggestion: ${made.label}`, layer: 'main'});
          if (doc.active !== 'main') doc.setActive('main');
          toast(`${touched.length} setting(s) changed. Undo takes the whole suggestion back.`, 'ok');
          clear(nudgeReport); nudgeReport.append(note('ok', `Applied “${made.label}”: ${touched.length} change(s). Undo (Ctrl+Z) reverts it.`));
        }}),
        el('button', {class: 'btn', type: 'button', text: 'Discard', onclick: () => clear(nudgeReport)})));
    }
  }

  const nudgeButtons = el('div', {class: 'chips nudge-buttons', role: 'group', 'aria-label': 'Suggestions'},
    NUDGES.map((n) => el('button', {class: 'chip nudge', type: 'button', title: n.about, text: n.label, dataset: {nudge: n.id}, onclick: () => tryNudge(n)})));

  // ── layout ──
  root.append(
    ctx.layer === 'sub' ? note('warn', 'You are on the secondary (dual) brush. Requests, the Patch box and suggestions all work on the primary brush; switch to “Primary brush” to see what they change.') : null,
    el('div', {class: 'card'}, el('h3', {text: 'Ask Claude'}),
      el('p', {class: 'small', text: 'This page has no model behind it. Claude works in a chat: you copy a request made from this brush, paste it there, and paste the answer back below. The server checks every value, and you see a list of what would change before anything does.'}),
      el('div', {class: 'field'}, el('label', {htmlFor: 'ai-wish', text: 'What do you want?'}), wish),
      el('label', {class: 'check', htmlFor: 'ai-all'}, allBox, el('span', {text: 'Offer every editable setting, not just the main ones (longer request)'})),
      el('div', {class: 'btn-row'}, copyBtn), details),
    el('div', {class: 'card'}, el('h3', {text: 'Paste Claude’s reply'}),
      el('p', {class: 'small muted', text: 'Paste the whole reply. The patch inside it is picked out and sent to the Patch box for the server’s check.'}),
      el('div', {class: 'field'}, el('label', {htmlFor: 'ai-reply', text: 'Claude’s reply'}), reply), replyStatus,
      el('div', {class: 'btn-row'}, sendBtn, el('button', {class: 'btn', type: 'button', text: 'Go to the Patch box', onclick: () => ctx.focusPatchBox && ctx.focusPatchBox()}),
        el('button', {class: 'btn btn-quiet', type: 'button', text: 'Clear', onclick: () => { reply.value = ''; memory.reply = ''; judge(); }}))),
    el('div', {class: 'card'}, el('h3', {text: 'Quick suggestions (no model)'}),
      el('p', {class: 'small muted', text: 'Fixed nudges to settings this brush holds: pick one, read the list, apply or discard. Nothing is learned and nothing leaves this page except the check against the server.'}),
      el('div', {class: 'field'}, el('label', {htmlFor: 'ai-strength', text: 'Strength'}), strength), nudgeButtons, nudgeReport),
    el('div', {class: 'card'}, el('h3', {text: 'Local models (Ollama)'}),
      el('p', {text: 'Ollama is not available from this page.'}),
      el('p', {class: 'small muted', text: 'The old designer could call a local Ollama directly. This page may only talk to its own server, and the server has no route that forwards to Ollama, so there is no button for it.'}),
      el('details', {class: 'ai-request'}, el('summary', {text: 'What a future server proxy would need'}), el('ul', {}, OLLAMA_NEEDS.map((t) => el('li', {text: t}))))));
  judge();
  return {root, requestText};
}
