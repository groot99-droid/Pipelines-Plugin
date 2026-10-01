/* The hub page. Reads the JSON routes serve.py exposes and renders them.
   Nothing here writes a file; the one POST creates a run through the bookkeeper.
   Every colour, size and font comes from tokens.json through /api/tokens, set
   as CSS custom properties on :root before anything is drawn. */
(function () {
  "use strict";

  const $ = (id) => document.getElementById(id);
  const esc = (text) => String(text ?? "").replace(/[&<>"']/g, (c) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  })[c]);

  // ── tokens -> CSS custom properties ──────────────────────────────────
  // A token path a.b.c becomes --a-b-c. A value that references another token
  // as {a.b.c} is rewritten to var(--a-b-c). Prose values, which carry a dash
  // or an angle bracket, are not CSS and are left out.
  function flattenTokens(tokens) {
    const flat = {};
    const walk = (value, path) => {
      if (value && typeof value === "object" && !Array.isArray(value)) {
        for (const [key, inner] of Object.entries(value)) walk(inner, path.concat(key));
        return;
      }
      if (typeof value === "number") value = String(value);
      if (typeof value !== "string") return;
      if (/[—<>]/.test(value)) return;
      const css = value.replace(/\{([a-z0-9_.]+)\}/gi, (_, ref) => `var(--${ref.replace(/[._]/g, "-")})`);
      flat["--" + path.join("-").replace(/[._]/g, "-")] = css;
    };
    walk(tokens, []);
    return flat;
  }

  function applyTokens(tokens) {
    const root = document.documentElement.style;
    for (const [name, value] of Object.entries(flattenTokens(tokens))) root.setProperty(name, value);
  }

  // ── fetch ────────────────────────────────────────────────────────────
  async function getJSON(url, options) {
    const response = await fetch(url, options);
    const data = await response.json().catch(() => ({ error: `HTTP ${response.status}` }));
    if (!response.ok) throw new Error(data.error || `HTTP ${response.status}`);
    return data;
  }

  // ── tabs ─────────────────────────────────────────────────────────────
  function showTab(name) {
    for (const view of document.querySelectorAll(".view")) view.hidden = view.dataset.view !== name;
    for (const tab of document.querySelectorAll(".tab")) {
      const on = tab.dataset.tab === name;
      tab.classList.toggle("on", on);
      tab.setAttribute("aria-selected", on ? "true" : "false");
    }
    try { localStorage.setItem("hub:tab", name); } catch (_) { /* private mode */ }
    if (name === "brushes") mountBrushes();
    if (name === "writing") probeMuseum();
  }

  // ── notes ────────────────────────────────────────────────────────────
  let notes = [];

  function fillSelect(select, values) {
    const keep = select.value;
    while (select.options.length > 1) select.remove(1);
    for (const value of values) {
      const option = document.createElement("option");
      option.value = value; option.textContent = value;
      select.append(option);
    }
    select.value = values.includes(keep) ? keep : "";
  }

  function renderNotes() {
    const kind = $("noteKind").value, status = $("noteStatus").value, project = $("noteProject").value;
    const shown = notes.filter((n) => (!kind || n.kind === kind) && (!status || n.status === status)
      && (!project || n.project === project));
    shown.sort((a, b) => (b.status === "blocked") - (a.status === "blocked") || (b.updated > a.updated ? 1 : -1));
    $("noteGrid").innerHTML = shown.map((n) => `
      <article class="card s-${esc(n.status)}">
        <header><h3>${esc(n.title)}</h3><span class="pill">${esc(n.kind)}</span><span class="pill state">${esc(n.status)}</span></header>
        <p class="meta">${esc(n.path)}${n.project ? " · " + esc(n.project) : ""} · updated ${esc(n.updated)}</p>
        <p>${esc(n.overview) || "<em>no overview</em>"}</p>
        ${n.first_step ? `<p class="step">${n.status === "blocked" ? "blocked: " : "next: "}${esc(n.first_step)}${n.next_steps_open > 1 ? ` (+${n.next_steps_open - 1})` : ""}</p>` : ""}
        ${n.context_brand.length ? `<p class="meta">gates: ${n.context_brand.map(esc).join(", ")}</p>` : ""}
      </article>`).join("");
    const empty = $("noteEmpty");
    empty.hidden = shown.length > 0;
    empty.textContent = notes.length ? "No note matches this filter." : "The vault has no notes yet. A run's record stage writes the first one.";
  }

  async function loadNotes() {
    notes = await getJSON("/api/notes");
    const distinct = (key) => [...new Set(notes.map((n) => n[key]).filter(Boolean))].sort();
    fillSelect($("noteKind"), distinct("kind"));
    fillSelect($("noteStatus"), distinct("status"));
    fillSelect($("noteProject"), distinct("project"));
    renderNotes();
  }

  let searchTimer = null;
  async function searchNotes() {
    const q = $("noteSearch").value.trim();
    const hits = $("noteHits");
    if (!q) { hits.hidden = true; hits.innerHTML = ""; return; }
    try {
      const found = await getJSON(`/api/search?q=${encodeURIComponent(q)}&top=8`);
      hits.hidden = false;
      hits.innerHTML = found.length
        ? found.map((h) => `<div class="hit"><span class="score">${h.score.toFixed(2)}</span> <strong>${esc(h.title)}</strong> · ${esc(h.heading)}<br><span class="meta">${esc(h.path)}</span><br>${esc(h.preview)}</div>`).join("")
        : `<div class="hit">no match</div>`;
    } catch (problem) {
      hits.hidden = false;
      hits.innerHTML = `<div class="hit">${esc(problem.message)}. Build it: <code>python studio/vault/tools/vault_index.py index</code></div>`;
    }
  }

  // ── runs ─────────────────────────────────────────────────────────────
  async function loadRuns() {
    const runs = await getJSON("/api/runs");
    const body = $("runTable").querySelector("tbody");
    body.innerHTML = runs.map((r) => r.status === "broken"
      ? `<tr class="s-blocked"><td>broken</td><td>-</td><td>-</td><td>${esc(r.run_id)}</td><td colspan="2">${esc(r.problem)}</td></tr>`
      : `<tr class="s-${esc(r.status)}"><td>${esc(r.status)}${r.parked ? `<br><span class="meta">on ${esc(r.parked.constraint)}: ${esc(r.parked.needs)}</span>` : ""}</td>
         <td>${esc(r.next_stage || "done")}</td><td>${esc(r.pipeline)}</td><td>${esc(r.run_id)}<br><span class="meta">${esc(r.title)}</span></td>
         <td>${esc(r.note_path || "(not set)")}</td><td>${esc((r.updated || "").slice(0, 16))}</td></tr>`).join("");
    $("runTable").hidden = runs.length === 0;
    $("runEmpty").hidden = runs.length > 0;
    $("runEmpty").textContent = "No runs. Start one under New run.";
  }

  // ── gates ────────────────────────────────────────────────────────────
  async function loadGates() {
    const gates = await getJSON("/api/gates");
    $("gateList").innerHTML = gates.map((g) => `
      <article class="card ${g.authored ? "s-complete" : "s-seed"}">
        <header><h3>${esc(g.gate)}</h3><span class="pill state">${g.authored ? "authored" : "not authored"}</span></header>
        <p>${esc(g.must_answer)}</p>
        ${g.answers.length ? `<p class="meta">answers: ${g.answers.map((a) => esc(`${a.section}. ${a.topic}`)).join(" · ")}</p>` : ""}
        ${g.unresolved.length ? `<p class="step">declared gap: ${g.unresolved.map((u) => esc(u.topic)).join("; ")}</p>` : ""}
        <p class="meta">needed by: ${g.needed_by.length ? g.needed_by.map(esc).join(", ") : "none yet"}</p>
      </article>`).join("");
  }

  // ── new run ──────────────────────────────────────────────────────────
  let pipelines = [];
  async function loadPipelines() {
    pipelines = await getJSON("/api/pipelines");
    const select = $("newPipeline");
    select.innerHTML = pipelines.map((p) => `<option value="${esc(p.pipeline)}" ${p.status === "implemented" ? "" : "disabled"}>${esc(p.pipeline)}${p.status === "implemented" ? "" : " (not implemented)"}</option>`).join("");
    select.value = (pipelines.find((p) => p.status === "implemented") || {}).pipeline || "";
    describePipeline();
  }

  function describePipeline() {
    const chosen = pipelines.find((p) => p.pipeline === $("newPipeline").value);
    $("newMakes").textContent = chosen ? `${chosen.makes} Needs: ${chosen.requires.join(", ") || "no brand context"}. Class: ${chosen.class}.` : "";
  }

  async function createRun(event) {
    event.preventDefault();
    const result = $("newResult");
    result.hidden = false;
    result.textContent = "creating…";
    try {
      const made = await getJSON("/api/runs", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ pipeline: $("newPipeline").value, title: $("newTitle").value }),
      });
      result.innerHTML = `<p>run <strong>${esc(made.run.run_id)}</strong> created for <strong>${esc(made.run.pipeline)}</strong>.</p>
        <p>In a Claude Code session on this repo, say:</p><pre>${esc(made.command)}</pre><p class="meta">${esc(made.note)}</p>`;
      $("newTitle").value = "";
      loadRuns();
    } catch (problem) {
      result.innerHTML = `<p class="step">${esc(problem.message)}</p>`;
    }
  }

  // ── writing ──────────────────────────────────────────────────────────
  async function loadWriting() {
    const data = await getJSON("/api/writing");
    const body = $("writingTable").querySelector("tbody");
    body.innerHTML = data.files.map((f) => `<tr><td>${esc(f.kind || f.source_type)}</td><td>${esc(f.file)}</td></tr>`).join("");
    $("writingTable").hidden = data.files.length === 0;
    $("writingEmpty").hidden = data.files.length > 0;
    $("writingEmpty").textContent = "No creative-writing index. Build it: python creative-writing/vault/tools/vault_search.py index";
  }

  // ── the museum: a link to its own server, never a proxy ──────────────
  let museum = null;
  async function loadMuseum() {
    museum = await getJSON("/api/museum");
    $("libraryLink").href = museum.library;
    $("walkLink").href = museum.viewer;
    const tab = $("libraryTab");
    tab.href = museum.library;
    tab.hidden = false;
    await probeMuseum();
  }

  // An opaque cross-origin fetch says only whether something answers on that port;
  // the hub reads nothing from the museum.
  async function probeMuseum() {
    if (!museum) return;
    const state = $("museumState");
    let up = false;
    try {
      await fetch(museum.url + "data/museum-manifest.json", { mode: "no-cors", cache: "no-store" });
      up = true;
    } catch (_) { up = false; }
    const built = museum.built ? "" : ` The library file is not built yet: <code>${esc(museum.build)}</code>.`;
    state.innerHTML = up
      ? `museum server up at <a href="${esc(museum.url)}">${esc(museum.url)}</a>.${built}`
      : `museum server not running at ${esc(museum.url)}. Start it from the repo folder: <code>${esc(museum.command)}</code>${built}`;
    for (const id of ["libraryLink", "walkLink", "libraryTab"]) $(id).classList.toggle("off", !up);
  }

  // ── brushes ──────────────────────────────────────────────────────────
  let brushesMounted = false;
  async function mountBrushes() {
    if (brushesMounted) return;
    brushesMounted = true;
    const response = await fetch("brush/index.html", { method: "HEAD" }).catch(() => null);
    if (response && response.ok) {
      $("brushFrame").src = "brush/index.html";
    } else {
      $("brushFrame").hidden = true;
      $("brushEmpty").hidden = false;
    }
  }

  // ── boot ─────────────────────────────────────────────────────────────
  async function boot() {
    const status = $("status");
    try {
      applyTokens(await getJSON("/api/tokens"));
    } catch (problem) {
      status.textContent = `tokens: ${problem.message}`;
    }
    for (const tab of document.querySelectorAll(".tab")) tab.addEventListener("click", () => showTab(tab.dataset.tab));
    for (const id of ["noteKind", "noteStatus", "noteProject"]) $(id).addEventListener("change", renderNotes);
    $("noteSearch").addEventListener("input", () => { clearTimeout(searchTimer); searchTimer = setTimeout(searchNotes, 180); });
    $("newPipeline").addEventListener("change", describePipeline);
    $("newRun").addEventListener("submit", createRun);
    let last = "notes";
    try { last = localStorage.getItem("hub:tab") || "notes"; } catch (_) { /* private mode */ }
    showTab(last);
    const loads = [loadNotes(), loadRuns(), loadGates(), loadPipelines(), loadWriting(), loadMuseum()];
    const results = await Promise.allSettled(loads);
    const failed = results.filter((r) => r.status === "rejected");
    status.textContent = failed.length ? `${failed.length} of ${loads.length} views failed: ${failed[0].reason.message}` : "live";
  }

  document.addEventListener("DOMContentLoaded", boot);
})();
