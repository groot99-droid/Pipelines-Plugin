/**
 * AIAssistPanel.js - conversational parameter editing via local Ollama
 *
 * Not a BasePanel subclass: the other panels are pure declarative
 * slider/toggle forms over BrushState, this one drives async network calls
 * and its own status/result UI, different enough in kind to keep separate.
 */

import { OllamaAssist } from '../ai/OllamaAssist.js';
import { BRUSH_PROPERTY_RANGES } from '../editor/BrushState.js';

export class AIAssistPanel {
  /**
   * @param {HTMLElement} container
   * @param {import('../editor/BrushState.js').BrushState} brushState
   * @param {(patch: object, summary: string) => void} onApply - applies a
   *   validated patch and pushes one history entry for it
   */
  constructor(container, brushState, onApply) {
    this.container = container;
    this.brushState = brushState;
    this.onApply = onApply;
    this.busy = false;
  }

  updateSliders() {
    /* no numeric controls to sync -- state changes render fresh next time */
  }

  render() {
    this.container.innerHTML = `
      <div class="panel-title">AI Assist</div>
      <p class="ai-blurb">
        Describe the change in plain language. The local model reads the current
        settings, proposes a parameter patch, and it's applied as one undoable step
        so you can always back out with Ctrl+Z.
      </p>
      <div class="ai-conn-row">
        <span class="ai-conn-dot" id="aiConnDot"></span>
        <span id="aiConnLabel">Ollama —</span>
        <button type="button" class="btn btn-icon ai-settings-toggle" id="aiSettingsBtn" title="Connection settings">⚙</button>
      </div>
      <div class="ai-settings" id="aiSettings" hidden>
        <label class="ai-field">Endpoint
          <input type="text" id="aiEndpoint" placeholder="http://localhost:11434">
        </label>
        <label class="ai-field">Tier
          <select id="aiTier">
            <option value="sm">sm — llama3.1:8b (everyday)</option>
            <option value="md">md — mistral-nemo:12b (AC + quiet desktop)</option>
          </select>
        </label>
      </div>
      <textarea id="aiInstruction" class="ai-instruction" rows="3"
        placeholder="e.g. make the grain rougher and reduce streamline"></textarea>
      <button type="button" class="btn btn-primary ai-apply-btn" id="aiApplyBtn">Apply with AI</button>
      <div id="aiResult" class="ai-result"></div>
    `;

    this.endpointInput = this.container.querySelector('#aiEndpoint');
    this.tierSelect = this.container.querySelector('#aiTier');
    this.settingsPanel = this.container.querySelector('#aiSettings');
    this.instructionInput = this.container.querySelector('#aiInstruction');
    this.applyBtn = this.container.querySelector('#aiApplyBtn');
    this.resultEl = this.container.querySelector('#aiResult');
    this.connDot = this.container.querySelector('#aiConnDot');
    this.connLabel = this.container.querySelector('#aiConnLabel');

    this.endpointInput.value = OllamaAssist.getEndpoint();
    this.tierSelect.value = OllamaAssist.getTierKey();

    this.container.querySelector('#aiSettingsBtn').addEventListener('click', () => {
      this.settingsPanel.hidden = !this.settingsPanel.hidden;
    });
    this.endpointInput.addEventListener('change', () => {
      OllamaAssist.setEndpoint(this.endpointInput.value.trim() || OllamaAssist.DEFAULT_ENDPOINT);
      this.refreshConnStatus();
    });
    this.tierSelect.addEventListener('change', () => {
      OllamaAssist.setTierKey(this.tierSelect.value);
      this.refreshConnStatus();
    });
    this.applyBtn.addEventListener('click', () => this.handleApply());
    this.instructionInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
        e.preventDefault();
        this.handleApply();
      }
    });

    this.refreshConnStatus();
  }

  async refreshConnStatus() {
    const endpoint = OllamaAssist.getEndpoint();
    const tier = OllamaAssist.getTier();
    try {
      const served = await OllamaAssist.fetchTags(endpoint);
      const ok = OllamaAssist.familyMatches(tier.model, served);
      this.connDot.className = 'ai-conn-dot ' + (ok ? 'on' : 'warn');
      this.connLabel.textContent = ok ? `Ollama — ${tier.model}` : `Ollama — ${tier.model} not pulled`;
    } catch (_) {
      this.connDot.className = 'ai-conn-dot off';
      this.connLabel.textContent = 'Ollama — unreachable';
    }
  }

  setBusy(busy) {
    this.busy = busy;
    this.applyBtn.disabled = busy;
    clearInterval(this.timerHandle);
    if (busy) {
      const start = Date.now();
      const tick = () => {
        const secs = Math.round((Date.now() - start) / 1000);
        this.applyBtn.innerHTML = `<span class="ai-spinner"></span> Thinking… ${secs}s`;
      };
      tick();
      this.timerHandle = setInterval(tick, 1000);
    } else {
      this.applyBtn.textContent = 'Apply with AI';
    }
  }

  async handleApply() {
    if (this.busy) return;
    const instruction = this.instructionInput.value.trim();
    if (!instruction) {
      this.instructionInput.focus();
      this.resultEl.innerHTML = '<p class="ai-summary ai-summary-warn">Describe a change first.</p>';
      return;
    }

    this.setBusy(true);
    this.resultEl.innerHTML =
      '<p class="ai-note">CPU generation on this laptop typically takes 30–90 seconds for a request this size.</p>';

    const endpoint = OllamaAssist.getEndpoint();
    const tier = OllamaAssist.getTier();
    const before = this.brushState.get();

    try {
      const served = await OllamaAssist.fetchTags(endpoint);
      if (!OllamaAssist.familyMatches(tier.model, served)) {
        throw new Error(
          `'${tier.model}' is not served — installed: ${served.join(', ') || '(none)'}. ` +
          `Run: ollama pull ${tier.model}`
        );
      }

      const prompt = OllamaAssist.buildPrompt(instruction, before);
      const raw = await OllamaAssist.generate(endpoint, {
        model: tier.model,
        prompt,
        options: { temperature: 0.2, num_ctx: tier.num_ctx, num_predict: tier.num_predict },
      });
      await OllamaAssist.evict(endpoint, tier.model);

      const parsed = OllamaAssist.extractJSON(raw);
      if (!parsed) {
        this.renderRawFailure(raw);
        return;
      }

      const { applied, rejected } = OllamaAssist.validatePatch(parsed.changes);
      if (Object.keys(applied).length === 0) {
        this.renderNoChanges(rejected, parsed.summary);
        return;
      }

      this.onApply(applied, parsed.summary || `AI edit: ${instruction}`);
      this.renderDiff(before, applied, rejected, parsed.summary);
      this.instructionInput.value = '';
    } catch (error) {
      this.renderError(error.message);
    } finally {
      this.setBusy(false);
    }
  }

  formatValue(key, value) {
    const range = BRUSH_PROPERTY_RANGES[key];
    return range ? range.display(value) : String(value);
  }

  renderDiff(before, applied, rejected, summary) {
    const rows = Object.entries(applied).map(([key, value]) => {
      const oldValue = before[key];
      const oldDisplay = typeof oldValue === 'boolean' ? String(oldValue) : this.formatValue(key, oldValue);
      const newDisplay = typeof value === 'boolean' ? String(value) : this.formatValue(key, value);
      return `<div class="ai-diff-row"><b>${key}</b> ${oldDisplay} → ${newDisplay}</div>`;
    }).join('');

    const rejectedHtml = rejected.length
      ? `<p class="ai-note">Ignored: ${rejected.map((r) => `${r.key} (${r.reason})`).join(', ')}</p>`
      : '';

    this.resultEl.innerHTML = `
      <p class="ai-summary">${this.escape(summary || 'Applied.')}</p>
      <div class="ai-diff">${rows}</div>
      ${rejectedHtml}
    `;
  }

  renderNoChanges(rejected, summary) {
    const rejectedHtml = rejected.length
      ? `<p class="ai-note">The model referenced properties that don't exist: ${rejected.map((r) => r.key).join(', ')}</p>`
      : '';
    this.resultEl.innerHTML = `
      <p class="ai-summary ai-summary-warn">No valid changes proposed.${summary ? ' ' + this.escape(summary) : ''}</p>
      ${rejectedHtml}
    `;
  }

  renderRawFailure(raw) {
    this.resultEl.innerHTML = `
      <p class="ai-summary ai-summary-error">The model didn't return valid JSON. Try rephrasing, or a smaller request.</p>
      <details class="ai-raw"><summary>Show raw response</summary><pre>${this.escape(raw)}</pre></details>
    `;
  }

  renderError(message) {
    this.resultEl.innerHTML = `<p class="ai-summary ai-summary-error">${this.escape(message)}</p>`;
  }

  escape(s) {
    return String(s ?? '').replace(/[&<>"']/g, (c) => ({
      '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
    }[c]));
  }
}

export default AIAssistPanel;
