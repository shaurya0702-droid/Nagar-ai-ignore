/* ═══════════════════════════════════════════════════════════════════════════
   NagarAI — Charts Module (Chart.js)
   ═══════════════════════════════════════════════════════════════════════════ */

const CHART_COLORS = {
  critical : '#ef4444',
  high     : '#f97316',
  medium   : '#eab308',
  low      : '#22c55e',
  amber    : '#f59e0b',
  amberLt  : '#fbbf24',
  blue     : '#3b82f6',
  purple   : '#8b5cf6',
  gridLine : 'rgba(248,250,252,0.05)',
  text     : '#94a3b8',
  border   : 'rgba(148,163,184,0.1)',
};

/* Shared dark base options ─────────────────────────────────────────────────── */
const BASE_OPTS = {
  responsive : true,
  maintainAspectRatio: false,
  plugins: {
    legend: { labels: { color: CHART_COLORS.text, font: { family: 'DM Sans', size: 12 }, boxWidth: 12, padding: 16 } },
    tooltip: {
      backgroundColor: '#0d1b35',
      borderColor     : 'rgba(245,158,11,0.25)',
      borderWidth     : 1,
      titleColor      : '#f59e0b',
      bodyColor       : '#94a3b8',
      padding         : 12,
      cornerRadius    : 8,
    },
  },
  scales: {
    x: {
      ticks : { color: CHART_COLORS.text, font: { family: 'DM Sans', size: 11 } },
      grid  : { color: CHART_COLORS.gridLine },
    },
    y: {
      ticks : { color: CHART_COLORS.text, font: { family: 'DM Sans', size: 11 } },
      grid  : { color: CHART_COLORS.gridLine },
    },
  },
};

/* Track instances so we can destroy before re-render ───────────────────────── */
const chartInstances = {};

function destroyChart(id) {
  if (chartInstances[id]) {
    chartInstances[id].destroy();
    delete chartInstances[id];
  }
}

/* ── 1. Ward Bar Chart (horizontal) ─────────────────────────────────────────── */
function renderWardBarChart(data, canvasId) {
  destroyChart(canvasId);
  const canvas = document.getElementById(canvasId);
  if (!canvas) return;

  const labels = Object.keys(data);
  const values = Object.values(data);

  chartInstances[canvasId] = new Chart(canvas, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label     : 'Complaints',
        data      : values,
        backgroundColor: labels.map((_, i) => `rgba(245,158,11,${0.5 + i * 0.06})`),
        borderColor    : CHART_COLORS.amber,
        borderWidth    : 1,
        borderRadius   : 4,
      }],
    },
    options: {
      ...BASE_OPTS,
      indexAxis: 'y',
      plugins: { ...BASE_OPTS.plugins, legend: { display: false } },
      scales: {
        x: { ...BASE_OPTS.scales.x, beginAtZero: true, ticks: { ...BASE_OPTS.scales.x.ticks, precision: 0 } },
        y: { ...BASE_OPTS.scales.y },
      },
    },
  });
}

/* ── 2. Daily Trend Line Chart ───────────────────────────────────────────────── */
function renderDailyTrendChart(data, canvasId) {
  destroyChart(canvasId);
  const canvas = document.getElementById(canvasId);
  if (!canvas) return;

  chartInstances[canvasId] = new Chart(canvas, {
    type: 'line',
    data: {
      labels  : data.map(d => d.day),
      datasets: [{
        label          : 'Complaints Filed',
        data           : data.map(d => d.count),
        borderColor    : CHART_COLORS.amber,
        backgroundColor: 'rgba(245,158,11,0.08)',
        pointBackgroundColor: CHART_COLORS.amber,
        pointBorderColor    : CHART_COLORS.amberLt,
        pointRadius    : 5,
        pointHoverRadius: 7,
        borderWidth    : 2,
        fill           : true,
        tension        : 0.4,
      }],
    },
    options: {
      ...BASE_OPTS,
      plugins: { ...BASE_OPTS.plugins, legend: { display: false } },
      scales: {
        x: { ...BASE_OPTS.scales.x },
        y: { ...BASE_OPTS.scales.y, beginAtZero: true, ticks: { ...BASE_OPTS.scales.y.ticks, precision: 0 } },
      },
    },
  });
}

/* ── 3. Priority Doughnut ────────────────────────────────────────────────────── */
function renderPriorityDoughnut(data, canvasId) {
  destroyChart(canvasId);
  const canvas = document.getElementById(canvasId);
  if (!canvas) return;

  const labels = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'];
  const colors = [CHART_COLORS.critical, CHART_COLORS.high, CHART_COLORS.medium, CHART_COLORS.low];

  chartInstances[canvasId] = new Chart(canvas, {
    type: 'doughnut',
    data: {
      labels,
      datasets: [{
        data           : labels.map(l => data[l] || 0),
        backgroundColor: colors.map(c => c + 'cc'),
        borderColor    : colors,
        borderWidth    : 2,
        hoverOffset    : 6,
      }],
    },
    options: {
      ...BASE_OPTS,
      cutout: '68%',
      scales: {},
      plugins: {
        ...BASE_OPTS.plugins,
        legend: { ...BASE_OPTS.plugins.legend, position: 'right' },
      },
    },
  });
}

/* ── 4. Escalation vs Resolution (2-line) ────────────────────────────────────── */
function renderEscalationChart(data, canvasId) {
  destroyChart(canvasId);
  const canvas = document.getElementById(canvasId);
  if (!canvas) return;

  chartInstances[canvasId] = new Chart(canvas, {
    type: 'line',
    data: {
      labels  : data.map(d => d.day),
      datasets: [
        {
          label          : 'Escalated',
          data           : data.map(d => d.escalated),
          borderColor    : CHART_COLORS.critical,
          backgroundColor: 'rgba(239,68,68,0.08)',
          pointBackgroundColor: CHART_COLORS.critical,
          borderWidth    : 2,
          fill           : true,
          tension        : 0.4,
        },
        {
          label          : 'Resolved',
          data           : data.map(d => d.resolved),
          borderColor    : CHART_COLORS.low,
          backgroundColor: 'rgba(34,197,94,0.08)',
          pointBackgroundColor: CHART_COLORS.low,
          borderWidth    : 2,
          fill           : true,
          tension        : 0.4,
        },
      ],
    },
    options: {
      ...BASE_OPTS,
      scales: {
        x: { ...BASE_OPTS.scales.x },
        y: { ...BASE_OPTS.scales.y, beginAtZero: true, ticks: { ...BASE_OPTS.scales.y.ticks, precision: 0 } },
      },
    },
  });
}

/* ── 5. Response Time Bar Chart (blue) ───────────────────────────────────────── */
function renderResponseTimeChart(data, canvasId) {
  destroyChart(canvasId);
  const canvas = document.getElementById(canvasId);
  if (!canvas) return;

  const labels = Object.keys(data);
  const values = Object.values(data);

  chartInstances[canvasId] = new Chart(canvas, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label          : 'Avg Response (hrs)',
        data           : values,
        backgroundColor: 'rgba(59,130,246,0.5)',
        borderColor    : CHART_COLORS.blue,
        borderWidth    : 1,
        borderRadius   : 4,
      }],
    },
    options: {
      ...BASE_OPTS,
      plugins: { ...BASE_OPTS.plugins, legend: { display: false } },
      scales: {
        x: { ...BASE_OPTS.scales.x },
        y: { ...BASE_OPTS.scales.y, beginAtZero: true },
      },
    },
  });
}

/* ── 6. Category Horizontal Bar ──────────────────────────────────────────────── */
function renderCategoryChart(data, canvasId) {
  destroyChart(canvasId);
  const canvas = document.getElementById(canvasId);
  if (!canvas) return;

  const palette = [
    CHART_COLORS.critical, CHART_COLORS.high, CHART_COLORS.medium,
    CHART_COLORS.blue, CHART_COLORS.purple, CHART_COLORS.low,
  ];

  chartInstances[canvasId] = new Chart(canvas, {
    type: 'bar',
    data: {
      labels  : Object.keys(data),
      datasets: [{
        label          : 'Complaints',
        data           : Object.values(data),
        backgroundColor: Object.keys(data).map((_, i) => palette[i % palette.length] + 'bb'),
        borderColor    : Object.keys(data).map((_, i) => palette[i % palette.length]),
        borderWidth    : 1,
        borderRadius   : 4,
      }],
    },
    options: {
      ...BASE_OPTS,
      indexAxis: 'y',
      plugins: { ...BASE_OPTS.plugins, legend: { display: false } },
      scales: {
        x: { ...BASE_OPTS.scales.x, beginAtZero: true, ticks: { ...BASE_OPTS.scales.x.ticks, precision: 0 } },
        y: { ...BASE_OPTS.scales.y },
      },
    },
  });
}

/* ── Score progress bar animation ────────────────────────────────────────────── */
function animateScoreBar(elementId, score, max = 10) {
  const el = document.getElementById(elementId);
  if (!el) return;
  el.style.width = '0%';
  requestAnimationFrame(() => {
    setTimeout(() => {
      el.style.width = ((score / max) * 100) + '%';
    }, 80);
  });
}

/* ── Generic counter animation ───────────────────────────────────────────────── */
function animateCounter(element, targetValue, duration = 1500) {
  if (!element) return;
  const start     = performance.now();
  const startVal  = 0;

  function step(now) {
    const elapsed  = now - start;
    const progress = Math.min(elapsed / duration, 1);
    const eased    = 1 - Math.pow(1 - progress, 3); // ease-out cubic
    const current  = Math.round(startVal + (targetValue - startVal) * eased);
    element.textContent = current.toLocaleString();
    if (progress < 1) requestAnimationFrame(step);
  }

  requestAnimationFrame(step);
}
