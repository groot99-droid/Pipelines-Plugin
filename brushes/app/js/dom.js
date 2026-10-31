// dom.js - the only way this app builds DOM.
//
// The page's CSP (F10) forbids inline scripts and inline style attributes, and
// this app never writes HTML strings: every node is built here and every text
// goes in by textContent. `style` is never set through an attribute either;
// code that needs a dynamic size sets a CSS custom property through
// node.style.setProperty(), which the CSP allows.

const ATTRIBUTE_ONLY = /^(aria-|data-|role$|list$|form$)/;

/** el('button', {class: 'btn', onclick: fn, text: 'Go'}, child, 'text', ...) */
export function el(tag, props, ...children) {
  const node = document.createElement(tag);
  let deferredValue;
  if (props) {
    for (const [key, value] of Object.entries(props)) {
      if (value === undefined || value === null || value === false) continue;
      if (key === 'class') node.className = value;
      else if (key === 'text') node.textContent = value;
      else if (key === 'value') deferredValue = value;           // after min/max/step on a range input
      else if (key === 'dataset') Object.assign(node.dataset, value);
      else if (key.startsWith('on') && typeof value === 'function') node.addEventListener(key.slice(2).toLowerCase(), value);
      else if (ATTRIBUTE_ONLY.test(key)) node.setAttribute(key, value === true ? '' : String(value));
      else if (key in node) node[key] = value;
      else node.setAttribute(key, value === true ? '' : String(value));
    }
  }
  append(node, children);
  if (deferredValue !== undefined) node.value = deferredValue;
  return node;
}

export function append(node, children) {
  for (const child of children.flat(Infinity)) {
    if (child === undefined || child === null || child === false) continue;
    node.append(child instanceof Node ? child : document.createTextNode(String(child)));
  }
  return node;
}

export function clear(node) {
  while (node.firstChild) node.removeChild(node.firstChild);
  return node;
}

let counter = 0;
export function uid(prefix = 'id') {
  counter += 1;
  return `${prefix}-${counter}`;
}

/** A visually-labelled field: <label for=id>text</label> + control. */
export function field(labelText, control, extraClass = '') {
  const id = control.id || (control.id = uid('f'));
  return el('div', {class: `field ${extraClass}`.trim()}, el('label', {htmlFor: id, text: labelText}), control);
}

/** True when a keyboard event comes from something the user types into. */
export function isTyping(event) {
  const t = event.target;
  if (!(t instanceof HTMLElement)) return false;
  if (t.isContentEditable) return true;
  const tag = t.tagName;
  if (tag === 'TEXTAREA' || tag === 'SELECT') return true;
  if (tag === 'INPUT') {
    const type = (t.getAttribute('type') || 'text').toLowerCase();
    return !['checkbox', 'radio', 'range', 'button', 'file'].includes(type);
  }
  return false;
}
