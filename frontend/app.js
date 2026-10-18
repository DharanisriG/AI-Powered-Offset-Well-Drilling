/**
 * Drilling AI — Frontend Application Logic
 * Integrates with FastAPI Backend:
 * - GET  /api/health
 * - GET  /api/wells
 * - GET  /api/wells/{well_id}
 * - GET  /api/wells/{well_id}/events
 * - POST /api/similar-wells
 * - POST /api/experience-search
 */

const API_BASE = window.location.port === '8000' ? '' : 'http://127.0.0.1:8000';

// Preset Scenarios for Rapid Hackathon Evaluation
const SCENARIO_PRESETS = {
  'tapti-gas': {
    well_id: 'NWIS-X1',
    field: 'Tapti',
    formation: 'Daman Sandstone',
    total_depth: 3020.0,
    current_depth: 2780.0,
    mud_weight: 12.9,
    pressure: 5520.0,
    rop: 22.0,
    wob: 22.0,
    torque: 15.8,
    inclination: 37.0,
    azimuth: 143.0
  },
  'mumbai-loss': {
    well_id: 'NWIS-X2',
    field: 'Mumbai Offshore',
    formation: 'Bassein Limestone',
    total_depth: 3480.0,
    current_depth: 2980.0,
    mud_weight: 11.3,
    pressure: 4280.0,
    rop: 12.2,
    wob: 16.2,
    torque: 13.7,
    inclination: 14.8,
    azimuth: 211.0
  },
  'mukta-shale': {
    well_id: 'NWIS-X3',
    field: 'Mukta',
    formation: 'Mukta Shale',
    total_depth: 2520.0,
    current_depth: 2180.0,
    mud_weight: 10.7,
    pressure: 3190.0,
    rop: 8.0,
    wob: 14.2,
    torque: 18.2,
    inclination: 31.0,
    azimuth: 182.0
  },
  'ratna-sticking': {
    well_id: 'NWIS-X4',
    field: 'Ratna',
    formation: 'Chattrabuj Sand',
    total_depth: 2480.0,
    current_depth: 2280.0,
    mud_weight: 12.2,
    pressure: 3420.0,
    rop: 17.0,
    wob: 19.0,
    torque: 15.0,
    inclination: 39.0,
    azimuth: 235.0
  }
};

// Application State
const state = {
  currentWell: { ...SCENARIO_PRESETS['tapti-gas'] },
  activeTab: 'dashboard',
  similarWells: [],
  experienceData: null,
  selectedExperienceWellId: null,
  offsetWells: [],
  offsetFilteredWells: [],
  offsetCurrentPage: 1,
  offsetPageSize: 15,
  isBackendHealthy: false
};

// ---------------- DOM References ----------------
const elements = {
  statusDot: document.getElementById('status-dot'),
  statusText: document.getElementById('status-text'),
  datasetMeta: document.getElementById('dataset-meta'),
  connectionAlert: document.getElementById('connection-alert'),
  pageTitle: document.getElementById('page-title'),
  pageSubtitle: document.getElementById('page-subtitle'),

  // Navigation
  navButtons: document.querySelectorAll('.nav-item'),
  tabPanes: document.querySelectorAll('.tab-pane'),

  // Dashboard elements
  dashWellId: document.getElementById('dash-well-id'),
  dashDepth: document.getElementById('dash-depth'),
  dashFormation: document.getElementById('dash-formation'),
  dashField: document.getElementById('dash-field'),
  dashMw: document.getElementById('dash-mw'),
  dashPress: document.getElementById('dash-press'),
  dashSimilarList: document.getElementById('dash-similar-list'),
  dashSimilarLoading: document.getElementById('dash-similar-loading'),
  btnEditWell: document.getElementById('btn-edit-well'),
  dashRefreshSimilar: document.getElementById('dash-refresh-similar'),

  // Current Well Form
  wellForm: document.getElementById('well-form'),
  scenarioPreset: document.getElementById('scenario-preset'),
  inputWellId: document.getElementById('input-well-id'),
  inputField: document.getElementById('input-field'),
  inputFormation: document.getElementById('input-formation'),
  inputTotalDepth: document.getElementById('input-total-depth'),
  inputCurrentDepth: document.getElementById('input-current-depth'),
  inputInclination: document.getElementById('input-inclination'),
  inputAzimuth: document.getElementById('input-azimuth'),
  inputMudWeight: document.getElementById('input-mud-weight'),
  inputPressure: document.getElementById('input-pressure'),
  inputRop: document.getElementById('input-rop'),
  inputWob: document.getElementById('input-wob'),
  inputTorque: document.getElementById('input-torque'),
  currentWellResults: document.getElementById('current-well-results'),
  currentWellMatches: document.getElementById('current-well-matches'),
  matchExplanation: document.getElementById('match-explanation'),

  // Offset Wells Page
  offsetSearch: document.getElementById('offset-search'),
  offsetFieldFilter: document.getElementById('offset-field-filter'),
  offsetWellsTbody: document.getElementById('offset-wells-tbody'),
  offsetLoading: document.getElementById('offset-loading'),
  paginationInfo: document.getElementById('pagination-info'),
  btnPrevPage: document.getElementById('btn-prev-page'),
  btnNextPage: document.getElementById('btn-next-page'),

  // Historical Experience Page
  expCurrentWellId: document.getElementById('exp-current-well-id'),
  expCurrentLocation: document.getElementById('exp-current-location'),
  expCurDepth: document.getElementById('exp-cur-depth'),
  expCurMw: document.getElementById('exp-cur-mw'),
  expCurPress: document.getElementById('exp-cur-press'),
  expCurRop: document.getElementById('exp-cur-rop'),
  expPrecedentToggle: document.getElementById('exp-precedent-toggle'),
  expWellsSelector: document.getElementById('exp-wells-selector'),
  expMainCardContainer: document.getElementById('exp-main-card-container'),
  expOtherEventsContainer: document.getElementById('exp-other-events-container'),
  expSummaryText: document.getElementById('exp-summary-text'),
  experienceLoading: document.getElementById('experience-loading'),

  // Modal
  wellModal: document.getElementById('well-details-modal'),
  modalCloseBtn: document.getElementById('modal-close-btn'),
  modalFooterClose: document.getElementById('modal-footer-close'),
  modalWellId: document.getElementById('modal-well-id'),
  modalWellSub: document.getElementById('modal-well-sub'),
  modalWellInfo: document.getElementById('modal-well-info'),
  modalEventsTimeline: document.getElementById('modal-events-timeline'),
  modalLoading: document.getElementById('modal-loading')
};

// ---------------- Navigation ----------------
function switchTab(tabId) {
  state.activeTab = tabId;

  elements.navButtons.forEach(btn => {
    btn.classList.toggle('active', btn.dataset.tab === tabId);
  });

  elements.tabPanes.forEach(pane => {
    pane.classList.toggle('hidden', pane.id !== `tab-${tabId}`);
    pane.classList.toggle('active', pane.id === `tab-${tabId}`);
  });

  // Update Page Title and Subtitle
  const titles = {
    'dashboard': { title: 'Drilling AI', sub: 'Offset Well Experience & Decision Support' },
    'current-well': { title: 'Current Well Situation', sub: 'Active drilling envelope and parameter matching' },
    'offset-wells': { title: 'Offset Wells Catalog', sub: '500 Historical offset wells database' },
    'historical-experience': { title: 'Historical Drilling Experience', sub: 'Evidence-based mitigation retrieval and precedent analysis' }
  };
  elements.pageTitle.textContent = titles[tabId]?.title || 'Drilling AI';
  elements.pageSubtitle.textContent = titles[tabId]?.sub || '';

  // Trigger page-specific loads
  if (tabId === 'historical-experience') {
    loadHistoricalExperience();
  } else if (tabId === 'offset-wells' && state.offsetWells.length === 0) {
    loadOffsetWells();
  }
}

// ---------------- API Helpers ----------------
async function apiGet(endpoint) {
  try {
    const res = await fetch(`${API_BASE}${endpoint}`);
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    return await res.json();
  } catch (err) {
    console.error(`API Error on GET ${endpoint}:`, err);
    showConnectionError(true);
    throw err;
  }
}

async function apiPost(endpoint, payload) {
  try {
    const res = await fetch(`${API_BASE}${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    return await res.json();
  } catch (err) {
    console.error(`API Error on POST ${endpoint}:`, err);
    showConnectionError(true);
    throw err;
  }
}

function showConnectionError(isError) {
  elements.connectionAlert.classList.toggle('hidden', !isError);
  if (isError) {
    elements.statusDot.className = 'status-indicator error';
    elements.statusText.textContent = 'Disconnected';
  } else {
    elements.statusDot.className = 'status-indicator connected';
    elements.statusText.textContent = 'Connected (FastAPI)';
  }
}

// ---------------- Health Check ----------------
async function checkBackendHealth() {
  try {
    const data = await apiGet('/api/health');
    state.isBackendHealthy = (data.status === 'healthy');
    showConnectionError(false);
    elements.datasetMeta.textContent = `${data.wells_count} Wells | ${data.events_count} Events`;
  } catch {
    showConnectionError(true);
  }
}

// ---------------- Dashboard Page ----------------
function updateDashboardCurrentWellUI() {
  const w = state.currentWell;
  elements.dashWellId.textContent = w.well_id;
  elements.dashDepth.innerHTML = `${w.current_depth.toLocaleString('en-US', { minimumFractionDigits: 1 })} <small>m</small>`;
  elements.dashFormation.textContent = w.formation;
  elements.dashField.textContent = w.field;
  elements.dashMw.innerHTML = `${w.mud_weight.toFixed(1)} <small>ppg</small>`;
  elements.dashPress.innerHTML = `${Math.round(w.pressure).toLocaleString()} <small>psi</small>`;
}

async function loadDashboardSimilarWells() {
  elements.dashSimilarLoading.classList.remove('hidden');
  elements.dashSimilarList.innerHTML = '';

  try {
    const payload = {
      total_depth: state.currentWell.total_depth,
      mud_weight: state.currentWell.mud_weight,
      pressure: state.currentWell.pressure,
      rop: state.currentWell.rop,
      wob: state.currentWell.wob,
      torque: state.currentWell.torque,
      inclination: state.currentWell.inclination,
      azimuth: state.currentWell.azimuth,
      top_k: 3,
      current_depth: state.currentWell.current_depth
    };

    const res = await apiPost('/api/similar-wells', payload);
    state.similarWells = res.similar_wells;
    renderDashboardSimilarWells(res.similar_wells);
  } catch {
    elements.dashSimilarList.innerHTML = `
      <div class="state-container">
        <span>Unable to fetch similar wells from backend. Ensure backend is running.</span>
      </div>`;
  } finally {
    elements.dashSimilarLoading.classList.add('hidden');
  }
}

function renderDashboardSimilarWells(wells) {
  if (!wells || wells.length === 0) {
    elements.dashSimilarList.innerHTML = `
      <div class="state-container">
        <span>No similar wells found matching current parameters.</span>
      </div>`;
    return;
  }

  elements.dashSimilarList.innerHTML = wells.map(w => `
    <div class="similar-well-item">
      <div class="well-info-group">
        <span class="well-id-text">${escapeHtml(w.well_id)}</span>
        <span class="similarity-badge">${w.similarity}%</span>
        <span class="well-meta-tag">${escapeHtml(w.formation)}</span>
        <span class="well-meta-tag">${escapeHtml(w.field)}</span>
      </div>
      <div>
        <button class="btn btn-outline btn-sm view-exp-btn" data-well-id="${escapeHtml(w.well_id)}">
          View Historical Experience →
        </button>
      </div>
    </div>
  `).join('');

  // Attach click handler to navigate directly to experience page with selected well
  elements.dashSimilarList.querySelectorAll('.view-exp-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      state.selectedExperienceWellId = btn.dataset.wellId;
      switchTab('historical-experience');
    });
  });
}

// ---------------- Current Well Page ----------------
function syncCurrentWellForm() {
  const w = state.currentWell;
  elements.inputWellId.value = w.well_id;
  elements.inputField.value = w.field;
  elements.inputFormation.value = w.formation;
  elements.inputTotalDepth.value = w.total_depth;
  elements.inputCurrentDepth.value = w.current_depth;
  elements.inputInclination.value = w.inclination;
  elements.inputAzimuth.value = w.azimuth;
  elements.inputMudWeight.value = w.mud_weight;
  elements.inputPressure.value = w.pressure;
  elements.inputRop.value = w.rop;
  elements.inputWob.value = w.wob;
  elements.inputTorque.value = w.torque;
}

function readCurrentWellForm() {
  return {
    well_id: elements.inputWellId.value.trim(),
    field: elements.inputField.value.trim(),
    formation: elements.inputFormation.value.trim(),
    total_depth: parseFloat(elements.inputTotalDepth.value) || 3000.0,
    current_depth: parseFloat(elements.inputCurrentDepth.value) || 2700.0,
    inclination: parseFloat(elements.inputInclination.value) || 0.0,
    azimuth: parseFloat(elements.inputAzimuth.value) || 0.0,
    mud_weight: parseFloat(elements.inputMudWeight.value) || 10.0,
    pressure: parseFloat(elements.inputPressure.value) || 3000.0,
    rop: parseFloat(elements.inputRop.value) || 10.0,
    wob: parseFloat(elements.inputWob.value) || 15.0,
    torque: parseFloat(elements.inputTorque.value) || 12.0
  };
}

async function handleFindSimilarWells(e) {
  if (e) e.preventDefault();
  state.currentWell = readCurrentWellForm();
  updateDashboardCurrentWellUI();

  const payload = {
    total_depth: state.currentWell.total_depth,
    mud_weight: state.currentWell.mud_weight,
    pressure: state.currentWell.pressure,
    rop: state.currentWell.rop,
    wob: state.currentWell.wob,
    torque: state.currentWell.torque,
    inclination: state.currentWell.inclination,
    azimuth: state.currentWell.azimuth,
    top_k: 3,
    current_depth: state.currentWell.current_depth
  };

  try {
    elements.currentWellResults.classList.remove('hidden');
    elements.currentWellMatches.innerHTML = `
      <div class="state-container">
        <div class="spinner"></div>
        <span>Comparing against 500 historical wells...</span>
      </div>`;

    const res = await apiPost('/api/similar-wells', payload);
    state.similarWells = res.similar_wells;
    elements.matchExplanation.textContent = res.explanation;
    renderCurrentWellMatches(res.similar_wells);
  } catch {
    elements.currentWellMatches.innerHTML = `
      <div class="state-container">
        <span>Error retrieving similar wells.</span>
      </div>`;
  }
}

function renderCurrentWellMatches(matches) {
  if (!matches || matches.length === 0) {
    elements.currentWellMatches.innerHTML = '<div class="state-container"><span>No matching offset wells found.</span></div>';
    return;
  }

  elements.currentWellMatches.innerHTML = matches.map(m => {
    const params = m.parameter_breakdown || {};
    return `
      <div class="match-detail-card">
        <div class="match-header">
          <div>
            <span class="well-id-text">${escapeHtml(m.well_id)}</span>
            <span class="similarity-badge ml-2">${m.similarity}% Match</span>
            <span class="well-meta-tag ml-3">${escapeHtml(m.formation)} (${escapeHtml(m.field)})</span>
          </div>
          <button class="btn btn-primary btn-sm view-exp-btn" data-well-id="${escapeHtml(m.well_id)}">
            View Historical Experience →
          </button>
        </div>

        <table class="param-table-mini">
          <thead>
            <tr>
              <th>Feature</th>
              <th>Current Well</th>
              <th>Matched Well</th>
              <th>Delta</th>
              <th>Match Quality</th>
            </tr>
          </thead>
          <tbody>
            ${Object.keys(params).map(k => {
              const p = params[k];
              const sign = p.difference > 0 ? '+' : '';
              return `
                <tr>
                  <td>${escapeHtml(p.feature)}</td>
                  <td>${p.input_value} ${escapeHtml(p.unit)}</td>
                  <td>${p.matched_value} ${escapeHtml(p.unit)}</td>
                  <td>${sign}${p.difference} ${escapeHtml(p.unit)}</td>
                  <td><strong>${escapeHtml(p.match_quality)}</strong></td>
                </tr>
              `;
            }).join('')}
          </tbody>
        </table>
      </div>
    `;
  }).join('');

  elements.currentWellMatches.querySelectorAll('.view-exp-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      state.selectedExperienceWellId = btn.dataset.wellId;
      switchTab('historical-experience');
    });
  });
}

// ---------------- Offset Wells Page ----------------
async function loadOffsetWells() {
  elements.offsetLoading.classList.remove('hidden');
  elements.offsetWellsTbody.innerHTML = '';

  try {
    const selectedField = elements.offsetFieldFilter.value;
    const url = selectedField ? `/api/wells?field=${encodeURIComponent(selectedField)}` : '/api/wells';
    const wells = await apiGet(url);
    state.offsetWells = wells;
    applyOffsetFilters();
  } catch {
    elements.offsetWellsTbody.innerHTML = `
      <tr>
        <td colspan="7" class="text-center">Unable to load offset wells from database.</td>
      </tr>`;
  } finally {
    elements.offsetLoading.classList.add('hidden');
  }
}

function applyOffsetFilters() {
  const query = elements.offsetSearch.value.trim().toLowerCase();
  state.offsetFilteredWells = state.offsetWells.filter(w => {
    return !query || w.well_id.toLowerCase().includes(query) || w.formation.toLowerCase().includes(query);
  });
  state.offsetCurrentPage = 1;
  renderOffsetWellsPage();
}

function renderOffsetWellsPage() {
  const total = state.offsetFilteredWells.length;
  const startIdx = (state.offsetCurrentPage - 1) * state.offsetPageSize;
  const endIdx = Math.min(startIdx + state.offsetPageSize, total);
  const pageWells = state.offsetFilteredWells.slice(startIdx, endIdx);

  elements.paginationInfo.textContent = `Showing ${total > 0 ? startIdx + 1 : 0} - ${endIdx} of ${total} wells`;
  elements.btnPrevPage.disabled = (state.offsetCurrentPage <= 1);
  elements.btnNextPage.disabled = (endIdx >= total);

  if (pageWells.length === 0) {
    elements.offsetWellsTbody.innerHTML = `
      <tr>
        <td colspan="7" class="text-center text-muted" style="padding: 2rem;">No matching offset wells found.</td>
      </tr>`;
    return;
  }

  elements.offsetWellsTbody.innerHTML = pageWells.map(w => `
    <tr>
      <td><strong>${escapeHtml(w.well_id)}</strong></td>
      <td>${escapeHtml(w.field)}</td>
      <td>${escapeHtml(w.formation)}</td>
      <td>${w.total_depth.toFixed(1)} m</td>
      <td>${w.mud_weight.toFixed(1)} ppg</td>
      <td>${Math.round(w.pressure)} psi</td>
      <td>
        <button class="btn btn-outline btn-sm open-well-btn" data-well-id="${escapeHtml(w.well_id)}">
          View Events & Details
        </button>
      </td>
    </tr>
  `).join('');

  elements.offsetWellsTbody.querySelectorAll('.open-well-btn').forEach(btn => {
    btn.addEventListener('click', () => openWellModal(btn.dataset.wellId));
  });
}

// ---------------- Historical Experience Page ----------------
// ---------------- Historical Experience Page ----------------
async function loadHistoricalExperience() {
  const w = state.currentWell;
  elements.expCurrentWellId.textContent = w.well_id;
  elements.expCurrentLocation.textContent = `${w.field} Field • ${w.formation}`;
  elements.expCurDepth.textContent = `${w.current_depth.toFixed(1)} m`;
  elements.expCurMw.textContent = `${w.mud_weight.toFixed(1)} ppg`;
  elements.expCurPress.textContent = `${Math.round(w.pressure)} psi`;
  elements.expCurRop.textContent = `${w.rop.toFixed(1)} m/hr`;

  elements.experienceLoading.classList.remove('hidden');
  elements.expMainCardContainer.innerHTML = '';
  elements.expOtherEventsContainer.innerHTML = '';
  elements.expWellsSelector.innerHTML = '';

  const payload = {
    total_depth: w.total_depth,
    mud_weight: w.mud_weight,
    pressure: w.pressure,
    rop: w.rop,
    wob: w.wob,
    torque: w.torque,
    inclination: w.inclination,
    azimuth: w.azimuth,
    top_k: 3,
    current_depth: w.current_depth
  };

  try {
    const data = await apiPost('/api/experience-search', payload);
    state.experienceData = data;

    // Pick top 3 similar wells
    const top3 = data.similar_wells.slice(0, 3);
    const top3Map = new Map(top3.map(sw => [sw.well_id, sw]));
    const top3Ids = new Set(top3.map(sw => sw.well_id));
    const allTop3Events = data.historical_experiences.filter(e => top3Ids.has(e.well_id));

    // Rank events across ALL TOP 3 SIMILAR WELLS to find the highest-ranked historical precedent
    const bestOverall = findMostRelevantEvent(allTop3Events, state.currentWell.current_depth, top3Map);

    // Fix 1: Always reset to 'BEST_PRECEDENT' on every new query (never lock to previously selected well)
    state.selectedExperienceWellId = 'BEST_PRECEDENT';

    renderExperienceWellsSelector(top3, bestOverall);
    renderSelectedWellExperiences();
  } catch {
    elements.expMainCardContainer.innerHTML = `
      <div class="state-container">
        <span>Failed to retrieve historical experiences from backend. Ensure server is active.</span>
      </div>`;
  } finally {
    elements.experienceLoading.classList.add('hidden');
  }
}

function renderExperienceWellsSelector(topSimilarWells, bestOverall) {
  if (!topSimilarWells || topSimilarWells.length === 0) {
    if (elements.expPrecedentToggle) elements.expPrecedentToggle.innerHTML = '';
    elements.expWellsSelector.innerHTML = '<span class="text-muted">No similar wells identified.</span>';
    return;
  }

  const isBestActive = (!state.selectedExperienceWellId || state.selectedExperienceWellId === 'BEST_PRECEDENT');

  // Fix 2: Render "Best Historical Precedent" option above the Top 3 well selector
  if (elements.expPrecedentToggle) {
    elements.expPrecedentToggle.innerHTML = `
      <button class="btn-best-precedent ${isBestActive ? 'active' : ''}" id="btn-select-best-precedent" type="button">
        <div style="display: flex; align-items: center; justify-content: space-between; width: 100%;">
          <div style="display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap;">
            <span style="font-size: 1.1rem; color: #f59e0b; line-height: 1;">★</span>
            <strong style="font-size: 0.95rem; color: var(--text-main);">Best Historical Precedent</strong>
            <span style="font-size: 0.82rem; color: var(--text-muted);">
              (Top precedent across all 3 wells: <strong style="font-family: var(--font-mono); color: var(--primary);">${escapeHtml(bestOverall?.source_well_id || '')}</strong> · ${escapeHtml(bestOverall?.event_type || '')} · Score: ${bestOverall?.final_score?.toFixed(1) || ''})
            </span>
          </div>
          ${isBestActive ? '<span style="font-size: 0.72rem; background: var(--primary); color: #fff; padding: 0.15rem 0.5rem; border-radius: 4px; font-weight: 600; text-transform: uppercase;">Selected</span>' : ''}
        </div>
      </button>
    `;

    elements.expPrecedentToggle.querySelector('#btn-select-best-precedent')?.addEventListener('click', () => {
      state.selectedExperienceWellId = 'BEST_PRECEDENT';
      renderExperienceWellsSelector(topSimilarWells, bestOverall);
      renderSelectedWellExperiences();
    });
  }

  // Display top 3 similar historical wells with ID, Similarity %, Formation, Field
  elements.expWellsSelector.innerHTML = topSimilarWells.map(w => {
    const isSelected = (w.well_id === state.selectedExperienceWellId);
    const isGlobalWinner = (bestOverall && w.well_id === bestOverall.source_well_id);
    return `
      <button class="offset-tab-btn ${isSelected ? 'active' : ''}" data-well-id="${escapeHtml(w.well_id)}" type="button">
        <div style="display: flex; align-items: center; justify-content: space-between;">
          <div>
            <strong style="font-family: var(--font-mono); font-size: 1.05rem;">${escapeHtml(w.well_id)}</strong>
            <span class="similarity-badge ml-2" style="font-size: 0.85rem; padding: 0.2rem 0.55rem;">${w.similarity}%</span>
          </div>
          ${isGlobalWinner ? '<span style="font-size: 0.72rem; border: 1px solid var(--primary); color: var(--primary); padding: 0.1rem 0.4rem; border-radius: 4px; font-weight: 600;">Source Precedent</span>' : ''}
        </div>
        <div style="font-size: 0.82rem; color: var(--text-muted); margin-top: 0.25rem;">
          ${escapeHtml(w.formation)} • ${escapeHtml(w.field)}
        </div>
      </button>
    `;
  }).join('');

  elements.expWellsSelector.querySelectorAll('.offset-tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      state.selectedExperienceWellId = btn.dataset.wellId;
      renderExperienceWellsSelector(topSimilarWells, bestOverall);
      renderSelectedWellExperiences();
    });
  });
}

const MEANINGFUL_EVENT_TYPES = new Set([
  'Lost Circulation',
  'Gas Kick',
  'Tight Hole / Pack-off',
  'Differential Sticking',
  'High Torque',
  'Wellbore Instability',
  'Pipe Sticking'
]);

function getDepthScore(depthDifference) {
  if (depthDifference <= 100) return 100;
  if (depthDifference <= 250) return 80;
  if (depthDifference <= 500) return 60;
  if (depthDifference <= 750) return 35;
  return 10;
}

function getEventScore(eventType) {
  switch (eventType) {
    case 'Gas Kick':
    case 'Lost Circulation':
      return 100;
    case 'Pipe Sticking':
    case 'Differential Sticking':
      return 90;
    case 'Tight Hole / Pack-off':
    case 'High Torque':
    case 'Wellbore Instability':
      return 80;
    case 'No Significant Event':
    default:
      return 20;
  }
}

function scoreEvent(evt, currentDepth, wellMetaMap) {
  const well = wellMetaMap ? wellMetaMap.get(evt.well_id) : null;
  const depthDiff = Math.abs(evt.depth - currentDepth);
  const depthScore = getDepthScore(depthDiff);
  const eventScore = getEventScore(evt.event_type);
  const finalScore = Number(((0.65 * depthScore) + (0.35 * eventScore)).toFixed(2));
  const isMeaningful = MEANINGFUL_EVENT_TYPES.has(evt.event_type);

  return {
    ...evt,
    source_well_id: evt.well_id,
    source_similarity: well?.similarity ?? null,
    source_field: well?.field ?? '',
    source_formation: well?.formation ?? '',
    depth_difference: depthDiff,
    depth_score: depthScore,
    event_score: eventScore,
    final_score: finalScore,
    is_meaningful: isMeaningful
  };
}

function findMostRelevantEvent(events, currentDepth, wellMetaMap) {
  if (!events || events.length === 0) return null;

  const scoredEvents = events.map(evt => scoreEvent(evt, currentDepth, wellMetaMap));

  // Separate meaningful incidents from routine/fallback events
  const meaningfulEvents = scoredEvents.filter(e => e.is_meaningful);

  // If meaningful events exist, rank among them.
  // "No Significant Event" remains a fallback ONLY when the well has no meaningful drilling event.
  const candidates = meaningfulEvents.length > 0 ? meaningfulEvents : scoredEvents;

  // Rank candidate events: highest final_score first; tie-break on smaller depth_difference
  candidates.sort((a, b) => {
    if (b.final_score !== a.final_score) {
      return b.final_score - a.final_score;
    }
    return a.depth_difference - b.depth_difference;
  });

  return candidates[0];
}

function renderSelectedWellExperiences() {
  if (!state.experienceData) return;

  const top3 = state.experienceData.similar_wells.slice(0, 3);
  const top3Map = new Map(top3.map(w => [w.well_id, w]));
  const top3Ids = new Set(top3.map(w => w.well_id));
  const currentDepth = state.currentWell.current_depth;

  // Collect and score all events across top 3 wells
  const allTop3Events = state.experienceData.historical_experiences
    .filter(e => top3Ids.has(e.well_id))
    .map(e => scoreEvent(e, currentDepth, top3Map));

  if (allTop3Events.length === 0) {
    elements.expMainCardContainer.innerHTML = `
      <div class="card main-experience-card">
        <div class="step-badge">3. Most Relevant Historical Experience</div>
        <div class="main-experience-header">
          <div>
            <h3 class="main-card-title">Most Relevant Historical Experience</h3>
            <p class="main-card-subtitle">Historical event ranked by operational relevance and depth proximity</p>
          </div>
        </div>
        <p class="text-muted mt-3">No historical drilling records logged for the top 3 offset wells.</p>
      </div>`;
    elements.expOtherEventsContainer.innerHTML = '';
    elements.expSummaryText.textContent = `3 similar offset wells were identified. No incidents logged.`;
    return;
  }

  const isGlobalMode = (!state.selectedExperienceWellId || state.selectedExperienceWellId === 'BEST_PRECEDENT');
  const currentWellId = state.selectedExperienceWellId;

  let eventsToRank = [];
  if (isGlobalMode) {
    // Mode A: Best Historical Precedent across all Top 3 wells
    eventsToRank = allTop3Events;
  } else {
    // Mode B: Individual selected well
    eventsToRank = allTop3Events.filter(e => e.source_well_id === currentWellId);

    // Fix 3: Explicit zero-event handling when user selects a well with 0 events
    if (eventsToRank.length === 0) {
      const wellMeta = top3Map.get(currentWellId);
      elements.expMainCardContainer.innerHTML = `
        <div class="card main-experience-card">
          <div class="step-badge">3. Most Relevant Historical Experience</div>
          <div class="main-experience-header">
            <div>
              <h3 class="main-card-title">Historical Offset Well Experience</h3>
              <p class="main-card-subtitle">Filtered by individual offset well</p>
            </div>
            <div class="source-well-tag" style="background: var(--bg-card-subtle); border: 1px solid var(--border-color); border-left: 3px solid var(--primary); padding: 0.35rem 0.75rem; border-radius: var(--radius-sm); font-size: 0.86rem; display: flex; align-items: center; gap: 0.35rem;">
              <span style="color: var(--text-muted); font-size: 0.8rem;">Well ID:</span>
              <strong style="font-family: var(--font-mono); color: var(--primary);">${escapeHtml(currentWellId)}</strong>
              ${wellMeta ? `<span style="color: var(--text-muted);">·</span><span style="color: var(--text-main); font-weight: 600;">Similarity: ${wellMeta.similarity}%</span>` : ''}
            </div>
          </div>
          <div style="padding: 2.5rem 1rem; text-align: center;">
            <p style="font-size: 1.05rem; font-weight: 600; color: var(--text-main); margin-bottom: 0.35rem;">
              No historical events logged for this well.
            </p>
            <p style="font-size: 0.88rem; color: var(--text-muted);">
              Well ID: <strong style="font-family: var(--font-mono);">${escapeHtml(currentWellId)}</strong>
            </p>
          </div>
        </div>
      `;
      elements.expOtherEventsContainer.innerHTML = '';
      elements.expSummaryText.textContent = `Offset well ${currentWellId} has no historical drilling events or incidents recorded in the database. Choose another similar well or return to Best Historical Precedent.`;
      return;
    }
  }

  // Rank candidate events: meaningful events prioritized; tie-break on smaller depth_difference
  const meaningfulEvents = eventsToRank.filter(e => e.is_meaningful);
  const candidates = meaningfulEvents.length > 0 ? meaningfulEvents : eventsToRank;
  candidates.sort((a, b) => {
    if (b.final_score !== a.final_score) {
      return b.final_score - a.final_score;
    }
    return a.depth_difference - b.depth_difference;
  });

  const mostRelevant = candidates[0];
  const otherEvents = (isGlobalMode ? allTop3Events : eventsToRank).filter(e => e.event_id !== mostRelevant.event_id);

  const badgeClass = getBadgeClassForEventType(mostRelevant.event_type);

  // Render ONE prominent card: Most Relevant Historical Experience
  elements.expMainCardContainer.innerHTML = `
    <div class="card main-experience-card">
      <div class="step-badge">3. Most Relevant Historical Experience</div>
      <div class="main-experience-header">
        <div>
          <h3 class="main-card-title">Most Relevant Historical Experience</h3>
          <p class="main-card-subtitle">${isGlobalMode ? 'Globally highest-ranked historical event across all Top 3 similar wells' : `Historical events logged for offset well ${escapeHtml(currentWellId)}`}</p>
        </div>
        <div class="source-well-tag" style="background: var(--bg-card-subtle); border: 1px solid var(--border-color); border-left: 3px solid var(--primary); padding: 0.35rem 0.75rem; border-radius: var(--radius-sm); font-size: 0.86rem; display: flex; align-items: center; gap: 0.35rem;">
          <span style="color: var(--text-muted); font-size: 0.8rem;">Source Well:</span>
          <strong style="font-family: var(--font-mono); color: var(--primary);">${escapeHtml(mostRelevant.source_well_id)}</strong>
          <span style="color: var(--text-muted);">·</span>
          <span style="color: var(--text-main); font-weight: 600;">Similarity: ${mostRelevant.source_similarity}%</span>
        </div>
      </div>

      <!-- EVENT -->
      <div class="story-section">
        <div class="story-label event-badge-label">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polygon points="12 2 2 7 12 12 22 7 12 2"></polygon>
            <polyline points="2 17 12 22 22 17"></polyline>
            <polyline points="2 12 12 17 22 12"></polyline>
          </svg>
          Event
        </div>
        <div class="event-meta-line">
          <span class="event-type-badge ${badgeClass}">${escapeHtml(mostRelevant.event_type)}</span>
          <span class="event-depth-badge">Depth: ${mostRelevant.depth.toFixed(1)} m</span>
          <span class="event-depth-badge">Depth difference: ${mostRelevant.depth_difference.toFixed(1)} m</span>
          <span class="proximity-note">(Ranked score: ${mostRelevant.final_score.toFixed(1)} • Depth score: ${mostRelevant.depth_score}, Event score: ${mostRelevant.event_score})</span>
        </div>
      </div>

      <!-- WHAT HAPPENED? -->
      <div class="story-section">
        <div class="story-label what-happened">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="12" y1="8" x2="12" y2="12"></line>
            <line x1="12" y1="16" x2="12.01" y2="16"></line>
          </svg>
          What Happened?
        </div>
        <div class="story-text">
          ${escapeHtml(mostRelevant.description)}
        </div>
      </div>

      <!-- ACTION TAKEN -->
      <div class="story-section">
        <div class="story-label action-taken">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="9 11 12 14 22 4"></polyline>
            <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"></path>
          </svg>
          Action Taken
        </div>
        <div class="story-text">
          ${escapeHtml(mostRelevant.action_taken)}
        </div>
      </div>

      <!-- RESULT -->
      <div class="story-section">
        <div class="story-label result-outcome">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
            <polyline points="22 4 12 14.01 9 11.01"></polyline>
          </svg>
          Result
        </div>
        <div class="story-text">
          ${escapeHtml(mostRelevant.result)}
        </div>
      </div>
    </div>
  `;

  // Render compact other events (if any)
  if (otherEvents.length > 0) {
    const tableHeader = isGlobalMode
      ? `Other historical events from Top 3 offset wells (${otherEvents.length})`
      : `Other historical events for ${escapeHtml(currentWellId)} (${otherEvents.length})`;

    elements.expOtherEventsContainer.innerHTML = `
      <div class="other-events-card">
        <details class="other-events-details">
          <summary class="other-events-summary">
            ${tableHeader}
          </summary>
          <table class="compact-events-table">
            <thead>
              <tr>
                ${isGlobalMode ? '<th style="width: 100px;">Well ID</th>' : ''}
                <th style="width: 110px;">Depth</th>
                <th style="width: 140px;">Depth Difference</th>
                <th style="width: 170px;">Event Type</th>
                <th>Summary</th>
              </tr>
            </thead>
            <tbody>
              ${otherEvents.map(e => `
                <tr>
                  ${isGlobalMode ? `<td><strong style="font-family: var(--font-mono);">${escapeHtml(e.source_well_id || e.well_id)}</strong></td>` : ''}
                  <td><strong>${e.depth.toFixed(1)} m</strong></td>
                  <td><code>${e.depth_difference !== undefined ? e.depth_difference.toFixed(1) : Math.abs(e.depth - currentDepth).toFixed(1)} m</code></td>
                  <td><span class="event-type-badge ${getBadgeClassForEventType(e.event_type)}" style="font-size: 0.75rem; padding: 0.15rem 0.5rem;">${escapeHtml(e.event_type)}</span></td>
                  <td style="color: var(--text-muted); font-size: 0.82rem;">${escapeHtml(e.description.substring(0, 95))}...</td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </details>
      </div>
    `;
  } else {
    elements.expOtherEventsContainer.innerHTML = '';
  }

  // Update concise Decision Support Evidence Summary
  elements.expSummaryText.textContent = isGlobalMode
    ? `3 similar offset wells were evaluated. The most relevant historical experience was identified in offset well ${mostRelevant.source_well_id} (${mostRelevant.source_similarity}% similarity), recording a ${mostRelevant.event_type} at ${mostRelevant.depth.toFixed(1)} m (Depth difference: ${mostRelevant.depth_difference.toFixed(1)} m, Ranked score: ${mostRelevant.final_score.toFixed(1)}). The recorded operational response and outcome are provided as historical evidence for engineer review.`
    : `Evaluated offset well ${currentWellId} (${mostRelevant.source_similarity}% similarity). The most relevant recorded event is a ${mostRelevant.event_type} at ${mostRelevant.depth.toFixed(1)} m (Depth difference: ${mostRelevant.depth_difference.toFixed(1)} m, Ranked score: ${mostRelevant.final_score.toFixed(1)}). The recorded response and outcome are provided as historical reference.`;
}

function getBadgeClassForEventType(eventType) {
  const norm = eventType.toLowerCase();
  if (norm.includes('loss') || norm.includes('circulation')) return 'badge-lost-circulation';
  if (norm.includes('kick') || norm.includes('influx')) return 'badge-gas-kick';
  if (norm.includes('tight') || norm.includes('pack')) return 'badge-tight-hole';
  if (norm.includes('differential')) return 'badge-differential-sticking';
  if (norm.includes('pipe sticking')) return 'badge-pipe-sticking';
  if (norm.includes('torque')) return 'badge-high-torque';
  if (norm.includes('instability')) return 'badge-wellbore-instability';
  return 'badge-no-significant-event';
}

// ---------------- Modal: Well Details & Timeline ----------------
async function openWellModal(wellId) {
  elements.modalWellId.textContent = wellId;
  elements.modalWellSub.textContent = 'Loading well specifications and events...';
  elements.modalWellInfo.innerHTML = '';
  elements.modalEventsTimeline.innerHTML = '';
  elements.modalLoading.classList.remove('hidden');

  elements.wellModal.showModal();

  try {
    const [well, events] = await Promise.all([
      apiGet(`/api/wells/${encodeURIComponent(wellId)}`),
      apiGet(`/api/wells/${encodeURIComponent(wellId)}/events`)
    ]);

    elements.modalWellSub.textContent = `${well.field} Field • ${well.formation}`;

    elements.modalWellInfo.innerHTML = `
      <div class="param-box">
        <span class="param-label">Total Depth</span>
        <span class="param-value">${well.total_depth.toFixed(1)} <small>m</small></span>
      </div>
      <div class="param-box">
        <span class="param-label">Mud Weight</span>
        <span class="param-value">${well.mud_weight.toFixed(1)} <small>ppg</small></span>
      </div>
      <div class="param-box">
        <span class="param-label">Pressure</span>
        <span class="param-value">${Math.round(well.pressure)} <small>psi</small></span>
      </div>
      <div class="param-box">
        <span class="param-label">ROP / WOB</span>
        <span class="param-value">${well.rop.toFixed(1)} / ${well.wob.toFixed(1)}</span>
      </div>
      <div class="param-box">
        <span class="param-label">Trajectory</span>
        <span class="param-value">${well.inclination.toFixed(1)}° / ${Math.round(well.azimuth)}°</span>
      </div>
    `;

    if (!events || events.length === 0) {
      elements.modalEventsTimeline.innerHTML = '<p class="text-muted">No historical events recorded for this well.</p>';
    } else {
      elements.modalEventsTimeline.innerHTML = events.map(e => `
        <div class="timeline-item">
          <div class="timeline-event-header">
            <span class="event-type-badge ${getBadgeClassForEventType(e.event_type)}">${escapeHtml(e.event_type)}</span>
            <span class="timeline-depth">${e.depth.toFixed(1)} m</span>
          </div>
          <div class="timeline-desc"><strong>Event:</strong> ${escapeHtml(e.description)}</div>
          <div class="timeline-box"><strong>Action Taken:</strong> ${escapeHtml(e.action_taken)}</div>
          <div class="timeline-box"><strong>Result:</strong> ${escapeHtml(e.result)}</div>
        </div>
      `).join('');
    }
  } catch {
    elements.modalEventsTimeline.innerHTML = '<p class="text-muted">Error loading well events from API.</p>';
  } finally {
    elements.modalLoading.classList.add('hidden');
  }
}

function closeWellModal() {
  elements.wellModal.close();
}

function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

// ---------------- Event Listeners & Initialization ----------------
function initEventListeners() {
  // Navigation tabs
  elements.navButtons.forEach(btn => {
    btn.addEventListener('click', () => switchTab(btn.dataset.tab));
  });

  // Dashboard buttons
  elements.btnEditWell.addEventListener('click', () => switchTab('current-well'));
  elements.dashRefreshSimilar.addEventListener('click', loadDashboardSimilarWells);

  // Current Well Form
  elements.wellForm.addEventListener('submit', handleFindSimilarWells);

  // Scenario Presets
  elements.scenarioPreset.addEventListener('change', () => {
    const presetKey = elements.scenarioPreset.value;
    if (SCENARIO_PRESETS[presetKey]) {
      state.currentWell = { ...SCENARIO_PRESETS[presetKey] };
      syncCurrentWellForm();
      updateDashboardCurrentWellUI();
      handleFindSimilarWells();
    }
  });

  // Offset Wells Controls
  elements.offsetSearch.addEventListener('input', applyOffsetFilters);
  elements.offsetFieldFilter.addEventListener('change', loadOffsetWells);

  elements.btnPrevPage.addEventListener('click', () => {
    if (state.offsetCurrentPage > 1) {
      state.offsetCurrentPage--;
      renderOffsetWellsPage();
    }
  });

  elements.btnNextPage.addEventListener('click', () => {
    const total = state.offsetFilteredWells.length;
    if (state.offsetCurrentPage * state.offsetPageSize < total) {
      state.offsetCurrentPage++;
      renderOffsetWellsPage();
    }
  });

  // Modal close handlers
  elements.modalCloseBtn.addEventListener('click', closeWellModal);
  elements.modalFooterClose.addEventListener('click', closeWellModal);
  elements.wellModal.addEventListener('click', (e) => {
    if (e.target === elements.wellModal) closeWellModal();
  });
}

// Bootstrap Application
async function initApp() {
  initEventListeners();
  updateDashboardCurrentWellUI();
  syncCurrentWellForm();

  await checkBackendHealth();
  await loadDashboardSimilarWells();
}

document.addEventListener('DOMContentLoaded', initApp);
