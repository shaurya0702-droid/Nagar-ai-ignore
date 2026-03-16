/* ═══════════════════════════════════════════════════════════════════════════
   NagarAI — Dashboard Controller
   ═══════════════════════════════════════════════════════════════════════════ */

let currentTab         = 'overview';
let allComplaints      = [];
let filteredComplaints = [];
let currentFilters     = { ward: '', priority: '', status: '', search: '' };
let autoRefreshInterval = null;
let emergencyMode      = false;
let currentModalId     = null;
let analyticsCache     = null;

/* ══════════════════════════════════════════════════════════════════════════════
   TAB SWITCHING
   ══════════════════════════════════════════════════════════════════════════════ */

function switchTab(tabName) {
  // Hide all panels
  document.querySelectorAll('.dashboard-panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.sidebar-nav-item').forEach(i => i.classList.remove('active'));

  // Show target panel
  const panel = document.getElementById('panel-' + tabName);
  if (panel) panel.classList.add('active');

  // Highlight sidebar item
  const navItem = document.querySelector(`[data-tab="${tabName}"]`);
  if (navItem) navItem.classList.add('active');

  // Update topbar title
  const titles = {
    overview    : '📊 Command Overview',
    complaints  : '🗂️ Complaints Management',
    analytics   : '📈 Analytics & Trends',
    heatmap     : '🗺️ Ward Heatmap',
    intelligence: '🧭 City Intelligence',
    settings    : '⚙️ Settings',
  };
  const titleEl = document.getElementById('panel-title');
  if (titleEl) titleEl.textContent = titles[tabName] || tabName;

  currentTab = tabName;

  // Lazy-load per tab
  if (tabName === 'complaints')   loadComplaints();
  if (tabName === 'analytics')    loadAnalytics();
  if (tabName === 'heatmap')      loadHeatmap();
  if (tabName === 'intelligence') loadIntelligence();
  if (tabName === 'settings')     initSettings();
}

/* ══════════════════════════════════════════════════════════════════════════════
   OVERVIEW TAB
   ══════════════════════════════════════════════════════════════════════════════ */

async function loadOverview() {
  try {
    const [stats, analytics] = await Promise.all([API.getStats(), API.getAnalytics()]);
    analyticsCache = analytics;

    renderStatsCards(stats);
    renderOverviewCharts(analytics);
    renderSLABreaches(analytics.sla_breaches || []);
    renderCityRecommendation(analytics.city_recommendation);
    checkEmergencyBanner(stats);
    checkSpike(analytics.spike_detection);
    renderIncidentClusters(analytics.incident_clusters || []);
  } catch (err) {
    console.error('Overview load error:', err);
    showToast('Failed to load overview data', 'error');
  }
}

function renderStatsCards(stats) {
  const map = {
    'stat-total'      : stats.total            || 0,
    'stat-critical'   : stats.critical          || 0,
    'stat-high'       : stats.high              || 0,
    'stat-medium'     : stats.medium            || 0,
    'stat-low'        : stats.low               || 0,
    'stat-sla'        : stats.sla_breached       || 0,
  };
  for (const [id, val] of Object.entries(map)) {
    const el = document.getElementById(id);
    if (el) animateCounter(el, val);
  }
}

function renderOverviewCharts(analytics) {
  renderWardBarChart(analytics.complaints_per_ward  || {}, 'ov-ward-chart');
  renderDailyTrendChart(analytics.daily_trend       || [], 'ov-trend-chart');
  renderPriorityDoughnut(analytics.priority_distribution || {}, 'ov-priority-chart');
}

function renderSLABreaches(breaches) {
  const container = document.getElementById('sla-breach-list');
  if (!container) return;

  if (!breaches || breaches.length === 0) {
    container.innerHTML = '<p style="color:var(--green-low);font-size:13px;padding:12px;">✅ No active SLA breaches</p>';
    return;
  }

  container.innerHTML = breaches.map(b => `
    <div class="sla-item">
      <div class="sla-item-left">
        <div class="cid">${b.complaint_id}</div>
        <div class="cat">${b.ward_name} — ${b.category}</div>
      </div>
      <div class="sla-item-right">
        <div class="elapsed">${b.time_elapsed_hours}h elapsed</div>
        <div class="allowed">SLA: ${b.sla_hours}h</div>
      </div>
    </div>
  `).join('');
}


/* ── buildRecommendationCard — renders amber-bordered AI rec card in modal ── */
function buildRecommendationCard(rec) {
  if (!rec) return '';
  const urgencyClass = rec.urgency || 'WITHIN_48H';
  const urgencyLabel = {
    IMMEDIATE:  '🚨 Immediate',
    SAME_DAY:   '⚡ Same Day',
    WITHIN_24H: '🕐 Within 24h',
    WITHIN_48H: '📅 Within 48h'
  }[urgencyClass] || urgencyClass;

  return `
    <div class="ai-recommendation-card">
      <div class="ai-recommendation-header">
        <span class="ai-recommendation-icon">🧭</span>
        <span class="ai-recommendation-title">AI Recommendation</span>
        <span class="ai-urgency-badge ${urgencyClass}" style="margin-left:auto;">${urgencyLabel}</span>
      </div>
      <div class="ai-recommendation-body">
        <div class="ai-rec-row">
          <span class="ai-rec-label">Action</span>
          <span class="ai-rec-value action">${rec.action || '—'}</span>
        </div>
        <div class="ai-rec-row">
          <span class="ai-rec-label">Reason</span>
          <span class="ai-rec-value">${rec.reason || '—'}</span>
        </div>
        <div class="ai-rec-row">
          <span class="ai-rec-label">Impact</span>
          <span class="ai-rec-value impact">${rec.impact || '—'}</span>
        </div>
        <div class="ai-rec-row">
          <span class="ai-rec-label">Authority</span>
          <span class="ai-rec-value authority">${rec.authority || '—'}</span>
        </div>
        ${rec.ai_summary ? `<div class="ai-rec-row"><span class="ai-rec-label">Summary</span><span class="ai-rec-value" style="font-style:italic;color:var(--text-secondary);">${rec.ai_summary}</span></div>` : ''}
      </div>
    </div>
  `;
}

function renderCityRecommendation(cityRec) {
  // Support both IDs: original city-rec-panel and new city-recommendation-panel
  const container = document.getElementById('city-recommendation-panel')
                 || document.getElementById('city-rec-panel');
  if (!container || !cityRec) return;

  const healthColors = {
    'Excellent':     '#22c55e',
    'Good':          '#3b82f6',
    'Moderate Risk': '#eab308',
    'High Risk':     '#f97316',
    'Critical':      '#ef4444'
  };
  const healthColor = healthColors[cityRec.city_health_label]
    || (cityRec.city_health_index >= 0.85 ? '#22c55e'
      : cityRec.city_health_index >= 0.70 ? '#3b82f6'
      : cityRec.city_health_index >= 0.55 ? '#eab308'
      : cityRec.city_health_index >= 0.40 ? '#f97316' : '#ef4444');
  const healthPct = Math.round((cityRec.city_health_index || 0) * 100);

  const deploymentRows = (cityRec.resource_deployment_plan || []).map(item => `
    <tr>
      <td><span style="color:#3b82f6;">${item.team || '—'}</span></td>
      <td>${item.ward || '—'}</td>
      <td style="color:#e2e8f0;">${item.action || '—'}</td>
    </tr>
  `).join('');

  container.innerHTML = `
    <div class="city-rec-panel">
      <h3>🧭 AI City Command Recommendation</h3>
      <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px;margin-bottom:20px;">
        <div style="background:rgba(245,158,11,0.08);border:1px solid rgba(245,158,11,0.2);border-radius:8px;padding:14px;">
          <div style="font-size:11px;color:#64748b;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:4px;">City Health Index</div>
          <div style="font-size:22px;font-weight:700;color:${healthColor};font-family:'Syne',sans-serif;">${healthPct}%</div>
          <div style="font-size:12px;color:${healthColor};margin-top:2px;">${cityRec.city_health_label || ''}</div>
          <div style="background:rgba(255,255,255,0.06);border-radius:100px;height:6px;overflow:hidden;margin-top:8px;">
            <div style="height:100%;width:${healthPct}%;background:linear-gradient(90deg,#ef4444,#eab308,#22c55e);border-radius:100px;transition:width 1.5s;"></div>
          </div>
        </div>
        <div style="background:rgba(239,68,68,0.08);border:1px solid rgba(239,68,68,0.2);border-radius:8px;padding:14px;">
          <div style="font-size:11px;color:#64748b;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:4px;">Citizens at Risk</div>
          <div style="font-size:22px;font-weight:700;color:#ef4444;font-family:'Syne',sans-serif;">${cityRec.total_citizens_at_risk ? cityRec.total_citizens_at_risk.toLocaleString() : '—'}</div>
          <div style="font-size:12px;color:#64748b;margin-top:2px;">Estimated affected</div>
        </div>
        <div style="background:rgba(59,130,246,0.08);border:1px solid rgba(59,130,246,0.2);border-radius:8px;padding:14px;">
          <div style="font-size:11px;color:#64748b;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:4px;">Top Priority Zone</div>
          <div style="font-size:22px;font-weight:700;color:#3b82f6;font-family:'Syne',sans-serif;">${cityRec.top_priority_ward || '—'}</div>
          <div style="font-size:12px;color:#64748b;margin-top:2px;">Highest risk locality</div>
        </div>
      </div>
      <div style="background:rgba(245,158,11,0.06);border:1px solid rgba(245,158,11,0.15);border-radius:8px;padding:14px;margin-bottom:20px;">
        <div style="font-size:11px;color:#64748b;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:6px;">⚡ Priority Action</div>
        <div style="font-size:14px;color:#f8fafc;font-weight:500;">${cityRec.top_priority_action || 'No action required'}</div>
      </div>
      <div>
        <div style="font-size:11px;color:#64748b;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:10px;">📋 Resource Deployment Plan</div>
        <table class="deployment-table">
          <thead><tr><th>Department</th><th>Locality</th><th>Action</th></tr></thead>
          <tbody>${deploymentRows || '<tr><td colspan="3" style="color:#64748b;text-align:center;">No deployment plan available</td></tr>'}</tbody>
        </table>
      </div>
      <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;margin-top:16px;">
        <div class="citizens-risk" style="font-size:12px;color:var(--text-muted);">
          Transparency Score: <span style="color:var(--amber);font-weight:700;">${cityRec.transparency_score || 0}%</span>
        </div>
      </div>
    </div>
  `;
}

function checkEmergencyBanner(stats) {
  const banner = document.getElementById('emergency-banner');
  if (!banner) return;
  if ((stats.critical || 0) > 0) {
    banner.innerHTML = `
      🚨 ${stats.critical} CRITICAL COMPLAINT(S) ACTIVE — Immediate Response Required &nbsp;|&nbsp;
      ${stats.emergency_overrides || 0} Emergency Override(s) Active
      <button class="close-btn" onclick="document.getElementById('emergency-banner').classList.remove('visible')">✕</button>
    `;
    banner.classList.add('visible');
  } else {
    banner.classList.remove('visible');
  }
}

function checkSpike(spikeData) {
  const el = document.getElementById('spike-alert');
  if (!el) return;
  if (spikeData && spikeData.detected) {
    el.innerHTML = `<span class="spike-alert-icon">⚠️</span> Abnormal Complaint Spike Detected — <strong>${spikeData.ward}</strong>: ${spikeData.count} complaints in last 24h`;
    el.classList.add('visible');
  } else {
    el.classList.remove('visible');
  }
}

/* ── renderIncidentClusters — City Incident Intelligence Panel ───────────── */
function renderIncidentClusters(clusters) {
  // Support both container IDs: doc §22 spec (incident-alert-container) + our built ID
  const container = document.getElementById('incident-alert-container')
                 || document.getElementById('incident-clusters-panel');
  if (!container) return;

  if (!clusters || clusters.length === 0) {
    container.innerHTML = '';
    return;
  }

  // Only show HIGH and CRITICAL — filter noise
  const alertClusters = clusters.filter(c => {
    const sev = c.incident_severity || c.severity || '';
    return sev === 'CRITICAL' || sev === 'HIGH';
  });
  if (alertClusters.length === 0) { container.innerHTML = ''; return; }

  const severityBg = {
    CRITICAL: 'rgba(239,68,68,0.10)',
    HIGH:     'rgba(249,115,22,0.08)',
    MEDIUM:   'rgba(234,179,8,0.07)',
    LOW:      'rgba(34,197,94,0.06)',
  };
  const severityBorder = {
    CRITICAL: 'rgba(239,68,68,0.35)',
    HIGH:     'rgba(249,115,22,0.30)',
    MEDIUM:   'rgba(234,179,8,0.25)',
    LOW:      'rgba(34,197,94,0.20)',
  };
  const severityColor = {
    CRITICAL: '#ef4444',
    HIGH:     '#f97316',
    MEDIUM:   '#eab308',
    LOW:      '#22c55e',
  };

  const totalCitizens = alertClusters.reduce((s, c) =>
    s + (c.estimated_citizens || c.citizens_affected || 0), 0);

  container.innerHTML = `
    <div class="incident-clusters-wrapper">
      <div class="incident-clusters-header">
        <span class="incident-header-icon">🏙️</span>
        <div>
          <div class="incident-header-title">City Incident Intelligence</div>
          <div class="incident-header-sub">
            ${alertClusters.length} active incident cluster${alertClusters.length > 1 ? 's' : ''} detected
            &nbsp;·&nbsp; ~${totalCitizens.toLocaleString()} citizens potentially affected
          </div>
        </div>
        <span class="incident-live-badge">● LIVE</span>
      </div>

      <div class="incident-cards-grid">
        ${alertClusters.map(cluster => {
          const sev     = cluster.incident_severity || cluster.severity || 'HIGH';
          const citizens = cluster.estimated_citizens || cluster.citizens_affected || 0;
          const title   = cluster.alert_title    || 'Possible Urban Incident Detected';
          const subtitle= cluster.alert_subtitle || `${cluster.category} Cluster — ${cluster.ward}`;
          const cause   = cluster.possible_cause || '';
          const color   = severityColor[sev] || '#f97316';

          return `
          <div class="incident-card" style="
            background:${severityBg[sev] || severityBg.HIGH};
            border-color:${severityBorder[sev] || severityBorder.HIGH};
            border-left-color:${color};
          ">
            <div class="incident-card-top">
              <span class="incident-severity-icon">${cluster.severity_icon || '⚠️'}</span>
              <div class="incident-card-meta">
                <div class="incident-category">${cluster.category}</div>
                <div class="incident-ward">📍 ${cluster.ward}</div>
              </div>
              <span class="incident-severity-badge" style="
                background:${severityBg[sev] || severityBg.HIGH};
                color:${color};
                border-color:${severityBorder[sev] || severityBorder.HIGH};
              ">${sev}</span>
            </div>

            <div class="incident-stats-row">
              <div class="incident-stat">
                <div class="incident-stat-num" style="color:${color}">${cluster.count}</div>
                <div class="incident-stat-lbl">Reports</div>
              </div>
              <div class="incident-stat">
                <div class="incident-stat-num" style="color:#f59e0b">${citizens.toLocaleString()}+</div>
                <div class="incident-stat-lbl">Citizens Affected</div>
              </div>
              <div class="incident-stat">
                <div class="incident-stat-num" style="color:#94a3b8">
                  ${((cluster.avg_priority || 0) * 10).toFixed(1)}/10
                </div>
                <div class="incident-stat-lbl">Avg Priority</div>
              </div>
            </div>

            ${cause ? `
            <div class="incident-action" style="margin-bottom:8px;">
              <div class="incident-action-label">Possible Cause</div>
              <div class="incident-action-text" style="color:#94a3b8;">${cause}</div>
            </div>` : ''}

            <div class="incident-action">
              <div class="incident-action-label">⚡ Recommended Action</div>
              <div class="incident-action-text">${cluster.recommended_action || '—'}</div>
            </div>

            <div class="incident-dept">
              <span class="badge badge-dept">
                ${(cluster.department || 'General').replace(' Department','').replace(' Cell','').replace(' & Police Coordination','')}
              </span>
              ${cluster.has_emergency ? '<span class="badge badge-emergency" style="font-size:10px;">🚨 Emergency</span>' : ''}
            </div>
          </div>`;
        }).join('')}
      </div>
    </div>
  `;
}

/* ══════════════════════════════════════════════════════════════════════════════
   COMPLAINTS TAB
   ══════════════════════════════════════════════════════════════════════════════ */

async function loadComplaints() {
  try {
    allComplaints      = await API.getComplaints(currentFilters);
    filteredComplaints = [...allComplaints];
    renderComplaintsTable(filteredComplaints);
    updateFilterInfo(filteredComplaints.length, allComplaints.length);
  } catch (err) {
    console.error('Complaints load error:', err);
    showToast('Failed to load complaints', 'error');
  }
}

function renderComplaintsTable(complaints) {
  const tbody = document.getElementById('complaints-tbody');
  if (!tbody) return;

  if (!complaints || complaints.length === 0) {
    tbody.innerHTML = `<tr><td colspan="10" style="text-align:center;color:var(--text-muted);padding:40px;">No complaints found matching your filters.</td></tr>`;
    return;
  }

  tbody.innerHTML = complaints.map(c => {
    const priorityBadge = `<span class="badge badge-${c.priority_label.toLowerCase()}">${c.priority_label}</span>`;
    const statusClass   = c.status.toLowerCase().replace(/\s+/g, '');
    const statusBadge   = `<span class="badge badge-${statusClass}">${c.status}</span>`;
    const slaPct        = c.sla_hours ? Math.round((c.time_elapsed_hours / c.sla_hours) * 100) : 0;
    const slaColor      = c.sla_breached ? 'var(--red-critical)' : slaPct > 75 ? 'var(--orange-high)' : 'var(--text-muted)';
    const slaText       = `<span class="sla-cell ${c.sla_breached ? 'breached' : ''}">${c.time_elapsed_hours || 0}h/${c.sla_hours}h${c.sla_breached ? ' <span class="badge badge-sla">BREACH</span>' : ''}</span>`;
    const emergIcon     = c.emergency_override ? '<span class="emergency-icon" title="Emergency Override">🚨</span>' : '';
    const deptShort     = (c.department || 'General').replace(' Department', '').replace(' Cell', '').replace(' & Police Coordination', '');

    // Incident report count — show amber badge if 2+ citizens reported same incident
    const reportCount   = c.report_count || 1;
    const reportBadge   = reportCount > 1
      ? `<span class="report-count-badge" title="${reportCount} citizens reported this incident">👥 ${reportCount}</span>`
      : '';

    // Duplicate indicator
    const dupIcon = c.is_duplicate
      ? '<span style="font-size:10px;color:var(--text-muted);margin-left:4px;" title="Duplicate complaint">⧉</span>'
      : '';

    return `
      <tr class="${c.is_duplicate ? 'row-duplicate' : ''}">
        <td><span class="cid">${c.complaint_id}</span>${emergIcon}${dupIcon}</td>
        <td style="color:var(--amber);font-size:12px;font-weight:500;">${c.ward_name}</td>
        <td style="max-width:180px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:var(--text-primary);" title="${c.text}">${c.text}</td>
        <td><span style="font-size:12px;color:var(--text-secondary);">${c.category}</span></td>
        <td>${priorityBadge}${reportBadge}</td>
        <td>${statusBadge}</td>
        <td>${slaText}</td>
        <td><span class="badge badge-dept">${deptShort}</span></td>
        <td>
          <button class="btn btn-sm btn-secondary" onclick="openComplaintModal(${c.id})">View</button>
        </td>
      </tr>`;
  }).join('');
}

function filterComplaints() {
  currentFilters.ward     = document.getElementById('filter-ward')?.value     || '';
  currentFilters.priority = document.getElementById('filter-priority')?.value || '';
  currentFilters.status   = document.getElementById('filter-status')?.value   || '';
  currentFilters.search   = document.getElementById('filter-search')?.value   || '';

  filteredComplaints = allComplaints.filter(c => {
    if (currentFilters.ward     && c.ward_name    !== currentFilters.ward)                              return false;
    if (currentFilters.priority && c.priority_label !== currentFilters.priority.toUpperCase())          return false;
    if (currentFilters.status   && c.status !== currentFilters.status)                                  return false;
    if (currentFilters.search   && !c.text.toLowerCase().includes(currentFilters.search.toLowerCase())) return false;
    return true;
  });

  renderComplaintsTable(filteredComplaints);
  updateFilterInfo(filteredComplaints.length, allComplaints.length);
}

function updateFilterInfo(shown, total) {
  const el = document.getElementById('filter-info');
  if (el) el.textContent = `Showing ${shown} of ${total} complaints`;
}

/* ══════════════════════════════════════════════════════════════════════════════
   COMPLAINT MODAL
   ══════════════════════════════════════════════════════════════════════════════ */

async function openComplaintModal(id) {
  currentModalId = id;
  try {
    const c = await API.getComplaint(id);
    if (!c) { showToast('Complaint not found', 'error'); return; }

    // Header info
    setModalField('modal-cid',       c.complaint_id);
    setModalField('modal-ward',      c.ward_name);
    setModalField('modal-category',  c.category);
    setModalField('modal-dept',      c.department || 'General');
    setModalField('modal-status-lbl', c.status);
    setModalField('modal-text',      c.text);
    setModalField('modal-created',   c.created_at ? new Date(c.created_at).toLocaleString('en-IN') : 'N/A');

    // Priority badge
    const priEl = document.getElementById('modal-priority');
    if (priEl) priEl.innerHTML = `<span class="badge badge-${c.priority_label.toLowerCase()}">${c.priority_label}</span>`;

    // Score bars
    const sev  = parseFloat(c.severity_score)   || 0;
    const cred = parseFloat(c.credibility_score) || 0;
    const pri  = parseFloat(c.priority_score)    || 0;
    setModalField('modal-sev-val',  (sev  * 10).toFixed(1) + ' / 10');
    setModalField('modal-cred-val', (cred * 10).toFixed(1) + ' / 10');
    setModalField('modal-pri-val',  (pri  * 10).toFixed(1) + ' / 10');

    animateScoreBar('modal-sev-bar',  sev  * 10);
    animateScoreBar('modal-cred-bar', cred * 10);
    animateScoreBar('modal-pri-bar',  pri  * 10);

    // Keywords
    const kwEl = document.getElementById('modal-keywords');
    if (kwEl) {
      const kws = c.severity_keywords || [];
      kwEl.innerHTML = kws.length
        ? kws.map(k => `<span class="tag">${k}</span>`).join('')
        : '<span style="color:var(--text-muted);font-size:12px;">None detected</span>';
    }

    // Credibility features
    const featEl = document.getElementById('modal-features');
    if (featEl) {
      const feats = c.credibility_features || [];
      featEl.innerHTML = feats.length
        ? feats.map(f => `<span class="tag-gray">${f}</span>`).join('')
        : '<span style="color:var(--text-muted);font-size:12px;">None</span>';
    }

    // AI Recommendation
    const rec = c.ai_recommendation;
    if (rec) {
      const urgencyClass = (rec.urgency || '').toLowerCase() === 'immediate' ? 'immediate' : '';
      setModalHTML('modal-rec', `
        <div class="rec-card">
          <div class="rec-card-header">
            <span class="rec-card-icon">🧭</span>
            <span class="rec-card-title">AI Recommendation</span>
          </div>
          <div class="rec-grid">
            <div class="rec-field rec-action">
              <label>Action</label>
              <p>${rec.action || 'No action specified'}</p>
            </div>
            <div class="rec-field">
              <label>Reason</label>
              <p>${rec.reason || '—'}</p>
            </div>
            <div class="rec-field">
              <label>Impact</label>
              <p>${rec.impact || '—'}</p>
            </div>
          </div>
          <div style="display:flex;gap:12px;align-items:center;flex-wrap:wrap;margin-top:14px;">
            <div><label style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:var(--text-muted);display:block;margin-bottom:3px;">Authority</label>
            <span class="badge badge-dept">${rec.authority || '—'}</span></div>
            <div><label style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:var(--text-muted);display:block;margin-bottom:3px;">Urgency</label>
            <span class="urgency-badge ${urgencyClass}">${rec.urgency || '—'}</span></div>
          </div>
          ${rec.ai_summary ? `<div style="margin-top:14px;background:rgba(245,158,11,0.04);border-radius:var(--radius-sm);padding:12px;font-size:13px;color:var(--text-secondary);font-style:italic;">${rec.ai_summary}</div>` : ''}
        </div>
      `);
    }

    // Inject new animated AI recommendation card into modal-recommendation-container
    const recContainer = document.getElementById('modal-recommendation-container');
    if (recContainer) {
      let recData = c.ai_recommendation;
      if (typeof recData === 'string') {
        try { recData = JSON.parse(recData); } catch(e) { recData = null; }
      }
      recContainer.innerHTML = buildRecommendationCard(recData);
    }

    // Lifecycle stepper
    renderLifecycle(c.status);

    // Status select
    const sel = document.getElementById('status-select');
    if (sel) sel.value = c.status;

    // SLA info
    setModalField('modal-sla',
      `${c.time_elapsed_hours || 0}h elapsed / ${c.sla_hours}h allowed${c.sla_breached ? ' — <span style="color:var(--red-critical)">BREACHED</span>' : ''}`
    );

    // Duplicate + Incident Report Count
    const reportCount = c.report_count || 1;
    const reportImpact = reportCount >= 10
      ? Math.round(reportCount * 55) + '+'
      : reportCount >= 5
        ? Math.round(reportCount * 60) + '+'
        : reportCount >= 2
          ? Math.round(reportCount * 50) + '+'
          : null;

    if (c.is_duplicate) {
      setModalField('modal-dup', `<span class="badge badge-sla">⧉ Duplicate of ${c.duplicate_of || 'unknown'}</span>`);
    } else if (reportCount > 1) {
      setModalField('modal-dup', `
        <div style="background:rgba(245,158,11,0.08);border:1px solid rgba(245,158,11,0.25);border-radius:8px;padding:10px 14px;">
          <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px;">
            <span style="font-size:16px;">👥</span>
            <span style="font-weight:700;color:var(--amber);font-size:14px;">${reportCount} citizens reported this incident</span>
          </div>
          ${reportImpact ? `<div style="font-size:12px;color:var(--text-secondary);">Estimated ${reportImpact} residents affected</div>` : ''}
          <div style="font-size:11px;color:var(--text-muted);margin-top:4px;">Impact score: ${(reportCount * (c.priority_score || 0)).toFixed(2)} — crowd-verified incident</div>
        </div>
      `);
    } else {
      setModalField('modal-dup', '<span style="color:var(--green-low)">Not a duplicate — single report</span>');
    }

    // Emergency
    setModalField('modal-emergency', c.emergency_override
      ? '<span class="badge badge-emergency">🚨 Emergency Override Active</span>'
      : '<span style="color:var(--text-muted)">No override</span>');

    document.getElementById('complaint-modal').classList.add('open');
  } catch (err) {
    console.error('Modal error:', err);
    showToast('Failed to load complaint details', 'error');
  }
}

function renderLifecycle(currentStatus) {
  const steps = ['Submitted', 'Assigned', 'In Progress', 'Resolved'];
  const statusMap = { Pending: 0, Submitted: 0, Assigned: 1, 'In Progress': 2, Resolved: 3, Escalated: 2 };
  const currentIdx = statusMap[currentStatus] ?? 0;

  const el = document.getElementById('modal-lifecycle');
  if (!el) return;

  el.innerHTML = steps.map((step, i) => {
    const cls = i < currentIdx ? 'done' : i === currentIdx ? 'current' : '';
    const icon = i < currentIdx ? '✓' : i === currentIdx ? '●' : '○';
    return `
      ${i > 0 ? `<div class="step-line ${i <= currentIdx ? 'done' : ''}"></div>` : ''}
      <div class="step-item ${cls}">
        <div class="dot">${icon}</div>
        <div class="step-text">${step}</div>
      </div>
    `;
  }).join('');
}

function closeModal() {
  document.getElementById('complaint-modal')?.classList.remove('open');
  currentModalId = null;
}

async function updateComplaintStatus(complaintId) {
  const sel = document.getElementById('status-select');
  if (!sel) return;
  const newStatus = sel.value;
  try {
    await API.updateComplaint(complaintId, { status: newStatus });
    closeModal();
    loadComplaints();
    if (typeof refreshHeatmap === 'function') refreshHeatmap();
    showToast('✅ Status updated to: ' + newStatus);
  } catch (err) {
    showToast('Failed to update status', 'error');
  }
}

/* ══════════════════════════════════════════════════════════════════════════════
   ANALYTICS TAB
   ══════════════════════════════════════════════════════════════════════════════ */

async function loadAnalytics() {
  try {
    const analytics = await API.getAnalytics();
    analyticsCache  = analytics;

    renderWardBarChart    (analytics.complaints_per_ward         || {}, 'ward-chart');
    renderDailyTrendChart (analytics.daily_trend                 || [], 'trend-chart');
    renderPriorityDoughnut(analytics.priority_distribution       || {}, 'priority-chart');
    renderEscalationChart (analytics.escalation_vs_resolution    || [], 'escalation-chart');
    renderResponseTimeChart(analytics.avg_response_time_per_ward || {}, 'response-chart');
    renderCategoryChart   (analytics.category_distribution       || {}, 'category-chart');
  } catch (err) {
    console.error('Analytics load error:', err);
    showToast('Failed to load analytics', 'error');
  }
}

/* ══════════════════════════════════════════════════════════════════════════════
   HEATMAP TAB
   ══════════════════════════════════════════════════════════════════════════════ */

async function loadHeatmap() {
  try {
    const heatmapData = await API.getHeatmap();
    renderHeatmapCards(heatmapData);
    // Small delay so the map container is visible before Leaflet measures it
    setTimeout(() => {
      initHeatmap();
      renderHeatmapMarkers(heatmapData);
    }, 100);
  } catch (err) {
    console.error('Heatmap load failed:', err);
    showToast('Failed to load heatmap data', 'error');
  }
}

function renderHeatmapCards(wardData) {
  const container = document.getElementById('density-cards');
  if (!container) return;

  container.innerHTML = wardData.map(w => `
    <div class="density-card density-${w.density.toLowerCase()}">
      <div class="dc-name">${w.ward}</div>
      <div class="dc-count">${w.count}</div>
      <div class="dc-density">${w.density}</div>
      <div style="font-size:10px;color:var(--text-muted);margin-top:4px;">
        🚨${w.critical} ⚠️${w.high} 🟡${w.medium} ✅${w.low}
      </div>
    </div>
  `).join('');
}

/* ══════════════════════════════════════════════════════════════════════════════
   INTELLIGENCE TAB
   ══════════════════════════════════════════════════════════════════════════════ */

async function loadIntelligence() {
  try {
    const analytics = await API.getAnalytics();
    analyticsCache  = analytics;

    renderResponsibleAI   (analytics.responsible_ai || {});
    renderImpactSummary   (analytics.impact || {});
    renderKeywordFrequency(analytics.severity_keyword_frequency || {});
    renderWardRecommendations(analytics.city_recommendation?.recommendations || []);
    renderDeploymentPlan  (analytics.city_recommendation?.resource_deployment_plan || []);
  } catch (err) {
    console.error('Intelligence load error:', err);
    showToast('Failed to load intelligence data', 'error');
  }
}

function renderResponsibleAI(rai) {
  const el = document.getElementById('rai-panel');
  if (!el) return;

  el.innerHTML = `
    <div class="confidence-ring">
      <div>
        <div class="confidence-num">${rai.model_confidence || 92.4}%</div>
        <div class="confidence-label">Model Confidence</div>
      </div>
      <div class="ai-badges">
        ${rai.explainability_enabled ? '<span class="ai-badge">✓ Explainability Enabled</span>' : ''}
        ${rai.bias_detection_active  ? '<span class="ai-badge">✓ Bias Detection Active</span>' : ''}
        <span class="ai-badge">✓ False Positive Risk: ${rai.false_positive_risk || 'Low'}</span>
        <span class="ai-badge">✓ SHAP Explanations</span>
        <span class="ai-badge">✓ SLA Enforcement</span>
        <span class="ai-badge">✓ Emergency Override</span>
      </div>
    </div>
  `;
}

function renderImpactSummary(impact) {
  const el = document.getElementById('impact-panel');
  if (!el) return;

  el.innerHTML = `
    <div class="impact-grid">
      <div class="impact-card">
        <div class="impact-num">${(impact.citizens_served || 0).toLocaleString()}</div>
        <div class="impact-lbl">Citizens Served</div>
      </div>
      <div class="impact-card">
        <div class="impact-num">${impact.avg_resolution_hours || 0}h</div>
        <div class="impact-lbl">Avg Resolution</div>
      </div>
      <div class="impact-card">
        <div class="impact-num">${impact.high_risk_prevented || 0}</div>
        <div class="impact-lbl">High Risk Prevented</div>
      </div>
      <div class="impact-card">
        <div class="impact-num">${impact.emergency_auto_boosts || 0}</div>
        <div class="impact-lbl">Emergency Boosts</div>
      </div>
    </div>
  `;
}

function renderKeywordFrequency(kwData) {
  const el = document.getElementById('keyword-panel');
  if (!el) return;

  const maxVal = Math.max(...Object.values(kwData), 1);
  const sorted = Object.entries(kwData).sort((a, b) => b[1] - a[1]).slice(0, 12);

  el.innerHTML = `
    <div class="kw-list">
      ${sorted.map(([word, count]) => `
        <div class="kw-row">
          <span class="kw-word">${word}</span>
          <div class="kw-bar-wrap">
            <div class="kw-bar-fill" style="width:${(count / maxVal) * 100}%"></div>
          </div>
          <span class="kw-count">${count}</span>
        </div>
      `).join('')}
    </div>
  `;
}

function renderWardRecommendations(recommendations) {
  const el = document.getElementById('ward-recs-container');
  if (!el) return;

  if (!recommendations || recommendations.length === 0) {
    el.innerHTML = '<p style="color:var(--text-muted);font-size:13px;">No ward recommendations available.</p>';
    return;
  }

  el.innerHTML = `
    <div class="ward-recs-grid">
      ${recommendations.map(r => {
        const riskColor = r.risk_score >= 3 ? 'var(--red-critical)' : r.risk_score >= 2 ? 'var(--orange-high)' : 'var(--yellow-medium)';
        return `
          <div class="ward-rec-card">
            <div class="ward-rec-header">
              <span class="ward-rec-name">${r.ward}</span>
              <span class="ward-risk-score" style="background:rgba(255,255,255,0.04);border:1px solid ${riskColor};color:${riskColor};">Risk: ${r.risk_score}</span>
            </div>
            <div style="margin-bottom:10px;">${r.dominant_issue ? `<span class="badge badge-${r.risk_score >= 3 ? 'critical' : r.risk_score >= 2 ? 'high' : 'medium'}">${r.dominant_issue}</span>` : ''}</div>
            <div class="ward-rec-action">🎯 ${r.recommended_action}</div>
            <div class="ward-rec-reason">📋 ${r.reason}</div>
            ${r.priority_teams ? `
              <div style="margin-top:12px;display:flex;flex-wrap:wrap;gap:6px;">
                ${(r.priority_teams || []).map(t => `<span class="badge badge-dept">${t.replace(' Department', '').replace(' Cell', '')}</span>`).join('')}
              </div>
            ` : ''}
          </div>
        `;
      }).join('')}
    </div>
  `;
}

function renderDeploymentPlan(plan) {
  const el = document.getElementById('deployment-plan-container');
  if (!el) return;

  if (!plan || plan.length === 0) {
    el.innerHTML = '<p style="color:var(--text-muted);font-size:13px;">No deployment plan available.</p>';
    return;
  }

  el.innerHTML = `
    <div class="table-wrapper">
      <table class="deployment-table">
        <thead>
          <tr>
            <th>Team / Department</th>
            <th>Ward</th>
            <th>Recommended Action</th>
          </tr>
        </thead>
        <tbody>
          ${plan.map(p => `
            <tr>
              <td><span class="badge badge-dept">${p.team}</span></td>
              <td style="color:var(--amber);font-weight:600;">${p.ward}</td>
              <td style="color:var(--text-secondary);">${p.action}</td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    </div>
  `;
}

/* ══════════════════════════════════════════════════════════════════════════════
   SETTINGS TAB
   ══════════════════════════════════════════════════════════════════════════════ */

function initSettings() {
  const toggle = document.getElementById('emergency-toggle');
  if (toggle) {
    toggle.checked = emergencyMode;
    toggle.addEventListener('change', async (e) => {
      emergencyMode = e.target.checked;
      try {
        const result = await API.setEmergencyMode(emergencyMode);
        updateEmergencyModeDisplay();
        showToast(result.message || (emergencyMode ? '🚨 Emergency Mode Activated' : '✅ Normal Mode Restored'),
                  emergencyMode ? 'warning' : 'success');
      } catch (err) {
        showToast('Failed to toggle emergency mode', 'error');
      }
    });
  }

  const recalcBtn = document.getElementById('recalc-btn');
  if (recalcBtn) {
    recalcBtn.addEventListener('click', async () => {
      recalcBtn.disabled   = true;
      recalcBtn.textContent = '⟳ Recalculating…';
      try {
        const result = await API.recalculate();
        showToast(`✅ Recalculated ${result.updated_count || 0} complaints`);
        loadComplaints();
      } catch (err) {
        showToast('Recalculation failed', 'error');
      } finally {
        recalcBtn.disabled   = false;
        recalcBtn.textContent = '⟳ Recalculate All Complaints';
      }
    });
  }

  // Display current weights
  updateEmergencyModeDisplay();
}

function updateEmergencyModeDisplay() {
  const pillEl   = document.getElementById('emergency-mode-pill');
  const weightEl = document.getElementById('weight-display');
  const modeEl   = document.getElementById('mode-label');

  if (pillEl) {
    pillEl.classList.toggle('active', emergencyMode);
    pillEl.textContent = emergencyMode ? '🚨 EMERGENCY MODE ON' : '';
  }
  if (weightEl) {
    weightEl.textContent = emergencyMode
      ? 'Weights: 0.8 × Severity + 0.2 × Credibility'
      : 'Weights: 0.6 × Severity + 0.4 × Credibility';
  }
  if (modeEl) {
    modeEl.textContent = emergencyMode ? '🚨 Emergency Mode' : '✅ Normal Mode';
    modeEl.style.color = emergencyMode ? 'var(--red-critical)' : 'var(--green-low)';
  }
}

/* ══════════════════════════════════════════════════════════════════════════════
   UTILITIES
   ══════════════════════════════════════════════════════════════════════════════ */

function showToast(message, type = 'success') {
  const container = document.getElementById('toast-container');
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.textContent = message;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity   = '0';
    toast.style.transform = 'translateX(20px)';
    toast.style.transition = 'all 0.3s';
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

function startAutoRefresh() {
  if (autoRefreshInterval) clearInterval(autoRefreshInterval);
  autoRefreshInterval = setInterval(() => {
    if (currentTab === 'overview') loadOverview();
  }, 30000);
}

function stopAutoRefresh() {
  if (autoRefreshInterval) {
    clearInterval(autoRefreshInterval);
    autoRefreshInterval = null;
  }
}

function updateClock() {
  const el = document.getElementById('system-time');
  if (!el) return;
  const now = new Date();
  el.textContent = now.toLocaleString('en-IN', { hour12: false, dateStyle: 'short', timeStyle: 'medium' });
}

/* DOM helpers */
function setModalField(id, value) {
  const el = document.getElementById(id);
  if (el) el.textContent = value;
}
function setModalHTML(id, html) {
  const el = document.getElementById(id);
  if (el) el.innerHTML = html;
}

/* ══════════════════════════════════════════════════════════════════════════════
   INIT
   ══════════════════════════════════════════════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', async () => {
  requireAuth();
  displayOfficerInfo();

  // Sidebar navigation
  document.querySelectorAll('.sidebar-nav-item').forEach(item => {
    item.addEventListener('click', () => switchTab(item.dataset.tab));
  });

  // Mobile sidebar toggle
  const hamburger = document.getElementById('sidebar-toggle');
  if (hamburger) {
    hamburger.addEventListener('click', () => {
      document.querySelector('.sidebar')?.classList.toggle('open');
    });
  }

  // Close modal on overlay click
  const modal = document.getElementById('complaint-modal');
  if (modal) {
    modal.addEventListener('click', (e) => {
      if (e.target === modal) closeModal();
    });
  }

  // Clock
  updateClock();
  setInterval(updateClock, 1000);

  // Load first tab
  await loadOverview();
  startAutoRefresh();
});
