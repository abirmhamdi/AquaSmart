/* ─── AquaSmart SPA ─────────────────────────────────────── */
const API = '';  // same origin

// ─── Icons (Lucide shapes, inlined: no download needed) ────
const ICONS = {
 "thermometer": "<path d=\"M14 4v10.54a4 4 0 1 1-4 0V4a2 2 0 0 1 4 0Z\" />",
 "flask-conical": "<path d=\"M14 2v6a2 2 0 0 0 .245.96l5.51 10.08A2 2 0 0 1 18 22H6a2 2 0 0 1-1.755-2.96l5.51-10.08A2 2 0 0 0 10 8V2\" /> <path d=\"M6.453 15h11.094\" /> <path d=\"M8.5 2h7\" />",
 "test-tube": "<path d=\"M14.5 2v17.5c0 1.4-1.1 2.5-2.5 2.5c-1.4 0-2.5-1.1-2.5-2.5V2\" /> <path d=\"M8.5 2h7\" /> <path d=\"M14.5 16h-5\" />",
 "waves": "<path d=\"M2 12q2.5 2 5 0t5 0 5 0 5 0\" /> <path d=\"M2 19q2.5 2 5 0t5 0 5 0 5 0\" /> <path d=\"M2 5q2.5 2 5 0t5 0 5 0 5 0\" />",
 "check-circle-2": "<circle cx=\"12\" cy=\"12\" r=\"10\" /> <path d=\"m16 9-5.5 5.5L8 12\" />",
 "alert-triangle": "<path d=\"m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3\" /> <path d=\"M12 9v4\" /> <path d=\"M12 17h.01\" />",
 "x-circle": "<circle cx=\"12\" cy=\"12\" r=\"10\" /> <path d=\"m15 9-6 6\" /> <path d=\"m9 9 6 6\" />",
 "sun": "<circle cx=\"12\" cy=\"12\" r=\"4\" /> <path d=\"M12 2v2\" /> <path d=\"M12 20v2\" /> <path d=\"m4.93 4.93 1.41 1.41\" /> <path d=\"m17.66 17.66 1.41 1.41\" /> <path d=\"M2 12h2\" /> <path d=\"M20 12h2\" /> <path d=\"m6.34 17.66-1.41 1.41\" /> <path d=\"m19.07 4.93-1.41 1.41\" />",
 "moon": "<path d=\"M20.985 12.486a9 9 0 1 1-9.473-9.472c.405-.022.617.46.402.803a6 6 0 0 0 8.268 8.268c.344-.215.825-.004.803.401\" />",
 "droplets": "<path d=\"M7 16.3c2.2 0 4-1.83 4-4.05 0-1.16-.57-2.26-1.71-3.19S7.29 6.75 7 5.3c-.29 1.45-1.14 2.84-2.29 3.76S3 11.1 3 12.25c0 2.22 1.8 4.05 4 4.05z\" /> <path d=\"M12.56 6.6A10.97 10.97 0 0 0 14 3.02c.5 2.5 2 4.9 4 6.5s3 3.5 3 5.5a6.98 6.98 0 0 1-11.91 4.97\" />",
 "shield-check": "<path d=\"M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z\" /> <path d=\"m9 12 2 2 4-4\" />",
 "eye": "<path d=\"M2.062 12.348a1 1 0 0 1 0-.696 10.75 10.75 0 0 1 19.876 0 1 1 0 0 1 0 .696 10.75 10.75 0 0 1-19.876 0\" /> <circle cx=\"12\" cy=\"12\" r=\"3\" />",
 "bot": "<path d=\"M12 8V4H8\" /> <rect width=\"16\" height=\"12\" x=\"4\" y=\"8\" rx=\"2\" /> <path d=\"M2 14h2\" /> <path d=\"M20 14h2\" /> <path d=\"M15 13v2\" /> <path d=\"M9 13v2\" />",
 "x": "<path d=\"M18 6 6 18\" /> <path d=\"m6 6 12 12\" />",
 "send": "<path d=\"M14.536 21.686a.5.5 0 0 0 .937-.024l6.5-19a.496.496 0 0 0-.635-.635l-19 6.5a.5.5 0 0 0-.024.937l7.93 3.18a2 2 0 0 1 1.112 1.11z\" /> <path d=\"m21.854 2.147-10.94 10.939\" />",
 "menu": "<path d=\"M4 5h16\" /> <path d=\"M4 12h16\" /> <path d=\"M4 19h16\" />"
};
function icon(name) {
  return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">${ICONS[name]}</svg>`;
}
Object.assign(ICONS, {"sliders-horizontal": "<path d=\"M10 5H3\" /> <path d=\"M12 19H3\" /> <path d=\"M14 3v4\" /> <path d=\"M16 17v4\" /> <path d=\"M21 12h-9\" /> <path d=\"M21 19h-5\" /> <path d=\"M21 5h-7\" /> <path d=\"M8 10v4\" /> <path d=\"M8 12H3\" />", "sparkles": "<path d=\"M11.017 2.814a1 1 0 0 1 1.966 0l1.051 5.558a2 2 0 0 0 1.594 1.594l5.558 1.051a1 1 0 0 1 0 1.966l-5.558 1.051a2 2 0 0 0-1.594 1.594l-1.051 5.558a1 1 0 0 1-1.966 0l-1.051-5.558a2 2 0 0 0-1.594-1.594l-5.558-1.051a1 1 0 0 1 0-1.966l5.558-1.051a2 2 0 0 0 1.594-1.594z\" /> <path d=\"M20 2v4\" /> <path d=\"M22 4h-4\" /> <circle cx=\"4\" cy=\"20\" r=\"2\" />", "activity": "<path d=\"M22 12h-2.48a2 2 0 0 0-1.93 1.46l-2.35 8.36a.25.25 0 0 1-.48 0L9.24 2.18a.25.25 0 0 0-.48 0l-2.35 8.36A2 2 0 0 1 4.49 12H2\" />", "calculator": "<rect width=\"16\" height=\"20\" x=\"4\" y=\"2\" rx=\"2\" /> <line x1=\"8\" x2=\"16\" y1=\"6\" y2=\"6\" /> <line x1=\"16\" x2=\"16\" y1=\"14\" y2=\"18\" /> <path d=\"M16 10h.01\" /> <path d=\"M12 10h.01\" /> <path d=\"M8 10h.01\" /> <path d=\"M12 14h.01\" /> <path d=\"M8 14h.01\" /> <path d=\"M12 18h.01\" /> <path d=\"M8 18h.01\" />", "layers": "<path d=\"M12.83 2.18a2 2 0 0 0-1.66 0L2.6 6.08a1 1 0 0 0 0 1.83l8.58 3.91a2 2 0 0 0 1.66 0l8.58-3.9a1 1 0 0 0 0-1.83z\" /> <path d=\"M2 12a1 1 0 0 0 .58.91l8.6 3.91a2 2 0 0 0 1.65 0l8.58-3.9A1 1 0 0 0 22 12\" /> <path d=\"M2 17a1 1 0 0 0 .58.91l8.6 3.91a2 2 0 0 0 1.65 0l8.58-3.9A1 1 0 0 0 22 17\" />", "cpu": "<path d=\"M12 20v2\" /> <path d=\"M12 2v2\" /> <path d=\"M17 20v2\" /> <path d=\"M17 2v2\" /> <path d=\"M2 12h2\" /> <path d=\"M2 17h2\" /> <path d=\"M2 7h2\" /> <path d=\"M20 12h2\" /> <path d=\"M20 17h2\" /> <path d=\"M20 7h2\" /> <path d=\"M7 20v2\" /> <path d=\"M7 2v2\" /> <rect x=\"4\" y=\"4\" width=\"16\" height=\"16\" rx=\"2\" /> <rect x=\"8\" y=\"8\" width=\"8\" height=\"8\" rx=\"1\" />", "external-link": "<path d=\"M15 3h6v6\" /> <path d=\"M10 14 21 3\" /> <path d=\"M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6\" />", "terminal": "<path d=\"M12 19h8\" /> <path d=\"m4 17 6-6-6-6\" />", "play": "<path d=\"M5 5a2 2 0 0 1 3.008-1.728l11.997 6.998a2 2 0 0 1 .003 3.458l-12 7A2 2 0 0 1 5 19z\" />", "rotate-ccw": "<path d=\"M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8\" /> <path d=\"M3 3v5h5\" />", "users": "<path d=\"M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2\" /> <path d=\"M16 3.128a4 4 0 0 1 0 7.744\" /> <path d=\"M22 21v-2a4 4 0 0 0-3-3.87\" /> <circle cx=\"9\" cy=\"7\" r=\"4\" />", "database": "<ellipse cx=\"12\" cy=\"5\" rx=\"9\" ry=\"3\" /> <path d=\"M3 5V19A9 3 0 0 0 21 19V5\" /> <path d=\"M3 12A9 3 0 0 0 21 12\" />", "trending-down": "<path d=\"M16 17h6v-6\" /> <path d=\"m22 17-8.5-8.5-5 5L2 7\" />", "chart-no-axes-combined": "<path d=\"M12 16v5\" /> <path d=\"M16 14.639V21\" /> <path d=\"M20 10.656V21\" /> <path d=\"m22 3-8.646 8.646a.5.5 0 0 1-.708 0L9.354 8.354a.5.5 0 0 0-.707 0L2 15\" /> <path d=\"M4 18.463V21\" /> <path d=\"M8 14.656V21\" />"});
if (window.Chart) Chart.defaults.font.family = "'Plus Jakarta Sans', sans-serif";

// ─── Theme (light / dark) ───────────────────────────────────
const css = n => getComputedStyle(document.documentElement).getPropertyValue('--' + n).trim();
const P = {   // palette read from the CSS variables, so canvases and inline colours match the active theme
  get accent()  { return css('accent'); },   get success() { return css('success'); },
  get warning() { return css('warning'); },  get orange()  { return css('orange'); },
  get danger()  { return css('danger'); },   get indigo()  { return css('indigo'); },
  get muted()   { return css('text-muted'); }, get grid()  { return css('chart-grid'); },
};

function currentTheme() { return document.documentElement.getAttribute('data-theme') === 'dark' ? 'dark' : 'light'; }

function syncThemeSwitch() {
  const dark = currentTheme() === 'dark';
  const sw = document.getElementById('theme-switch');
  sw.setAttribute('aria-checked', String(dark));
  sw.title = dark ? 'Switch to light mode' : 'Switch to dark mode';
}

function refreshActivePage() {   // redraw charts and inline colours after a theme change
  const id = document.querySelector('.page.active')?.id;
  if (id === 'page-home')      { loadOverview(); loadTrend(); }
  if (id === 'page-ponds')     loadPonds();
  if (id === 'page-analytics') loadAnalytics();
  if (id === 'page-federated') loadFLStatus();
}

function setTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  try { localStorage.setItem('aquasmart-theme', theme); } catch (e) {}
  syncThemeSwitch();
  refreshActivePage();
}

document.getElementById('theme-switch').addEventListener('click', () => setTheme(currentTheme() === 'dark' ? 'light' : 'dark'));
syncThemeSwitch();

// ─── Navigation ────────────────────────────────────────────
function navigate(page, scrollToAbout) {
  document.querySelectorAll('.nav-link[data-page]').forEach(el =>
    el.classList.toggle('active', el.dataset.page === page && !scrollToAbout));
  document.querySelector('.nav-link[data-about]')?.classList.toggle('active', !!scrollToAbout);
  document.querySelectorAll('.page').forEach(el => el.classList.remove('active'));
  document.getElementById(`page-${page}`)?.classList.add('active');
  document.getElementById('about').style.display  = page === 'home' ? '' : 'none';   // About Us lives under the home page
  document.getElementById('nav-links').classList.remove('open');

  if (page === 'home')      { loadOverview(); loadTrend(); }
  if (page === 'ponds')     loadPonds();
  if (page === 'analytics') loadAnalytics();
  if (page === 'federated') loadFLStatus();

  if (scrollToAbout) document.getElementById('about').scrollIntoView({ behavior: 'smooth' });
  else window.scrollTo(0, 0);
}

document.querySelectorAll('[data-page]').forEach(btn => {
  btn.addEventListener('click', () => navigate(btn.dataset.page));
});
document.querySelector('[data-about]')?.addEventListener('click', () => navigate('home', true));   // optional: only if an About link exists
document.getElementById('nav-toggle').addEventListener('click', () => {
  document.getElementById('nav-links').classList.toggle('open');
});

// ─── Clock ──────────────────────────────────────────────────
function updateClock() {
  document.getElementById('live-time').textContent =
    new Date().toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
}
setInterval(updateClock, 1000); updateClock();

// ─── Helpers ────────────────────────────────────────────────
function stratBadge(s) {
  const map = { STOP:'red', REDUCE:'orange', NORMAL:'green', INCREASE:'blue' };
  return `<span class="badge badge-${map[s]||'teal'}">${s}</span>`;
}
function wqiBadge(cat) {
  const map = { Excellent:'blue', Good:'green', Fair:'yellow', Poor:'red' };
  return `<span class="badge badge-${map[cat]||'teal'}">${cat}</span>`;
}
function alertClass(sev) {
  return { critical:'alert-critical', warning:'alert-warning', info:'alert-info' }[sev] || 'alert-info';
}
function paramColor(param, val) {
  const ranges = {
    temperature:       { ok:[20,28], warn:[15,33] },
    dissolved_oxygen:  { ok:[5,12],  warn:[3,12] },
    ph:                { ok:[6.5,8.5], warn:[5.5,9.5] },
    turbidity:         { ok:[0,30],  warn:[0,50] },
    ammonia:           { ok:[0,.02], warn:[0,.06] },
    nitrate:           { ok:[0,10],  warn:[0,20] },
  };
  const r = ranges[param]; if (!r) return 'var(--accent)';
  if (val < r.ok[0] || val > r.ok[1]) {
    if (val < r.warn[0] || val > r.warn[1]) return 'var(--danger)';
    return 'var(--orange)';
  }
  return 'var(--success)';
}

// ─── Trend chart state ──────────────────────────────────────
let trendChart = null, trendData = [], currentParam = 'temperature';

// ─── Trend chart ────────────────────────────────────────────
async function loadTrend() {
  const data = await fetch(`${API}/api/dashboard/history?hours=24`).then(r => r.json());
  trendData = data;
  renderTrend();
}

function setTrendParam(param) {
  currentParam = param;
  document.querySelectorAll('#trend-seg button').forEach(b => b.classList.toggle('active', b.dataset.param === param));
  renderTrend();
}

function renderTrend() {
  const labels = trendData.map(r => r.timestamp.substring(11, 16));
  const vals   = trendData.map(r => r[currentParam]);
  const colors = { temperature:P.orange, dissolved_oxygen:P.accent, ph:P.indigo, wqi:P.success, ammonia:P.danger, turbidity:P.warning };
  const col = P.accent;

  const cfg = {
    type: 'line',
    data: {
      labels,
      datasets: [{
        label: currentParam.replace('_',' '),
        data: vals,
        borderColor: col,
        backgroundColor: col + '18',
        borderWidth: 2,
        pointRadius: 0,
        fill: true,
        tension: 0.4,
      }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { grid: { color: P.grid }, ticks: { color: P.muted, maxTicksLimit: 8, font:{size:10} } },
        y: { grid: { color: P.grid }, ticks: { color: P.muted, font:{size:10} } },
      },
    }
  };

  if (trendChart) { trendChart.destroy(); }
  trendChart = new Chart(document.getElementById('trendChart'), cfg);
}

// ─── Monitoring (navy pond cards) ────────────────────────────
function onNavy(level) { return level === 'good' ? 'good' : level; }   // good = mint, ok = amber, bad = red

async function loadPonds() {
  const grid = document.getElementById('ponds-grid');
  try {
    const ponds = await fetch(`${API}/api/dashboard/ponds`).then(r => r.json());
    const tone  = { STOP:'bad', REDUCE:'ok', NORMAL:'', INCREASE:'' };
    const lvl   = (key, v) => kpiLevel(KPIS.find(k => k.key === key), v);
    const wTone = w => w >= 70 ? '' : (w >= 45 ? 'ok' : 'bad');
    grid.innerHTML = ponds.map(p => {
      const lt = lvl('temperature', p.temperature), ld = lvl('dissolved_oxygen', p.dissolved_oxygen), lp = lvl('ph', p.ph);
      const wt = wTone(p.wqi);
      return `
      <div class="mon-card">
        <div class="mon-glow"></div>
        <div class="mon-top">
          <div class="mon-head">
            <h2>${icon('waves')}${p.name}</h2>
            <span class="mon-pill ${tone[p.strategy] || ''}">${p.strategy}</span>
          </div>
          <div class="mon-metrics">
            <div><span>Fish</span><b>${p.population}</b></div>
            <div><span>Weight</span><b>${Number(p.avg_weight_g).toFixed(1)} <small>g</small></b></div>
            <div><span>Temp</span><b class="${lt}">${p.temperature.toFixed(1)} <small>°C</small></b></div>
            <div><span>DO</span><b class="${ld}">${p.dissolved_oxygen.toFixed(1)} <small>mg/L</small></b></div>
            <div><span>pH</span><b class="${lp}">${p.ph.toFixed(2)}</b></div>
            <div><span>WQI</span><b>${p.wqi.toFixed(1)} <small class="cat ${wt}">${p.wqi_category}</small></b></div>
          </div>
        </div>
        <div class="mon-bar"><div class="track"><div class="fill ${wt}" style="width:${Math.max(0, Math.min(100, p.wqi))}%"></div></div></div>
      </div>`;
    }).join('');
  } catch (e) {
    grid.innerHTML = '<div class="alert alert-warning">Could not load ponds. Is the server running?</div>';
  }
}

// ─── Predictions ─────────────────────────────────────────────
function revealPrediction() {   // the results appear only after the button is pressed
  const out = document.getElementById('pr-output');
  const first = out.hidden;
  out.hidden = false;
  if (first) {
    out.classList.add('reveal');
    setTimeout(() => out.scrollIntoView({ behavior: 'smooth', block: 'start' }), 80);
  }
}

const REC_STATES = {
  NORMAL:   { tone:'good', icon:'check-circle-2', title:'Feeding recommended', sub:'Water conditions are within acceptable range.',          note:'Your fish are healthy and ready to eat.', mult:'Standard rate' },
  INCREASE: { tone:'good', icon:'check-circle-2', title:'Feeding recommended', sub:'Water conditions are great right now.',                  note:'Your fish are healthy and ready to eat.', mult:'Boosted rate' },
  REDUCE:   { tone:'ok',   icon:'alert-triangle', title:'Reduce feeding rate', sub:'Water conditions need monitoring before full feeding.',  note:'Adjust aeration and monitor closely.',    mult:'Reduced rate' },
  STOP:     { tone:'bad',  icon:'x-circle',       title:'Do not feed',         sub:'Water conditions are dangerous right now.',              note:'Fix the water quality first, then feed again.', mult:'Feeding paused' },
};
let _modelScore;   // R2 of the trained model on held-out data (shown on the Confidence card)

async function getModelScore() {
  if (_modelScore !== undefined) return _modelScore;
  try { const st = await fetch(`${API}/api/dashboard/stats`).then(r => r.json()); _modelScore = st.model_score ?? null; }
  catch (e) { _modelScore = null; }
  return _modelScore;
}

function setAlertBanner(state, iconName, lines) {
  const b = document.getElementById('alert-banner');
  b.dataset.state = state;
  document.getElementById('alert-icon').innerHTML = icon(iconName);
  document.getElementById('alert-text').innerHTML = lines.map(l => `<div>${l}</div>`).join('');
}

async function runPrediction() {
  const num = id => parseFloat(document.getElementById(id).value);
  const payload = {
    temperature: num('f-temp'), dissolved_oxygen: num('f-do'), ph: num('f-ph'),
    turbidity: num('f-turb'), ammonia: num('f-ammo'), nitrate: num('f-nit') || 3.0,
    fish_weight_g: num('f-fw'), population: parseInt(document.getElementById('f-pop').value, 10),
    base_feed_kg: num('f-feed'),
  };
  if (Object.values(payload).some(v => Number.isNaN(v))) return;   // wait until every field has a value
  try {
    const res = await fetch(`${API}/api/predict`, { method:'POST', headers:{ 'Content-Type':'application/json' }, body: JSON.stringify(payload) });
    if (!res.ok) throw new Error((await res.json()).detail || 'Request failed');
    const r  = await res.json();
    const st = REC_STATES[r.strategy] || REC_STATES.NORMAL;

    document.getElementById('rec-banner').dataset.state = st.tone;
    document.getElementById('rec-icon').innerHTML = icon(st.icon);
    document.getElementById('rec-title').textContent = st.title;
    document.getElementById('rec-sub').textContent   = st.sub;
    document.getElementById('rec-note').textContent  = st.note;
    document.getElementById('rec-feed').textContent  = Number(r.recommended_feed_kg).toFixed(2);

    document.getElementById('kpi-wqi').textContent       = Number(r.water_quality_index).toFixed(2);
    document.getElementById('kpi-wqi-label').textContent = r.wqi_category;
    document.getElementById('kpi-mlpred').textContent    = r.ml_prediction_g != null ? Number(r.ml_prediction_g).toFixed(2) : '-';
    document.getElementById('kpi-mult').textContent      = `×${r.multiplier}`;
    document.getElementById('kpi-mult-sub').textContent  = st.mult;
    document.getElementById('kpi-conf').textContent      = r.confidence;
    const score = await getModelScore();
    document.getElementById('kpi-conf-sub').textContent  = score != null ? `Model score ${Number(score).toFixed(2)}` : 'Model confidence';

    const alerts = r.parameter_alerts || [];
    if (!alerts.length) setAlertBanner('good', 'check-circle-2', ['All parameters are within safe range.']);
    else setAlertBanner(alerts.some(a => a.severity === 'critical') ? 'bad' : 'ok', 'alert-triangle',
                        alerts.map(a => `<strong>${a.param}</strong> (${a.value} ${a.unit}): ${a.message}`));
    document.querySelector('.pr-results').hidden = false;
    revealPrediction();
  } catch (err) {
    setAlertBanner('bad', 'x-circle', [`Could not get a recommendation: ${err.message}. Make sure the backend is running.`]);
    document.querySelector('.pr-results').hidden = true;   // nothing to show except the error
    revealPrediction();
  }
}

document.getElementById('predict-form').addEventListener('submit', (e) => { e.preventDefault(); runPrediction(); });

// ─── Analytics ──────────────────────────────────────────────
const AN = { charts: {}, hidden: { tempdo: {}, ph: {}, ammo: {}, wqi: {} } };   // hidden: legend toggles survive redraws
const AN_ORANGE = '#F97316', AN_INDIGO = '#6366F1', AN_RED = '#EF4444', AN_GREEN = '#10B981';

function anOptions(twoAxes) {
  const tick = { color: P.muted, font: { size: 9 } };
  const scales = {
    x: { grid: { display: false }, ticks: { ...tick, maxTicksLimit: 8 } },
    y: { grid: { color: P.grid }, ticks: tick },
  };
  if (twoAxes) scales.y1 = { position: 'right', grid: { drawOnChartArea: false }, ticks: tick };
  return {
    responsive: true, maintainAspectRatio: false, interaction: { mode: 'index', intersect: false },
    plugins: { legend: { display: false },
      tooltip: { backgroundColor: '#0F2D4A', titleColor: '#ffffff', bodyColor: '#ffffff', borderColor: 'rgba(62,193,163,.4)', borderWidth: 1,
                 padding: 10, cornerRadius: 12, boxPadding: 4, titleFont: { size: 11, weight: '700' }, bodyFont: { size: 11 } } },
    scales,
  };
}
const anSet = (label, data, color, extra = {}) =>
  ({ label, data, borderColor: color, backgroundColor: color + '1f', borderWidth: 2, fill: true, tension: 0.4, pointRadius: 0, pointHoverRadius: 4, ...extra });

async function loadAnalytics() {
  let rows;
  try { rows = await fetch(`${API}/api/dashboard/history?hours=48`).then(r => r.json()); }
  catch (e) { document.getElementById('an-grid').insertAdjacentHTML('afterbegin', '<div class="alert alert-warning" style="grid-column:1/-1">Could not load analytics data. Is the server running?</div>'); return; }
  if (!window.Chart || !rows.length) return;
  const labels = rows.map(r => r.timestamp.substring(11, 16));
  const col = k => rows.map(r => r[k]);
  const defs = {
    chartTempDO:         { key: 'tempdo', two: true, sets: [anSet('Temperature (°C)', col('temperature'), AN_ORANGE, { yAxisID: 'y' }),
                                                              anSet('Dissolved O₂ (mg/L)', col('dissolved_oxygen'), P.accent, { yAxisID: 'y1' })] },
    chartPH:             { key: 'ph',     sets: [anSet('pH Level', col('ph'), AN_INDIGO)] },
    chartAmmoniaNitrate: { key: 'ammo',   sets: [anSet('Ammonia (mg/L)', col('ammonia'), AN_RED), anSet('Nitrate (mg/L)', col('nitrate'), AN_GREEN)] },
    chartWQI:            { key: 'wqi',    sets: [anSet('WQI Score', col('wqi'), P.accent)] },
  };
  for (const [id, d] of Object.entries(defs)) {
    if (AN.charts[id]) AN.charts[id].destroy();
    d.sets.forEach((ds, i) => { ds.hidden = !!AN.hidden[d.key][i]; });
    const opts = anOptions(d.two);
    if (d.two) { opts.scales.y.display = !AN.hidden[d.key][0]; opts.scales.y1.display = !AN.hidden[d.key][1]; }
    AN.charts[id] = new Chart(document.getElementById(id), { type: 'line', data: { labels, datasets: d.sets }, options: opts });
    AN.charts[id]._key = d.key;
  }
  document.querySelectorAll('#an-grid .lg').forEach(b => b.setAttribute('aria-pressed', String(!AN.hidden[b.dataset.chart][b.dataset.idx])));
}

// clickable legends: show or hide a line
document.getElementById('an-grid').addEventListener('click', (e) => {
  const b = e.target.closest('.lg');
  if (!b) return;
  const key = b.dataset.chart, idx = Number(b.dataset.idx);
  const hide = !AN.hidden[key][idx];
  AN.hidden[key][idx] = hide;
  b.setAttribute('aria-pressed', String(!hide));
  const chart = Object.values(AN.charts).find(c => c && c._key === key);
  if (!chart) return;
  chart.data.datasets[idx].hidden = hide;
  if (key === 'tempdo') chart.options.scales[idx === 0 ? 'y' : 'y1'].display = !hide;
  chart.update();
});

// ML model information pop-up (real details from the loaded model)
let _modalReturnFocus = null;
async function openModelModal() {
  const bd = document.getElementById('ml-modal-backdrop'), body = document.getElementById('ml-modal-body');
  _modalReturnFocus = document.activeElement;
  body.innerHTML = '<div class="spinner"></div>';
  bd.hidden = false;
  document.body.style.overflow = 'hidden';
  document.getElementById('close-ml-modal-btn').focus();
  try {
    const info = await fetch(`${API}/api/dashboard/stats`).then(r => r.json());
    renderModelModal(info);
  } catch (e) {
    body.innerHTML = '<div class="alert alert-warning">Could not load model information. Is the server running?</div>';
  }
}
function closeModelModal() {
  document.getElementById('ml-modal-backdrop').hidden = true;
  document.body.style.overflow = '';
  if (_modalReturnFocus && _modalReturnFocus.focus) _modalReturnFocus.focus();
}
function renderModelModal(info) {
  const feats = info.features || [], SHOW = 12;
  const task = (info.task_type || '-').replace(/^./, c => c.toUpperCase());
  const m = (info.note || '').match(/^Trained by\s+(.+)$/i);
  const trained = m ? `<span>Trained by</span><code>${m[1]}</code>` : (info.note ? `<span>${info.note}</span>` : '');
  document.getElementById('ml-modal-body').innerHTML = `
    <div class="ml-stats">
      <div class="ml-stat"><div class="l">Model</div><div class="v">${info.model_name || '-'}</div></div>
      <div class="ml-stat"><div class="l">Task</div><div class="v">${task}</div></div>
      <div class="ml-stat"><div class="l">Features</div><div class="v">${info.features_count ?? feats.length}</div></div>
      <div class="ml-stat"><div class="l">Samples</div><div class="v">${Number(info.training_samples || 0).toLocaleString()}</div></div>
    </div>
    ${trained ? `<div class="ml-trained">${icon('terminal')}${trained}</div>` : ''}
    ${feats.length ? `<h3 class="ml-feat-title">Feature List</h3><div class="ml-feats" id="ml-feats"></div>` : ''}`;
  if (!feats.length) return;
  let expanded = false;
  const draw = () => {
    const shown = expanded ? feats : feats.slice(0, SHOW);
    document.getElementById('ml-feats').innerHTML = shown.map(f => `<span class="chip">${f}</span>`).join('') +
      (feats.length > SHOW ? `<button type="button" class="chip" id="ml-feats-toggle">${expanded ? 'Show less' : `+${feats.length - SHOW} more`}</button>` : '');
    const t = document.getElementById('ml-feats-toggle');
    if (t) t.addEventListener('click', () => { expanded = !expanded; draw(); });
  };
  draw();
}
document.getElementById('ml-modal-backdrop').addEventListener('click', (e) => { if (e.target.id === 'ml-modal-backdrop') closeModelModal(); });
document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && !document.getElementById('ml-modal-backdrop').hidden) closeModelModal(); });

// ─── Chatbot ────────────────────────────────────────────────
function appendMessage(role, html, suggestions) {
  const msgs = document.getElementById('chat-messages');
  const isUser = role === 'user';
  const div = document.createElement('div');
  div.className = `message ${role}`;

  const formatted = html
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\n/g, '<br>');

  let sugHtml = '';
  if (suggestions && suggestions.length) {
    sugHtml = `<div class="suggestions">${suggestions.map(s =>
      `<span class="suggestion-chip" onclick="sendSuggestion(this)">${s}</span>`
    ).join('')}</div>`;
  }

  div.innerHTML = `
    <div class="msg-avatar ${role}">${isUser ? 'You' : 'AB'}</div>
    <div>
      <div class="msg-bubble">${formatted}</div>
      ${sugHtml}
    </div>`;
  msgs.appendChild(div);
  msgs.scrollTop = msgs.scrollHeight;
}

function showTyping() {
  const msgs = document.getElementById('chat-messages');
  const div = document.createElement('div');
  div.id = 'typing-indicator';
  div.className = 'message bot';
  div.innerHTML = `<div class="msg-avatar bot">AB</div><div class="msg-bubble"><div class="typing"><span></span><span></span><span></span></div></div>`;
  msgs.appendChild(div);
  msgs.scrollTop = msgs.scrollHeight;
}

function hideTyping() {
  document.getElementById('typing-indicator')?.remove();
}

async function sendChat() {
  const input = document.getElementById('chat-input');
  const text = input.value.trim();
  if (!text) return;

  appendMessage('user', text);
  input.value = '';
  showTyping();

  try {
    const r = await fetch(`${API}/api/chat`, {
      method: 'POST', headers: {'Content-Type':'application/json'},
      body: JSON.stringify({ message: text })
    }).then(r => r.json());

    await new Promise(res => setTimeout(res, 600));
    hideTyping();
    appendMessage('bot', r.reply, r.suggestions);
  } catch(e) {
    hideTyping();
    appendMessage('bot', 'Connection error. Make sure the backend server is running.', []);
  }
}

function sendSuggestion(el) {
  document.getElementById('chat-input').value = el.textContent;
  sendChat();
}

// Floating chat widget
function toggleChat(force) {
  const panel = document.getElementById('chat-panel');
  const fab   = document.getElementById('chat-fab');
  const open  = force === undefined ? !panel.classList.contains('open') : force;
  panel.classList.toggle('open', open);
  fab.classList.toggle('open', open);
  fab.setAttribute('aria-label', open ? 'Close AquaBot chat' : 'Open AquaBot chat');
  if (open) setTimeout(() => document.getElementById('chat-input').focus(), 150);
}
function openChat() { toggleChat(true); }
document.addEventListener('keydown', e => { if (e.key === 'Escape') toggleChat(false); });

// ─── Overview (home) ─────────────────────────────────────────
let _ovData = null;   // latest reading

const KPIS = [
  { key:'temperature',      label:'Temp.',        unit:'°C',   icon:'thermometer',   digits:1, good:[20,28],   ok:[15,32],
    msg:{ good:'Water temperature is optimal',   ok:'Water temperature is acceptable', bad:'Water temperature is out of range' }, advice:'Check shading or heating.' },
  { key:'dissolved_oxygen', label:'Dissolved O₂', unit:'mg/L', icon:'thermometer',   digits:1, good:[5,12],    ok:[3,12],
    msg:{ good:'Oxygen levels are adequate',     ok:'Oxygen is getting low',           bad:'Oxygen is critically low' },          advice:'Turn on the aerator.' },
  { key:'ph',               label:'pH',           unit:'',     icon:'flask-conical', digits:1, good:[6.5,8.5], ok:[5.5,9.5],
    msg:{ good:'pH is within the target range',  ok:'pH is drifting from the target',  bad:'pH is out of range' },                advice:'Test the water and correct the balance.' },
  { key:'ammonia',          label:'Ammonia',      unit:'mg/L', icon:'test-tube',     digits:4, good:[0,.02],   ok:[0,.06],
    msg:{ good:'Ammonia levels are safe',        ok:'Ammonia is rising',               bad:'Ammonia is at a toxic level' },       advice:'Change part of the water.' },
  { key:'turbidity',        label:'Turbidity',    unit:'NTU',  icon:'waves',         digits:2, good:[0,20],    ok:[0,30], infoOnly:true,
    msg:{ good:'Water clarity is good',          ok:'Clarity needs monitoring',        bad:'Water is too cloudy' },               advice:'Check the filter and reduce feeding.' },
  { key:'nitrate',          label:'Nitrate',      unit:'mg/L', icon:'flask-conical', digits:2, good:[0,10],    ok:[0,20], infoOnly:true,
    msg:{ good:'Nitrate levels are within range', ok:'Nitrate is getting high',        bad:'Nitrate is too high' },               advice:'Change part of the water.' },
];

function kpiLevel(k, v) {
  if (v >= k.good[0] && v <= k.good[1]) return 'good';
  if (v >= k.ok[0]   && v <= k.ok[1])   return 'ok';
  return 'bad';
}

// feeding decision: the four core readings count fully; turbidity and nitrate only when they are really bad
function overallState(d) {
  const levels = KPIS.map(k => { const l = kpiLevel(k, d[k.key]); return (k.infoOnly && l === 'ok') ? 'good' : l; });
  if (levels.includes('bad')) return 'STOP';
  if (levels.includes('ok'))  return 'REDUCE';
  return 'FEED';
}

const FEED_STATES = {
  FEED:   { tone:'good', icon:'check-circle-2', title:'Feeding recommended', desc:'Water conditions are great right now.',          sub:'Your fish are healthy and ready to eat.' },
  REDUCE: { tone:'ok',   icon:'alert-triangle', title:'Reduce feeding',      desc:'Some readings are outside the ideal range.',      sub:'Give about half the usual portion and keep watching the water.' },
  STOP:   { tone:'bad',  icon:'x-circle',       title:'Do not feed',         desc:'Water conditions are dangerous right now.',       sub:'Fix the water quality first, then feed again.' },
};

const TIPS = [
  { icon:'sun',          text:'Feed 2-3 times daily in 5-10 minute windows to maximize growth and minimize feed waste.' },
  { icon:'droplets',     text:'Regularly monitor water temperature, pH, and dissolved oxygen levels in real-time.' },
  { icon:'shield-check', text:'Avoid overfeeding to prevent water pollution, ammonia spikes, and fish mortality.' },
  { icon:'eye',          text:'Clear water means a healthy pond. Good visibility helps you spot potential problems early.' },
];

async function loadOverview() {
  try {
    const d = await fetch(`${API}/api/dashboard/current`).then(r => r.json());
    _ovData = d;

    document.getElementById('kpi-cards').innerHTML = KPIS.map(k => {
      const lv  = kpiLevel(k, d[k.key]);
      const cls = lv === 'bad' ? 'bad' : (lv === 'ok' && !k.infoOnly ? 'ok' : '');
      return `<div class="kpi">
        <div class="kpi-head">${icon(k.icon)}<span>${k.label}</span></div>
        <div class="kpi-val">${Number(d[k.key]).toFixed(k.digits)}${k.unit ? ` <small>${k.unit}</small>` : ''}</div>
        <p class="kpi-msg ${cls}">${k.msg[lv]}</p>
      </div>`;
    }).join('');

    const state = overallState(d);
    const fs = FEED_STATES[state];
    document.getElementById('feed-answer').innerHTML = `
      <div class="feed-box" data-state="${fs.tone}">
        <div class="fb-text">
          <div class="head">${icon(fs.icon)}<h3>${fs.title}</h3></div>
          <p class="desc">${fs.desc}</p>
          <p class="sub">${fs.sub}</p>
        </div>
        <div class="score">
          <span class="l">Water Quality</span>
          <span class="n">${Math.round(d.wqi)}</span>
          <span class="c">${d.wqi_category || ''}</span>
        </div>
      </div>`;

    renderTips(d, state);
    calcFeed();
    loadOverviewPonds();
  } catch (e) {
    const el = document.getElementById('feed-answer');
    if (el) el.innerHTML = '<div class="alert alert-critical">Could not load water data. Is the server running?</div>';
  }
}

function renderTips(d, state) {
  const el = document.getElementById('tips');
  if (!el) return;
  let first = '';
  if (state !== 'FEED') {   // when something is off, the most urgent reading comes first
    const issues = KPIS.map(k => ({ k, lv: kpiLevel(k, d[k.key]) }))
                       .filter(x => x.lv === 'bad' || (x.lv === 'ok' && !x.k.infoOnly))
                       .sort((a, b) => (b.lv === 'bad') - (a.lv === 'bad'));
    if (issues.length) first = `<div class="tip ${issues[0].lv}">${icon('alert-triangle')}<span>${issues[0].k.msg[issues[0].lv]}. ${issues[0].k.advice}</span></div>`;
  }
  el.innerHTML = first + TIPS.map(t => `<div class="tip">${icon(t.icon)}<span>${t.text}</span></div>`).join('');
}

async function loadOverviewPonds() {
  const el = document.getElementById('ov-ponds');
  if (!el) return;
  try {
    const ponds = await fetch(`${API}/api/dashboard/ponds`).then(r => r.json());
    const tone  = { STOP:'bad', REDUCE:'ok', NORMAL:'', INCREASE:'' };
    const label = { STOP:'Stop', REDUCE:'Reduce', NORMAL:'Normal', INCREASE:'Increase' };
    el.innerHTML = ponds.map(p => `
      <div class="ov-pond" onclick="navigate('ponds')">
        <div class="l"><span class="dot ${tone[p.strategy] || ''}"></span><span class="nm">${p.name}</span></div>
        <div class="r"><span class="wqi">WQI: ${Math.round(p.wqi)}</span><span class="pill ${tone[p.strategy] || ''}">${label[p.strategy] || p.strategy}</span></div>
      </div>`).join('');
  } catch (e) {
    el.innerHTML = '<div class="small text-muted">Could not load ponds.</div>';
  }
}

function calcFeed() {
  const count  = parseFloat(document.getElementById('num-fish').value)   || 0;
  const weight = parseFloat(document.getElementById('avg-weight').value) || 0;
  let mult = 1, extra = '', color = '';
  if (_ovData) {
    const st = overallState(_ovData);
    mult = { FEED:1, REDUCE:0.55, STOP:0 }[st];
    if (st === 'REDUCE') { extra = 'Reduced by 45% because water conditions are not ideal.'; color = 'var(--warning)'; }
    if (st === 'STOP')   { extra = 'Feeding is paused because water conditions are dangerous.'; color = 'var(--danger)'; }
  }
  const kg = (count * weight * 0.03 / 1000) * mult;   // 3% of total body weight
  document.getElementById('feed-amount').textContent = kg.toFixed(2);
  const ex = document.getElementById('feed-extra');
  ex.textContent = extra; ex.style.color = color;
}

// ─── Federated Learning & SMPC ──────────────────────────────
const FL = { chart: null, theme: null, timer: null, total: 0 };
const $fl = (id) => document.getElementById(id);

function flSetButton(mode) {   // 'start' | 'running' | 'again'
  const b = $fl('fl-start-btn');
  if (mode === 'running') {
    b.disabled = true;
    b.innerHTML = '<span class="spin"></span><span class="bt">Training in progress...</span>';
  } else {
    b.disabled = false;
    b.innerHTML = `<span class="bi">${icon(mode === 'again' ? 'rotate-ccw' : 'play')}</span><span class="bt">${mode === 'again' ? 'Run Training Again' : 'Start Federated Training'}</span>`;
  }
}

function flMessage(kind, title, paragraphs) {
  const el = $fl('fl-message');
  el.innerHTML = `<div class="fl-msg ${kind === 'bad' ? 'bad' : ''}"><h4>${icon(kind === 'bad' ? 'x-circle' : 'check-circle-2')}${title}</h4>${paragraphs.join('')}</div>`;
  el.hidden = false;
}

function flDrawChart(hist) {
  if (!window.Chart) return;
  const labels = hist.map(h => `R${h.round}`), data = hist.map(h => h.avg_rmse);
  const th = currentTheme();
  if (FL.chart && FL.theme !== th) { FL.chart.destroy(); FL.chart = null; }   // redraw with the new theme colours
  if (!FL.chart) {
    FL.theme = th;
    const tick = { color: P.muted, font: { size: 10 } };
    const title = (text) => ({ display: true, text, color: P.muted, font: { size: 10, weight: '600' } });
    FL.chart = new Chart($fl('fl-chart'), {
      type: 'line',
      data: { labels, datasets: [{ label: 'Global RMSE', data, borderColor: '#3EC1A3', backgroundColor: 'rgba(62,193,163,.12)', borderWidth: 3,
                                   fill: true, tension: 0.35, pointRadius: 3, pointBackgroundColor: '#3EC1A3', pointBorderColor: '#3EC1A3' }] },
      options: {
        responsive: true, maintainAspectRatio: false, animation: { duration: 300 },
        plugins: { legend: { display: false },
          tooltip: { backgroundColor: '#0F2D4A', titleColor: '#ffffff', bodyColor: '#ffffff', borderColor: 'rgba(62,193,163,.4)', borderWidth: 1, padding: 10, cornerRadius: 12 } },
        scales: { x: { title: title('Training round'), grid: { display: false }, ticks: tick },
                  y: { title: title('RMSE'), grid: { color: P.grid }, ticks: tick, beginAtZero: false } },
      },
    });
  } else {
    FL.chart.data.labels = labels;
    FL.chart.data.datasets[0].data = data;
    FL.chart.update();
  }
}

function flCards(clients, training) {
  const pill = training ? '<span class="fl-pill run">Training</span>' : '<span class="fl-pill">Aggregated</span>';
  return clients.map(c => `
    <div class="fl-card">
      <div class="top"><h3>${icon('waves')}${c.pond}</h3>${pill}</div>
      <div class="m"><span>RMSE</span><b>${c.rmse != null ? Number(c.rmse).toFixed(3) : '-'}</b></div>
      <div class="m"><span>R²</span><b class="${c.r2 != null && c.r2 < 0 ? 'neg' : 'mint'}">${c.r2 != null ? Number(c.r2).toFixed(3) : '-'}</b></div>
    </div>`).join('');
}

function renderFL(s) {
  const hist = s.rounds_history || [];
  const training = s.status === 'training';
  if (!hist.length && !training && s.status !== 'error') {      // nothing has run yet: empty states
    $fl('fl-status-section').hidden = true;
    $fl('fl-contrib').hidden = true;  $fl('fl-contrib-empty').hidden = false;
    $fl('fl-chart-empty').hidden = false;
    flDrawChart([]);
    flSetButton('start');
    return;
  }
  $fl('fl-status-section').hidden = false;
  $fl('fl-chart-empty').hidden = hist.length > 0;
  flDrawChart(hist);

  const cur = s.current_round || hist.length, tot = s.total_rounds || FL.total || cur;
  $fl('fl-round-label').textContent = `${cur} / ${tot}`;
  $fl('fl-progress-bar').style.width = `${tot ? Math.round(100 * cur / tot) : 0}%`;
  const last = hist[hist.length - 1];
  $fl('fl-rmse').textContent = last ? Number(last.avg_rmse).toFixed(3) : '-';
  $fl('fl-r2').textContent   = last ? Number(last.avg_r2).toFixed(3)   : '-';

  if (last && last.clients && last.clients.length) {
    $fl('fl-contrib-empty').hidden = true;
    const grid = $fl('fl-contrib');
    grid.hidden = false;
    grid.innerHTML = flCards(last.clients, training);
  }

  if (training) { $fl('fl-message').hidden = true; flSetButton('running'); return; }
  if (s.status === 'error') {
    flMessage('bad', 'Training failed', [`<p>${s.error || 'Something went wrong while training.'}</p>`]);
    flSetButton('again');
    return;
  }
  const nClients = s.n_clients || (last && last.clients ? last.clients.length : 0);
  const check = s.smpc && s.smpc.distortion_x != null
    ? `<p class="chk">SMPC check: masked updates were about ${Number(s.smpc.distortion_x).toLocaleString()}x their real size, yet the aggregate matches plain FedAvg (error ${Number(s.smpc.aggregate_error).toExponential(1)}).</p>` : '';
  flMessage('good', 'Training Completed', [
    `<p>Training completed successfully across ${nClients} pond clients in ${tot} rounds. Model updates were masked locally and aggregated using FedAvg + SMPC.</p>`,
    `<p class="chk" style="font-weight:800;color:var(--tone,var(--mint-dark))">Raw sensor data stayed on each client.</p>`, check]);
  flSetButton('again');
}

async function loadFLStatus() {
  try {
    const s = await fetch(`${API}/api/federated/status`).then(r => r.json());
    renderFL(s);
    if (s.status === 'training') flPoll();
    return s;
  } catch (e) { return null; }
}

function flPoll() {
  if (FL.timer) return;
  FL.timer = setInterval(async () => {
    const s = await loadFLStatus();
    if (!s || s.status !== 'training') { clearInterval(FL.timer); FL.timer = null; }
  }, 800);
}

async function startFL() {
  const clamp = (id, lo, hi, def) => { const v = parseFloat($fl(id).value); const c = Number.isNaN(v) ? def : Math.min(hi, Math.max(lo, v)); if (c !== v) $fl(id).value = c; return c; };
  const n_rounds = Math.round(clamp('fl-rounds', 2, 50, 10));
  const n_ponds  = Math.round(clamp('fl-ponds', 2, 11, 8));
  const dp_noise = clamp('fl-dp', 0, 2, 0);
  FL.total = n_rounds;
  flSetButton('running');
  // react at once: the first run after a server start needs a few seconds to load the pond data
  $fl('fl-message').hidden = true;
  $fl('fl-contrib').hidden = true;  $fl('fl-contrib-empty').hidden = false;
  $fl('fl-chart-empty').hidden = false;
  flDrawChart([]);
  $fl('fl-status-section').hidden = false;
  $fl('fl-round-label').textContent = `0 / ${n_rounds}`;
  $fl('fl-progress-bar').style.width = '0%';
  $fl('fl-rmse').textContent = '-'; $fl('fl-r2').textContent = '-';
  try {
    const res = await fetch(`${API}/api/federated/train`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ n_rounds, n_ponds, dp_noise }) });
    const j = await res.json();
    if (!res.ok || j.started === false) throw new Error(j.message || j.detail || 'Training could not start.');
  } catch (e) {
    flMessage('bad', 'Training could not start', [`<p>${e.message}</p>`]);
    flSetButton('start');
    return;
  }
  flPoll();
}

// ─── Boot ────────────────────────────────────────────────────
async function boot() {
  await loadOverview();
  loadTrend();
}

boot();
// Auto-refresh the Overview every 30 seconds
setInterval(() => {
  if (document.getElementById('page-home').classList.contains('active')) loadOverview();
}, 30000);
