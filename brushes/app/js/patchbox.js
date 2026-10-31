// patchbox.js - the "Claude route" (F10 "The app"): Claude proposes a settings
// patch, the user pastes it here. There is no patch inbox on the server.
//
// Paste -> POST /api/validate-patch against the OPENED brush's original (a
// library id, or the Brush.archive member of an opened file) -> the report
// (applied / clamped / rejected / unchanged / warnings, and the base kind) with
// a before/after diff -> Apply, one undo step. Python's answer wins; this
// panel never applies a key the server did not accept.
//
// "Copy my patch" puts the current edits on the clipboard as the same compact
// envelope (F3 "Patches"), for pasting back to Claude.

import {el, clear} from './dom.js';
import {api} from './api.js';
import {parseEnvelope, envelopeText, shorten, dropResolution, diffRows, REJECT_TEXT, WARNING_TEXT} from './patch.js';
import {toast, copyText} from './ui.js';

/** The body of POST /api/validate-patch for a doc. */
export function validateBody(doc, changes) {
  if (doc.origin.kind === 'library' && doc.libraryId) return {changes, base_id: doc.libraryId};
  const members = (doc.base && doc.base.members) || [];
  const archive = members.find((m) => m.path === 'Brush.archive');
  if (archive) return {changes, base: {members: [archive]}};
  return {changes, era: doc.era};
}

export function createPatchBox({schema, getDoc}) {
  const area = el('textarea', {class: 'patch-area mono', id: 'patch-paste', rows: 6, spellcheck: false, autocomplete: 'off',
    placeholder: '{"schema": "rosw-brushes-patch/1", "base_id": null, "summary": "...", "changes": {"plotSpacing": 0.2}}'});
  const report = el('div', {class: 'patch-report', 'aria-live': 'polite'});
  const mine = el('textarea', {class: 'patch-area mono', id: 'patch-mine', rows: 3, readOnly: true, spellcheck: false, 'aria-label': 'Your current patch'});
  let pending = null;                       // {applied, summary} of the last good check
  let unsubscribe = null;

  const checkBtn = el('button', {class: 'btn btn-primary', type: 'button', text: 'Check patch', onclick: () => check()});

  async function check() {
    const doc = getDoc();
    clear(report); pending = null;
    if (!doc) { report.append(note('bad', 'Open a brush first.')); return; }
    const parsed = parseEnvelope(area.value);
    if (!parsed.ok) { report.append(note('bad', parsed.error)); return; }
    const {envelope} = parsed;
    checkBtn.disabled = true;
    report.append(el('p', {class: 'muted', text: 'Checking with the server…'}));
    let result;
    try {
      result = await api.validatePatch(validateBody(doc, envelope.changes));
    } catch (error) {
      clear(report); report.append(note('bad', `${error.code}: ${error.message}`, error.hint)); checkBtn.disabled = false; return;
    }
    checkBtn.disabled = false;
    show(doc, envelope, result);
  }

  function show(doc, envelope, result) {
    clear(report);
    const applied = result.applied || {};
    const keys = Object.keys(applied);
    if (envelope.base_id && doc.libraryId && envelope.base_id !== doc.libraryId) {
      report.append(note('warn', `This patch was written for brush ${envelope.base_id}; the open brush is ${doc.libraryId}. Check the diff before applying.`));
    }
    if (envelope.summary) report.append(el('p', {class: 'small', text: `Summary: ${envelope.summary}`}));
    const base = result.base || {};
    report.append(el('p', {class: 'small muted', text: `Checked against: ${base.kind || '?'}${base.era ? ` (${base.era})` : ''}.${base.note ? ' ' + base.note : ''}`}),
      el('p', {class: result.ok ? 'ok-text' : 'bad-text', text: `${keys.length} to apply, ${(result.rejected || []).length} rejected, ${(result.unchanged || []).length} unchanged, ${(result.clamped || []).length} clamped.`}));
    if (keys.length) {
      const rows = diffRows(schema, doc, applied);
      report.append(el('table', {class: 'table diff'},
        el('thead', {}, el('tr', {}, ['Setting', 'Opened', 'Now', 'After patch'].map((h) => el('th', {text: h})))),
        el('tbody', {}, rows.map((r) => el('tr', {}, el('td', {}, el('strong', {text: r.label}), el('div', {class: 'small muted mono', text: r.key})),
          el('td', {text: r.isNew ? '(not set)' : r.original}), el('td', {text: r.now}), el('td', {class: 'after', text: r.after}))))));
    }
    if ((result.rejected || []).length) {
      report.append(el('div', {class: 'notice notice-bad'}, el('strong', {text: 'Rejected (not applied)'}),
        el('ul', {}, result.rejected.map((r) => el('li', {}, el('code', {text: r.key}), ` ${r.code}: ${REJECT_TEXT[r.code] || r.reason || ''}`)))));
    }
    if ((result.clamped || []).length) {
      report.append(el('div', {class: 'notice notice-warn'}, el('strong', {text: 'Clamped'}),
        el('ul', {}, result.clamped.map((c) => el('li', {text: `${c.key}: ${c.from} became ${c.to} (${c.min} to ${c.max})`})))));
    }
    if ((result.unchanged || []).length) report.append(el('p', {class: 'small muted', text: `Already the value in the brush: ${result.unchanged.join(', ')}.`}));
    if ((result.warnings || []).length) {
      report.append(el('div', {class: 'notice notice-warn'}, el('strong', {text: 'Warnings'}),
        el('ul', {}, result.warnings.map((w) => el('li', {}, el('code', {text: w.key}), ` ${WARNING_TEXT[w.code] || w.code}`)))));
    }
    if (keys.length) {
      pending = {applied, summary: envelope.summary};
      report.append(el('div', {class: 'btn-row'},
        el('button', {class: 'btn btn-primary', type: 'button', text: `Apply ${keys.length} change${keys.length === 1 ? '' : 's'}`, onclick: () => apply()}),
        el('button', {class: 'btn', type: 'button', text: 'Discard', onclick: () => { pending = null; clear(report); }})));
    }
  }

  function apply() {
    const doc = getDoc();
    if (!doc || !pending) return;
    const touched = doc.setMany(dropResolution(shorten(pending.applied)), {label: `patch${pending.summary ? `: ${pending.summary.slice(0, 40)}` : ''}`, layer: 'main'});
    doc.setActive('main');
    toast(`${touched.length} setting(s) changed. Undo takes the whole patch back.`, 'ok');
    pending = null; clear(report);
    report.append(note('ok', `Applied ${touched.length} change(s).`));
    area.value = '';
  }

  function refreshMine() {
    const doc = getDoc();
    const changes = doc ? doc.patch('main') : {};
    mine.value = Object.keys(changes).length ? envelopeText({baseId: doc.libraryId || null, changes}) : '';
  }

  function note(kind, text, hint) {
    return el('div', {class: `notice notice-${kind === 'bad' ? 'bad' : kind === 'warn' ? 'warn' : 'ok'}`, role: kind === 'bad' ? 'alert' : null},
      el('p', {text}), hint ? el('p', {class: 'small', text: hint}) : null);
  }

  const root = el('div', {class: 'patchbox'},
    el('div', {class: 'card'}, el('h3', {text: 'Paste a patch'}),
      el('p', {class: 'small muted', text: 'Ask Claude for a patch, paste its JSON here, then check it. Nothing changes until you press Apply.'}),
      el('label', {htmlFor: 'patch-paste', class: 'sr-only', text: 'Patch JSON'}), area,
      el('div', {class: 'btn-row'}, checkBtn, el('button', {class: 'btn btn-quiet', type: 'button', text: 'Clear', onclick: () => { area.value = ''; pending = null; clear(report); }})),
      report),
    el('div', {class: 'card'}, el('h3', {text: 'Your patch'}),
      el('p', {class: 'small muted', text: 'The settings you changed, as one line Claude can read.'}),
      el('label', {htmlFor: 'patch-mine', class: 'sr-only', text: 'Your current patch'}), mine,
      el('div', {class: 'btn-row'}, el('button', {class: 'btn', type: 'button', text: 'Copy my patch', onclick: async () => {
        refreshMine();
        if (!mine.value) { toast('No settings changed yet.', 'warn'); return; }
        toast((await copyText(mine.value, mine)) ? 'Patch copied.' : 'Copy failed: the text is selected, copy it by hand.', 'info');
      }}))));

  return {
    el: root, check, area,
    setDoc(doc) {
      if (unsubscribe) unsubscribe();
      pending = null; clear(report); refreshMine();
      if (doc) unsubscribe = doc.subscribe(refreshMine);
    },
    focus() { area.focus(); },
  };
}
