// Room title card: shown for a few seconds when a scene is entered (name, years, one line).
export function createTitleCard() {
  const el = document.getElementById('title-card');
  const h = el ? el.querySelector('h2') : null;
  const years = el ? el.querySelector('.years') : null;
  const summary = el ? el.querySelector('.summary') : null;
  let timer = 0;
  let current = null;

  function show(intro, { hold = 4.5 } = {}) {
    if (!el || !intro) return;
    current = intro;
    if (h) h.textContent = intro.title || '';
    if (years) { years.textContent = intro.years || ''; years.hidden = !intro.years; }
    if (summary) { summary.textContent = intro.summary || ''; summary.hidden = !intro.summary; }
    el.hidden = false;
    // restart the CSS transition
    el.classList.remove('visible');
    void el.offsetWidth;
    el.classList.add('visible');
    timer = hold;
  }
  function hide() { if (el) el.classList.remove('visible'); timer = 0; }
  function update(dt) {
    if (timer > 0) {
      timer -= dt;
      if (timer <= 0) hide();
    }
  }
  function isVisible() { return !!el && el.classList.contains('visible'); }
  return { show, hide, update, isVisible, current: () => current };
}
