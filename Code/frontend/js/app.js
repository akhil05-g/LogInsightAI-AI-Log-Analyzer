const API = window.location.origin;

/* ═══ SVG ICON HELPERS ═══ */
const ICONS = {
  success: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>',
  error: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>',
  warning: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>',
  info: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>',
  chart: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>',
  template: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg>',
  search: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>',
  alert: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>',
  levels: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/><line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/></svg>',
};

/* ═══ TOAST ═══ */
class Toast {
  constructor() {
    this.container = document.getElementById('toast-container');
  }
  show(message, type = 'info', duration = 4000) {
    const el = document.createElement('div');
    el.className = `toast toast-${type}`;
    el.innerHTML = `${ICONS[type] || ICONS.info}<span>${message}</span>`;
    this.container.appendChild(el);
    setTimeout(() => {
      el.style.opacity = '0';
      el.style.transform = 'translateX(30px)';
      setTimeout(() => el.remove(), 300);
    }, duration);
  }
}

/* ═══ UI CONTROLLER ═══ */
class UI {
  constructor() {
    this.page = 'landing';
    this.tab = 'analysis';

    document.querySelectorAll('.nav-link[data-page]').forEach(btn =>
      btn.addEventListener('click', () => this.showPage(btn.dataset.page))
    );
    document.querySelectorAll('.tab-btn-dash').forEach(btn =>
      btn.addEventListener('click', () => this.switchTab(btn.dataset.tab))
    );
    document.querySelectorAll('.sidebar-item[data-tab]').forEach(btn =>
      btn.addEventListener('click', () => this.switchTab(btn.dataset.tab))
    );
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const sidebar = document.getElementById('sidebar');
    if (sidebarToggle && sidebar) {
      sidebarToggle.addEventListener('click', () => sidebar.classList.toggle('collapsed'));
    }
    window.addEventListener('scroll', () => {
      document.querySelector('.glass-nav').classList.toggle('scrolled', window.scrollY > 20);
    });
  }

  showPage(page) {
    this.page = page;
    document.querySelectorAll('.page').forEach(el =>
      el.classList.toggle('active', el.id === 'page-' + page)
    );
    document.querySelectorAll('.nav-link[data-page]').forEach(btn =>
      btn.classList.toggle('active', btn.dataset.page === page)
    );
    const vantaBg = document.getElementById('vanta-bg');
    if (vantaBg) vantaBg.style.display = page === 'landing' ? '' : 'none';
    window.scrollTo(0, 0);
  }

  switchTab(tab) {
    this.tab = tab;
    document.querySelectorAll('.tab-btn-dash').forEach(btn =>
      btn.classList.toggle('active', btn.dataset.tab === tab)
    );
    document.querySelectorAll('.sidebar-item[data-tab]').forEach(btn =>
      btn.classList.toggle('active', btn.dataset.tab === tab)
    );
    document.querySelectorAll('.tab-pane').forEach(pane =>
      pane.classList.toggle('active', pane.id === 'pane-' + tab)
    );
  }

  showLoading(text = 'Analyzing...') {
    const overlay = document.getElementById('loading-overlay');
    document.getElementById('loading-text').textContent = text;
    overlay.classList.add('active');
  }

  hideLoading() {
    document.getElementById('loading-overlay').classList.remove('active');
  }
}

/* ═══ FILE MANAGER ═══ */
class Files {
  constructor(app) {
    this.app = app;
    this.logId = null;
    this.content = null;
    this.filename = null;
    this.initUpload();
  }

  initUpload() {
    const zone = document.getElementById('upload-zone');
    const input = document.getElementById('upload-input');
    const newUploadBtn = document.getElementById('btn-new-upload');

    zone.addEventListener('click', (e) => {
      // Don't open dialog if click came from the browse button or input itself
      if (e.target.closest('.upload-browse-btn') || e.target === input) return;
      input.click();
    });
    zone.addEventListener('dragover', e => { e.preventDefault(); zone.classList.add('drag-over'); });
    zone.addEventListener('dragleave', () => zone.classList.remove('drag-over'));
    zone.addEventListener('drop', e => {
      e.preventDefault();
      zone.classList.remove('drag-over');
      if (e.dataTransfer.files.length) this.upload(e.dataTransfer.files[0]);
    });
    input.addEventListener('change', () => {
      if (input.files.length) this.upload(input.files[0]);
    });
    newUploadBtn.addEventListener('click', () => {
      input.value = '';
      input.click();
    });
  }

  async upload(file) {
    if (!file.name.match(/\.(log|txt)$/i)) {
      this.app.toast.show('Please upload .log or .txt files', 'warning');
      return;
    }
    const fd = new FormData();
    fd.append('file', file);
    try {
      this.app.ui.showLoading('Uploading...');
      const resp = await fetch(`${API}/api/logs/upload`, { method: 'POST', body: fd });
      if (!resp.ok) {
        const text = await resp.text();
        let msg = 'Upload failed';
        try { msg = JSON.parse(text).detail || msg; } catch { msg = text || msg; }
        throw new Error(msg);
      }
      const data = await resp.json();

      this.logId = data.log_id;
      this.filename = data.filename;
      this.app.toast.show(`Uploaded: ${data.filename} (${data.line_count} lines)`, 'success');

      /* Update status bar */
      const sfn = document.getElementById('status-filename');
      if (sfn) sfn.textContent = data.filename;

      await this.loadContent(data.log_id);
      this.showFilePreview(data.filename, data.line_count);
      this.app.analysis.enable();
      this.app.ui.showPage('dashboard');
    } catch (e) {
      this.app.toast.show('Upload error: ' + e.message, 'error');
    } finally {
      this.app.ui.hideLoading();
    }
  }

  async loadContent(id) {
    const resp = await fetch(`${API}/api/logs/${id}`);
    const data = await resp.json();
    this.content = data.content;
    this.app.logView.render(data.content);
    document.getElementById('loaded-file').textContent = data.filename;
  }

  showFilePreview(filename, lineCount) {
    const zone = document.getElementById('upload-zone');
    const preview = document.getElementById('file-preview');
    zone.style.display = 'none';
    preview.classList.remove('hidden');
    document.getElementById('preview-filename').textContent = filename;
    document.getElementById('preview-meta').textContent = `${lineCount} lines`;
  }
}

/* ═══ LOG VIEWER ═══ */
class LogView {
  constructor() {
    this.rawLines = [];
    this.currentLevel = 'all';
    this.searchQuery = '';
    this.initFilters();
  }

  initFilters() {
    document.querySelectorAll('.log-filter-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.log-filter-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        this.currentLevel = btn.dataset.level;
        this.applyFilters();
      });
    });
    const searchInput = document.getElementById('log-search');
    if (searchInput) {
      searchInput.addEventListener('input', (e) => {
        this.searchQuery = e.target.value.toLowerCase();
        this.applyFilters();
      });
    }
  }

  render(content) {
    this.rawLines = content.split('\n');
    document.getElementById('log-count').textContent = this.rawLines.length + ' lines';
    this.applyFilters();
  }

  applyFilters() {
    const body = document.getElementById('log-body');
    let filtered = this.rawLines.map((line, i) => ({ line, index: i }));

    if (this.currentLevel !== 'all') {
      filtered = filtered.filter(({ line }) => {
        if (this.currentLevel === 'error') return /\bERROR\b|\bFATAL\b|\bCRITICAL\b/i.test(line);
        if (this.currentLevel === 'warn') return /\bWARN(ING)?\b/i.test(line);
        if (this.currentLevel === 'info') return /\bINFO\b/i.test(line);
        return true;
      });
    }

    if (this.searchQuery) {
      filtered = filtered.filter(({ line }) => line.toLowerCase().includes(this.searchQuery));
    }

    document.getElementById('log-count').textContent = `${filtered.length} / ${this.rawLines.length} lines`;

    if (filtered.length === 0) {
      body.innerHTML = '<div class="log-empty">No matching log lines</div>';
      return;
    }

    body.innerHTML = filtered.map(({ line, index }) => {
      let cls = '';
      if (/\bERROR\b|\bFATAL\b|\bCRITICAL\b/i.test(line)) cls = 'hl-error';
      else if (/\bWARN(ING)?\b/i.test(line)) cls = 'hl-warn';
      else if (/\bINFO\b/i.test(line)) cls = 'hl-info';
      let displayText = this.esc(line);
      if (this.searchQuery) {
        const regex = new RegExp(`(${this.escRegex(this.searchQuery)})`, 'gi');
        displayText = displayText.replace(regex, '<mark>$1</mark>');
      }
      return `<div class="log-line"><span class="log-num">${index + 1}</span><span class="log-text ${cls}">${displayText}</span></div>`;
    }).join('');
  }

  esc(s) {
    return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }

  escRegex(s) {
    return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  }
}

/* ═══ CHART ═══ */
class Chart {
  draw(canvasId, data) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const size = 220;
    canvas.width = size;
    canvas.height = size;
    const cx = size / 2, cy = size / 2, r = 80, ir = 52;
    const colors = { critical: '#991B1B', error: '#DC2626', warning: '#D97706', info: '#2563EB' };
    const total = Object.values(data).reduce((a, b) => a + b, 0);

    if (!total) {
      ctx.fillStyle = '#E2E8F0';
      ctx.beginPath(); ctx.arc(cx, cy, r, 0, Math.PI * 2); ctx.fill();
      ctx.fillStyle = '#fff';
      ctx.beginPath(); ctx.arc(cx, cy, ir, 0, Math.PI * 2); ctx.fill();
      ctx.fillStyle = '#94A3B8'; ctx.font = '500 13px Inter'; ctx.textAlign = 'center';
      ctx.fillText('No issues', cx, cy + 5);
      return;
    }

    let angle = -Math.PI / 2;
    Object.entries(data).forEach(([key, val]) => {
      if (!val) return;
      const slice = (val / total) * Math.PI * 2;
      ctx.beginPath(); ctx.moveTo(cx, cy);
      ctx.arc(cx, cy, r, angle, angle + slice);
      ctx.fillStyle = colors[key] || '#94A3B8'; ctx.fill();
      angle += slice;
    });

    ctx.beginPath(); ctx.arc(cx, cy, ir, 0, Math.PI * 2);
    ctx.fillStyle = '#fff'; ctx.fill();
    ctx.fillStyle = '#191c1e'; ctx.font = '700 24px Inter'; ctx.textAlign = 'center';
    ctx.fillText(total, cx, cy + 3);
    ctx.fillStyle = '#94A3B8'; ctx.font = '500 11px Inter';
    ctx.fillText('issues', cx, cy + 19);

    const legend = canvas.parentElement.querySelector('.chart-legend');
    if (legend) {
      legend.innerHTML = Object.entries(data)
        .filter(([, v]) => v > 0)
        .map(([k, v]) => `<span class="legend-item"><span class="legend-dot" style="background:${colors[k]}"></span>${k}: ${v}</span>`)
        .join('');
    }
  }
}

/* ═══ ANALYSIS ═══ */
class Analysis {
  constructor(app) {
    this.app = app;
    this.lastResults = null;
    document.getElementById('btn-full').addEventListener('click', () => this.run('full'));
    document.getElementById('btn-parse').addEventListener('click', () => this.run('parse'));
    document.getElementById('btn-detect').addEventListener('click', () => this.run('detect'));
    document.getElementById('btn-export').addEventListener('click', () => this.exportResults());
    document.getElementById('hero-cta').addEventListener('click', () => this.app.ui.showPage('dashboard'));
  }

  enable() {
    document.getElementById('btn-full').disabled = false;
    document.getElementById('btn-parse').disabled = false;
    document.getElementById('btn-detect').disabled = false;
  }

  async run(type) {
    const id = this.app.files.logId;
    if (!id) {
      this.app.toast.show('Upload a log file first', 'warning');
      return;
    }
    const steps = type === 'full'
      ? ['Connecting to MCP...', 'Parsing log structure...', 'Running 5-engine anomaly detection...', 'Training DeepLog LSTM model...', 'Correlating events...', 'Analyzing failure trends...', 'Running compliance audit...', 'Generating AI summary...']
      : type === 'parse'
        ? ['Connecting to MCP...', 'Parsing log structure...']
        : ['Connecting to MCP...', 'Running 5-engine anomaly detection...', 'Training DeepLog LSTM model...'];

    try {
      /* Update status bar */
      const engineEl = document.getElementById('status-engine');
      if (engineEl) { engineEl.className = 'status-item status-active'; engineEl.lastChild.textContent = ' Analyzing...'; }

      this.app.ui.showLoading(steps[0]);

      /* Cycle through loading text */
      let stepIdx = 0;
      const stepInterval = setInterval(() => {
        stepIdx++;
        if (stepIdx < steps.length) {
          document.getElementById('loading-text').textContent = steps[stepIdx];
        }
      }, 3000);

      const resp = await fetch(`${API}/api/analysis/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          log_id: id,
          analysis_type: type,
          sensitivity: document.getElementById('sens').value,
        }),
      });

      clearInterval(stepInterval);

      const data = await resp.json();
      if (data.error) {
        this.app.toast.show('Error: ' + data.error, 'error');
        return;
      }
      this.render(data);
      this.app.toast.show('Analysis complete!', 'success');
      this.app.ui.switchTab('analysis');
    } catch (e) {
      this.app.toast.show('Failed: ' + e.message, 'error');
    } finally {
      this.app.ui.hideLoading();
      const engineEl = document.getElementById('status-engine');
      if (engineEl) { engineEl.className = 'status-item status-idle'; engineEl.lastChild.textContent = ' Engine Idle'; }
    }
  }

  render(data) {
    this.lastResults = data;
    document.getElementById('btn-export').disabled = false;
    if (data.parse_result) this.renderParse(data.parse_result);
    if (data.detection_result) this.renderDetect(data.detection_result, data.issue_explanations || []);
    if (data.correlation_result) this.renderCorrelation(data.correlation_result);
    if (data.prediction_result) this.renderPrediction(data.prediction_result);
    if (data.compliance_result) this.renderCompliance(data.compliance_result);
    // Metadata section removed per user request
    if (data.ai_summary) this.renderAI(data.ai_summary);
  }

  exportResults() {
    if (!this.lastResults) {
      this.app.toast.show('No analysis results to export', 'warning');
      return;
    }
    const blob = new Blob([JSON.stringify(this.lastResults, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `loginsight-analysis-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
    this.app.toast.show('Analysis exported successfully', 'success');
  }

  renderParse(r) {
    const pane = document.getElementById('pane-analysis');
    const s = r.summary || {};
    const tm = r.template_mining || {};
    const rp = r.regex_parsing || {};
    const ld = s.level_distribution || rp.level_distribution || {};
    const tmpls = (tm.templates || []).slice(0, 15);
    const now = new Date().toLocaleString();

    const statsHtml = `
      <div class="analysis-ts">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
        Analysis completed at ${now}
      </div>
      <div class="stats-grid">
        <div class="stat-card"><div class="stat-label">Total Lines</div><div class="stat-value">${s.total_lines || '—'}</div></div>
        <div class="stat-card"><div class="stat-label">Templates</div><div class="stat-value">${s.unique_templates || '—'}</div></div>
        <div class="stat-card"><div class="stat-label">Format</div><div class="stat-value">${s.format || '—'}</div></div>
        <div class="stat-card"><div class="stat-label">Errors</div><div class="stat-value">${(ld.ERROR || 0) + (ld.FATAL || 0)}</div></div>
      </div>`;

    let templateHtml = '';
    if (tmpls.length) {
      templateHtml = `
        <div class="glass-card dash-full">
          <div class="card-title">${ICONS.template} Log Templates <span class="badge badge-info">${tmpls.length}</span></div>
          <table class="tmpl-table">
            <thead><tr><th>#</th><th>Template</th><th>Count</th></tr></thead>
            <tbody>${tmpls.map((t, i) =>
              `<tr><td>${i + 1}</td><td class="tmpl-text">${this.esc(t.template || '')}</td><td class="tmpl-count">${t.count}</td></tr>`
            ).join('')}</tbody>
          </table>
        </div>`;
    }

    const chartHtml = `
      <div class="glass-card">
        <div class="card-title">${ICONS.chart} Severity Distribution</div>
        <div class="chart-wrap"><canvas id="sev-chart"></canvas><div class="chart-legend"></div></div>
      </div>`;

    const levelsHtml = `
      <div class="glass-card">
        <div class="card-title">${ICONS.levels} Log Levels</div>
        ${Object.entries(ld).map(([k, v]) =>
          `<div style="display:flex;justify-content:space-between;padding:8px 0;font-size:.82rem"><span>${k}</span><strong>${v}</strong></div>`
        ).join('') || '<p style="color:var(--on-surface-var);font-size:.82rem">None detected</p>'}
      </div>`;

    pane.innerHTML = statsHtml + `<div class="dash-grid">${chartHtml}${levelsHtml}</div>${templateHtml}<div id="detect-results"></div>`;
    setTimeout(() => this.app.chart.draw('sev-chart', {
      critical: (ld.FATAL || 0) + (ld.CRITICAL || 0),
      error: ld.ERROR || 0,
      warning: (ld.WARN || 0) + (ld.WARNING || 0),
      info: (ld.INFO || 0) + (ld.DEBUG || 0),
    }), 50);
  }

  renderDetect(r, issueExplanations = []) {
    const el = document.getElementById('detect-results') || document.getElementById('pane-analysis');
    const s = r.summary || {};
    const kw = r.keyword_detection || {};
    const pt = r.pattern_detection || {};
    const dets = (kw.detections || []).concat(pt.matches || []).sort((a, b) => {
      const order = { critical: 0, error: 1, warning: 2, info: 3 };
      return (order[a.severity] || 3) - (order[b.severity] || 3);
    });

    const health = s.health_assessment || '';
    const hc = health.split('\u2014')[0]?.trim() || 'FAIR';

    let html = `
      <div class="glass-card dash-full" style="margin-top:20px">
        <div class="card-title" style="justify-content:space-between">
          ${ICONS.search} Detection Results
          <span class="health-badge health-${hc}">${health}</span>
        </div>
        <div class="stats-grid" style="margin-top:12px">
          <div class="stat-card"><div class="stat-label">Total Issues</div><div class="stat-value">${s.total_issues_found || 0}</div></div>
          <div class="stat-card"><div class="stat-label">ML Anomalies</div><div class="stat-value">${s.logai_anomalies || 0}</div></div>
          <div class="stat-card"><div class="stat-label">DeepLog LSTM</div><div class="stat-value">${s.deeplog_anomalies || 0}</div></div>
          <div class="stat-card"><div class="stat-label">Statistical</div><div class="stat-value">${s.statistical_anomalies || 0}</div></div>
          <div class="stat-card"><div class="stat-label">Keywords</div><div class="stat-value">${s.keyword_detections || 0}</div></div>
          <div class="stat-card"><div class="stat-label">Patterns</div><div class="stat-value">${s.pattern_matches || 0}</div></div>
        </div>
      </div>`;

    // Build a lookup map from Gemini explanations: line_number -> explanation obj
    // Coerce to Number because Gemini may return line_number as string
    const explainMap = new Map();
    if (issueExplanations && issueExplanations.length) {
      for (const ex of issueExplanations) {
        if (ex.line_number) explainMap.set(Number(ex.line_number), ex);
      }
    }

    // Deduplicate: keep highest severity detection per line
    const sevRank = { critical: 0, error: 1, warning: 2, info: 3 };
    const uniqueMap = new Map();
    for (const d of dets) {
      const ln = Number(d.line_number);
      if (!uniqueMap.has(ln) || (sevRank[d.severity] ?? 3) < (sevRank[uniqueMap.get(ln).severity] ?? 3)) {
        uniqueMap.set(ln, d);
      }
    }
    const uniqueDets = [...uniqueMap.values()].sort((a, b) => (sevRank[a.severity] ?? 3) - (sevRank[b.severity] ?? 3));

    if (uniqueDets.length) {
      const hasExplanations = explainMap.size > 0;
      html += `
        <div class="glass-card dash-full">
          <div class="card-title">${ICONS.alert} Issues Found <span class="badge badge-error">${uniqueDets.length}</span>
            ${hasExplanations ? '<span class="badge badge-info" style="margin-left:8px;font-size:.7rem">AI-Explained</span>' : ''}
          </div>
          <div class="issue-explained-list">
            ${uniqueDets.slice(0, 50).map((d, idx) => {
              const ex = explainMap.get(Number(d.line_number));
              const rawText = this.esc((d.context || d.matched_text || '').substring(0, 200));
              if (ex) {
                // Render as expandable card with AI explanation
                return `
                  <div class="issue-card sev-${d.severity}" onclick="this.classList.toggle('expanded')">
                    <div class="issue-card-header">
                      <span class="error-line">L${d.line_number}</span>
                      <span class="badge badge-${d.severity}">${d.severity}</span>
                      <span class="issue-explanation-text">${this.esc(ex.explanation || '')}</span>
                      <span class="issue-expand-icon">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"/></svg>
                      </span>
                    </div>
                    <div class="issue-card-details">
                      <div class="issue-detail-row">
                        <div class="issue-detail-label">
                          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>
                          Impact
                        </div>
                        <div class="issue-detail-value">${this.esc(ex.impact || 'No impact information available.')}</div>
                      </div>
                      <div class="issue-detail-row">
                        <div class="issue-detail-label">
                          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
                          Fix
                        </div>
                        <div class="issue-detail-value">${this.esc(ex.fix || 'Review the log context and apply the appropriate corrective action.')}</div>
                      </div>
                      <div class="issue-detail-row issue-raw-log">
                        <div class="issue-detail-label">
                          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="4 17 10 11 4 5"/><line x1="12" y1="19" x2="20" y2="19"/></svg>
                          Raw Log
                        </div>
                        <div class="issue-detail-value"><code>${rawText}</code></div>
                      </div>
                    </div>
                  </div>`;
              } else {
                // Fallback: simple row without explanation
                return `
                  <div class="issue-card sev-${d.severity} no-expand">
                    <div class="issue-card-header">
                      <span class="error-line">L${d.line_number}</span>
                      <span class="badge badge-${d.severity}">${d.severity}</span>
                      <span class="issue-explanation-text">${rawText}</span>
                    </div>
                  </div>`;
              }
            }).join('')}
          </div>
        </div>`;
    }
    el.innerHTML = (el.id === 'detect-results' ? '' : el.innerHTML) + html;

    // Render engine performance metrics
    this.renderEngineMetrics(r);
  }

  renderEngineMetrics(r) {
    const el = document.getElementById('detect-results') || document.getElementById('pane-analysis');
    const dl = r.deeplog_detection || {};
    const pyod = r.anomaly_detection || {};
    const logai = r.logai_analysis || {};

    const rows = [];

    // DeepLog LSTM
    rows.push({
      engine: 'DeepLog LSTM',
      type: 'Deep Learning',
      status: dl.available === false ? 'Unavailable' : 'Active',
      metrics: dl.available === false ? dl.message || 'PyTorch not installed' : [
        `Device: ${dl.device || 'N/A'}`,
        `Model: ${dl.model || 'LSTM'}`,
        `Templates: ${dl.num_templates || 0}`,
        `Window: ${dl.window_size || 0} | Top-K: ${dl.top_k || 0}`,
        `Training Sequences: ${dl.training_sequences || 0}`,
        `Anomalies: ${dl.anomaly_count || 0}`,
        `Anomaly Rate: ${dl.anomaly_rate || 0}%`,
      ].join(' | '),
    });

    // PyOD Isolation Forest
    rows.push({
      engine: 'PyOD IsolationForest',
      type: 'Statistical ML',
      status: pyod.error ? 'Error' : 'Active',
      metrics: pyod.error || [
        `Lines Analyzed: ${pyod.total_lines_analyzed || 0}`,
        `Anomalies: ${pyod.total_anomalies || 0}`,
        `Anomaly Rate: ${pyod.anomaly_rate || 0}%`,
      ].join(' | '),
    });

    // LogAI
    rows.push({
      engine: 'Salesforce LogAI',
      type: 'ML Pipeline',
      status: logai.available === false ? 'Unavailable' : logai.error ? 'Fallback' : 'Active',
      metrics: logai.available === false ? (logai.message || 'LogAI not installed') : logai.error || [
        `Lines Analyzed: ${logai.total_lines_analyzed || 0}`,
        `Templates: ${logai.templates_found || 0}`,
        `Anomalies: ${logai.anomaly_count || 0}`,
        `Avg Score: ${logai.avg_anomaly_score || 0}`,
      ].join(' | '),
    });

    // FlashText
    const kw = r.keyword_detection || {};
    rows.push({
      engine: 'FlashText Keywords',
      type: 'Rule-Based',
      status: 'Active',
      metrics: [
        `Detections: ${kw.total_detections || 0}`,
        `Lines with Issues: ${kw.lines_with_issues || 0}`,
      ].join(' | '),
    });

    // Regex Patterns
    const pt = r.pattern_detection || {};
    const catDist = pt.category_distribution || {};
    const cats = Object.entries(catDist).map(([k,v]) => `${k}: ${v}`).join(', ');
    rows.push({
      engine: 'Regex Patterns',
      type: 'Rule-Based',
      status: 'Active',
      metrics: [
        `Matches: ${pt.total_matches || 0}`,
        cats ? `Categories: ${cats}` : '',
      ].filter(Boolean).join(' | '),
    });

    const statusColors = { Active: '#16A34A', Unavailable: '#94A3B8', Error: '#DC2626', Fallback: '#D97706' };

    let html = `
      <div class="glass-card dash-full" style="margin-top:20px">
        <div class="card-title">${ICONS.chart} Engine Performance Metrics <span class="badge badge-info">5 engines</span></div>
        <table class="tmpl-table" style="margin-top:12px">
          <thead><tr><th>Engine</th><th>Type</th><th>Status</th><th>Metrics</th></tr></thead>
          <tbody>${rows.map(r => `
            <tr>
              <td><strong>${r.engine}</strong></td>
              <td style="font-size:.78rem;color:var(--on-surface-var)">${r.type}</td>
              <td><span class="badge badge-${r.status === 'Active' ? 'success' : r.status === 'Error' ? 'error' : r.status === 'Fallback' ? 'warning' : 'info'}">${r.status}</span></td>
              <td style="font-size:.75rem;color:var(--on-surface-var);max-width:400px">${r.metrics}</td>
            </tr>
          `).join('')}</tbody>
        </table>
      </div>`;

    el.innerHTML += html;
  }

  renderCorrelation(r) {
    const el = document.getElementById('detect-results') || document.getElementById('pane-analysis');
    const roots = r.root_cause_candidates || [];
    const cascades = r.cascading_failures || [];
    const impact = r.component_impact || [];
    const summary = r.summary || {};

    let html = `
      <div class="glass-card dash-full" style="margin-top:20px">
        <div class="card-title">${ICONS.levels} Event Correlation <span class="badge badge-info">${r.total_event_groups || 0} groups</span></div>
        <div class="stats-grid" style="margin-top:12px">
          <div class="stat-card"><div class="stat-label">Error Events</div><div class="stat-value">${r.total_error_events || 0}</div></div>
          <div class="stat-card"><div class="stat-label">Cascading Failures</div><div class="stat-value">${summary.cascading_failure_count || 0}</div></div>
          <div class="stat-card"><div class="stat-label">Components Affected</div><div class="stat-value">${summary.unique_components_affected || 0}</div></div>
        </div>`;

    if (roots.length) {
      html += `<div class="card-title" style="margin-top:16px">${ICONS.alert} Root Cause Candidates</div>
        <div class="error-list">${roots.slice(0, 10).map(rc => `
          <div class="error-item sev-error">
            <span class="error-line">L${rc.line_number}</span>
            <span class="badge badge-error">${rc.severity}</span>
            <span class="error-content">${this.esc(rc.content?.substring(0, 180))}</span>
            <span style="color:var(--on-surface-var);font-size:.75rem;margin-left:auto">Cascade: ${rc.cascade_size} events across ${(rc.affected_components||[]).length} components</span>
          </div>`).join('')}</div>`;
    }

    if (impact.length) {
      html += `<div class="card-title" style="margin-top:16px">${ICONS.chart} Component Impact</div>
        <div style="display:flex;flex-wrap:wrap;gap:8px;margin-top:8px">
          ${impact.slice(0, 10).map(c => `<span class="badge badge-warning" style="font-size:.78rem">${c.component}: ${c.error_count} errors</span>`).join('')}
        </div>`;
    }

    html += `</div>`;
    el.innerHTML += html;
  }

  renderPrediction(r) {
    const el = document.getElementById('detect-results') || document.getElementById('pane-analysis');
    const trend = r.trend || {};
    const preds = r.component_predictions || [];
    const risk = r.overall_risk || 'LOW';
    const riskColors = { CRITICAL: '#991B1B', HIGH: '#DC2626', MEDIUM: '#D97706', LOW: '#16A34A' };

    let html = `
      <div class="glass-card dash-full" style="margin-top:20px">
        <div class="card-title" style="justify-content:space-between">
          ${ICONS.chart} Predictive Analysis
          <span class="badge badge-${risk === 'HIGH' || risk === 'CRITICAL' ? 'error' : risk === 'MEDIUM' ? 'warning' : 'success'}">Risk: ${risk}</span>
        </div>
        ${r.risk_summary ? `<p style="color:var(--on-surface-var);font-size:.85rem;margin:10px 0;line-height:1.5">${r.risk_summary}</p>` : ''}
        <div class="stats-grid" style="margin-top:12px">
          <div class="stat-card"><div class="stat-label">Error Events</div><div class="stat-value">${r.total_error_events || 0}</div></div>
          <div class="stat-card"><div class="stat-label">Error Rate</div><div class="stat-value">${r.overall_error_rate_pct || 0}%</div></div>
          <div class="stat-card"><div class="stat-label">Trend</div><div class="stat-value">${trend.direction || '—'}</div></div>
        </div>`;

    if (preds.length) {
      const highs = preds.filter(p => p.risk_level === 'HIGH' || p.risk_level === 'MEDIUM');
      if (highs.length) {
        html += `<div class="card-title" style="margin-top:16px">${ICONS.warning} At-Risk Components</div>
          <div class="error-list">${highs.slice(0, 8).map(p => `
            <div class="error-item sev-${p.risk_level === 'HIGH' ? 'error' : 'warning'}">
              <span class="badge badge-${p.risk_level === 'HIGH' ? 'error' : 'warning'}">${p.risk_level}</span>
              <span class="error-content">${this.esc(p.prediction)}</span>
              <span style="color:var(--on-surface-var);font-size:.75rem;margin-left:auto">${p.error_count} errors (${p.error_rate_pct}%)</span>
            </div>`).join('')}</div>`;
      }
    }

    html += `</div>`;
    el.innerHTML += html;
  }

  renderCompliance(r) {
    const el = document.getElementById('detect-results') || document.getElementById('pane-analysis');
    const score = r.compliance_score ?? 0;
    const grade = r.grade || '—';
    const status = r.status || 'UNKNOWN';
    const gradeColors = { A: '#16A34A', B: '#2563EB', C: '#D97706', F: '#DC2626' };
    const pii = r.pii_summary || {};
    const recs = r.recommendations || [];
    const audit = r.audit_trail_scores || {};

    let html = `
      <div class="glass-card dash-full" style="margin-top:20px">
        <div class="card-title" style="justify-content:space-between">
          ${ICONS.search} Compliance & Audit Report
          <span class="badge badge-${grade === 'A' ? 'success' : grade === 'B' ? 'info' : grade === 'C' ? 'warning' : 'error'}">Grade: ${grade} (${score}%)</span>
        </div>
        <div style="margin:12px 0">
          <span class="badge badge-info">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
            ${r.checks_passed || 0} / ${r.checks_total || 0} checks passed
          </span>
        </div>
        <div class="stats-grid" style="margin-top:12px">
          <div class="stat-card"><div class="stat-label">Compliance Score</div><div class="stat-value">${score}%</div></div>
          <div class="stat-card"><div class="stat-label">PII Findings</div><div class="stat-value">${Object.values(pii).reduce((a,b)=>a+b,0)}</div></div>
          <div class="stat-card"><div class="stat-label">Security Issues</div><div class="stat-value">${(r.security_findings || []).length}</div></div>
        </div>`;


    // Audit trail scores
    if (Object.keys(audit).length) {
      html += `<div class="card-title" style="margin-top:16px">${ICONS.levels} Audit Trail Completeness</div>
        <div style="margin-top:8px">
          ${Object.entries(audit).map(([k, v]) => {
            const label = k.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
            const color = v >= 70 ? '#16A34A' : v >= 40 ? '#D97706' : '#DC2626';
            return `<div style="display:flex;justify-content:space-between;align-items:center;padding:6px 0;font-size:.82rem">
              <span>${label}</span>
              <div style="display:flex;align-items:center;gap:8px">
                <div style="width:120px;height:6px;background:rgba(79,70,229,0.08);border-radius:3px;overflow:hidden">
                  <div style="width:${v}%;height:100%;background:${color};border-radius:3px"></div>
                </div>
                <strong style="color:${color}">${v}%</strong>
              </div>
            </div>`;
          }).join('')}
        </div>`;
    }

    // Recommendations
    if (recs.length) {
      html += `<div class="card-title" style="margin-top:16px">${ICONS.info} Recommendations</div>
        <div class="error-list">${recs.map(r => `
          <div class="error-item sev-${r.priority === 'HIGH' ? 'error' : 'warning'}">
            <span class="badge badge-${r.priority === 'HIGH' ? 'error' : 'warning'}">${r.priority}</span>
            <span class="error-content"><strong>${r.area}:</strong> ${this.esc(r.action)}</span>
            <span style="color:var(--on-surface-var);font-size:.72rem;margin-left:auto">${r.standard}</span>
          </div>`).join('')}</div>`;
    }

    html += `</div>`;
    el.innerHTML += html;
  }

  renderMeta(data) {
    const el = document.getElementById('detect-results') || document.getElementById('pane-analysis');
    const engines = data.engines_used || [];
    const timing = data.timing || {};

    if (!engines.length && !Object.keys(timing).length) return;

    let html = `
      <div class="glass-card dash-full" style="margin-top:20px">
        <div class="card-title">${ICONS.info} Analysis Metadata</div>
        <div style="display:flex;flex-wrap:wrap;gap:8px;margin-top:10px">`;

    if (engines.length) {
      html += engines.map(e => `<span class="badge badge-info" style="font-size:.75rem">${e}</span>`).join('');
    }

    html += `</div>`;

    if (Object.keys(timing).length) {
      html += `<div style="margin-top:12px;font-size:.82rem;color:var(--on-surface-var)">`;
      html += Object.entries(timing).map(([tool, sec]) => `<span style="margin-right:16px">${tool}: <strong>${sec}s</strong></span>`).join('');
      html += `</div>`;
    }

    html += `</div>`;
    el.innerHTML += html;
  }

  renderAI(md) {
    document.getElementById('pane-summary').innerHTML = `<div class="ai-summary">${this.md2html(md)}</div>`;
  }

  md2html(m) {
    if (!m) return '';
    const lines = m.split('\n');
    const out = [];
    let i = 0;

    while (i < lines.length) {
      const raw = lines[i];
      const trimmed = raw.trim();

      // ── Blank line → paragraph break ──
      if (trimmed === '') {
        out.push('<div class="ai-spacer"></div>');
        i++;
        continue;
      }

      // ── Horizontal rule ──
      if (/^-{3,}$/.test(trimmed) || /^\*{3,}$/.test(trimmed) || /^_{3,}$/.test(trimmed)) {
        out.push('<hr class="ai-hr">');
        i++;
        continue;
      }

      // ── Table block ──
      if (/^\|.+\|\s*$/.test(trimmed)) {
        const tableLines = [];
        while (i < lines.length && /^\|.+\|\s*$/.test(lines[i].trim())) {
          const tl = lines[i].trim();
          // Skip separator rows |---|---|
          if (!/^\|[\s:|-]+\|\s*$/.test(tl)) {
            tableLines.push(tl);
          }
          i++;
        }
        if (tableLines.length > 0) {
          const hdrCells = tableLines[0].split('|').filter(c => c.trim() !== '').map(c => `<th>${this._inlineMd(c.trim())}</th>`).join('');
          let tbody = '';
          for (let r = 1; r < tableLines.length; r++) {
            const cells = tableLines[r].split('|').filter(c => c.trim() !== '').map(c => `<td>${this._inlineMd(c.trim())}</td>`).join('');
            tbody += `<tr>${cells}</tr>`;
          }
          out.push(`<table class="ai-table"><thead><tr>${hdrCells}</tr></thead><tbody>${tbody}</tbody></table>`);
        }
        continue;
      }

      // ── Headings ──
      const h3 = trimmed.match(/^###\s+(.+)$/);
      if (h3) { out.push(`<h3>${this._inlineMd(h3[1])}</h3>`); i++; continue; }

      const h2 = trimmed.match(/^##\s+(.+)$/);
      if (h2) { out.push(`<h2 class="ai-section-heading">${this._inlineMd(h2[1])}</h2>`); i++; continue; }

      const h1 = trimmed.match(/^#\s+(.+)$/);
      if (h1) { out.push(`<h1>${this._inlineMd(h1[1])}</h1>`); i++; continue; }

      // ── Blockquote ──
      if (trimmed.startsWith('> ')) {
        const bqLines = [];
        while (i < lines.length && lines[i].trim().startsWith('> ')) {
          bqLines.push(lines[i].trim().substring(2));
          i++;
        }
        out.push(`<blockquote class="ai-blockquote">${bqLines.map(l => this._inlineMd(l)).join('<br>')}</blockquote>`);
        continue;
      }

      // ── Unordered list block ──
      if (/^[-*]\s+/.test(trimmed)) {
        const items = [];
        while (i < lines.length && /^\s*[-*]\s+/.test(lines[i])) {
          items.push(lines[i].trim().replace(/^[-*]\s+/, ''));
          i++;
        }
        out.push(`<ul class="ai-list">${items.map(it => `<li>${this._inlineMd(it)}</li>`).join('')}</ul>`);
        continue;
      }

      // ── Ordered list block ──
      if (/^\d+[.)\s]\s*/.test(trimmed)) {
        const items = [];
        while (i < lines.length && /^\s*\d+[.)\s]\s*/.test(lines[i].trim())) {
          items.push(lines[i].trim().replace(/^\d+[.)\s]\s*/, ''));
          i++;
        }
        out.push(`<ol class="ai-list">${items.map(it => `<li>${this._inlineMd(it)}</li>`).join('')}</ol>`);
        continue;
      }

      // ── Regular paragraph line ──
      // Collect consecutive non-special lines into a paragraph
      const pLines = [];
      while (i < lines.length) {
        const pl = lines[i].trim();
        if (pl === '' || /^-{3,}$/.test(pl) || /^#{1,3}\s/.test(pl) || /^\|.+\|/.test(pl)
            || /^[-*]\s+/.test(pl) || /^\d+[.)\s]\s/.test(pl) || pl.startsWith('> ')) {
          break;
        }
        pLines.push(pl);
        i++;
      }
      if (pLines.length > 0) {
        out.push(`<p>${pLines.map(l => this._inlineMd(l)).join('<br>')}</p>`);
      }
    }

    return out.join('\n');
  }

  /** Convert inline markdown: bold, italic, code, links */
  _inlineMd(s) {
    if (!s) return '';
    return s
      .replace(/\*\*\*(.+?)\*\*\*/g, '<strong><em>$1</em></strong>')
      .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.+?)\*/g, '<em>$1</em>')
      .replace(/`([^`]+)`/g, '<code class="ai-inline-code">$1</code>');
  }

  esc(s) {
    return (s || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }
}

/* ═══ APP ═══ */
class App {
  constructor() {
    this.toast = new Toast();
    this.ui = new UI();
    this.chart = new Chart();
    this.logView = new LogView();
    this.files = new Files(this);
    this.analysis = new Analysis(this);
  }
}

document.addEventListener('DOMContentLoaded', () => {
  window.app = new App();
});
