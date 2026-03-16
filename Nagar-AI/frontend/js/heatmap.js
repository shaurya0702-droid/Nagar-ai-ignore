/* ═══════════════════════════════════════════════════════════════════════════
   NagarAI — Ward Risk Heatmap Controller
   Leaflet.js — real Delhi locality coordinates
   ═══════════════════════════════════════════════════════════════════════════ */

let leafletMap   = null;
let mapMarkers   = [];

// Real Delhi coordinates — matches seed_data.py Zone table exactly
const WARD_COORDS = {
    "Connaught Place": [28.6315, 77.2167],
    "Civil Lines":     [28.6810, 77.2290],
    "Karol Bagh":      [28.6514, 77.1907],
    "Rohini":          [28.7384, 77.1172],
    "Dwarka":          [28.5921, 77.0460],
    "Lajpat Nagar":    [28.5700, 77.2373]
};

// Color by avg_priority score — matches priority formula thresholds exactly
function getMarkerColor(avgPriority) {
    if (avgPriority >= 0.75) return '#ef4444';   // CRITICAL — red
    if (avgPriority >= 0.55) return '#f97316';   // HIGH — orange
    if (avgPriority >= 0.35) return '#eab308';   // MEDIUM — yellow
    return '#22c55e';                            // LOW — green
}

function initHeatmap() {
    if (leafletMap) {
        leafletMap.remove();
        leafletMap = null;
    }

    leafletMap = L.map('ward-map').setView([28.6480, 77.1500], 11);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 18
    }).addTo(leafletMap);

    addMapLegend();
}

function renderHeatmapMarkers(wardData) {
    if (!leafletMap) return;

    // Remove previous markers
    mapMarkers.forEach(m => leafletMap.removeLayer(m));
    mapMarkers = [];

    wardData.forEach(ward => {
        const coords      = WARD_COORDS[ward.ward] || [28.6480, 77.1500];
        const avgPriority = ward.avg_priority || 0;
        const color       = getMarkerColor(avgPriority);

        // Outer glow circle — subtle aura behind the main marker
        const glowRadius = Math.max(32, ward.count * 12);
        const glowCircle = L.circleMarker(coords, {
            radius:      glowRadius,
            fillColor:   color,
            color:       color,
            weight:      0,
            opacity:     0,
            fillOpacity: 0.10,
            interactive: false
        }).addTo(leafletMap);
        mapMarkers.push(glowCircle);

        // Main solid marker — radius scales with complaint volume
        const mainRadius = Math.max(20, ward.count * 7);
        const circle = L.circleMarker(coords, {
            radius:      mainRadius,
            fillColor:   color,
            color:       color,
            weight:      2,
            opacity:     1,
            fillOpacity: 0.45
        }).addTo(leafletMap);

        // Dark-themed popup
        const urgencyIcon = ward.critical > 0 ? '🚨' : ward.density === 'High' ? '⚠️' : '📍';
        circle.bindPopup(`
            <div style="font-family:'DM Sans',sans-serif;min-width:210px;padding:4px;">
                <div style="font-size:15px;font-weight:600;color:#f59e0b;margin-bottom:10px;
                            border-bottom:1px solid rgba(245,158,11,0.3);padding-bottom:6px;">
                    ${urgencyIcon} ${ward.ward}
                </div>
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;font-size:13px;">
                    <span style="color:#94a3b8;">Total</span>
                    <span style="font-weight:600;color:#e2e8f0;">${ward.count} complaints</span>
                    <span style="color:#ef4444;">Critical</span>
                    <span style="font-weight:600;color:#ef4444;">${ward.critical}</span>
                    <span style="color:#f97316;">High</span>
                    <span style="font-weight:600;color:#f97316;">${ward.high}</span>
                    <span style="color:#eab308;">Medium</span>
                    <span style="font-weight:600;color:#eab308;">${ward.medium}</span>
                    <span style="color:#22c55e;">Low</span>
                    <span style="font-weight:600;color:#22c55e;">${ward.low}</span>
                    <span style="color:#94a3b8;">Avg Priority</span>
                    <span style="font-weight:600;color:#e2e8f0;">${(avgPriority * 10).toFixed(1)}/10</span>
                </div>
                <div style="margin-top:10px;padding:6px 10px;border-radius:6px;text-align:center;
                            background:${color}22;border:1px solid ${color}66;
                            color:${color};font-weight:600;font-size:12px;">
                    Risk Level: ${ward.density}
                </div>
            </div>
        `, {
            maxWidth: 270,
            className: 'nagarai-popup'
        });

        mapMarkers.push(circle);

        // Animated pulse rings for CRITICAL wards only
        if (ward.critical > 0) {
            addPulseRings(coords, color, leafletMap);
        }
    });
}

function addPulseRings(coords, color, map) {
    const icon = L.divIcon({
        className: '',
        html: `<div class="map-pulse-ring" style="--pulse-color:${color};"></div>`,
        iconSize:   [60, 60],
        iconAnchor: [30, 30]
    });
    const marker = L.marker(coords, { icon, interactive: false }).addTo(map);
    mapMarkers.push(marker);
}

function addMapLegend() {
    const legend = L.control({ position: 'bottomright' });
    legend.onAdd = () => {
        const div = L.DomUtil.create('div', 'nagarai-map-legend');
        div.innerHTML = `
            <div style="background:rgba(5,13,26,0.92);border:1px solid rgba(245,158,11,0.3);
                        padding:12px 16px;border-radius:10px;font-family:'DM Sans',sans-serif;
                        font-size:12px;color:#e2e8f0;min-width:170px;">
                <div style="color:#f59e0b;font-weight:600;margin-bottom:8px;font-size:13px;">
                    Ward Risk Level
                </div>
                <div style="display:flex;flex-direction:column;gap:5px;">
                    <div style="display:flex;align-items:center;gap:8px;">
                        <span style="width:12px;height:12px;border-radius:50%;background:#ef4444;flex-shrink:0;"></span>
                        <span>Critical (avg &ge;0.75)</span>
                    </div>
                    <div style="display:flex;align-items:center;gap:8px;">
                        <span style="width:12px;height:12px;border-radius:50%;background:#f97316;flex-shrink:0;"></span>
                        <span>High (avg &ge;0.55)</span>
                    </div>
                    <div style="display:flex;align-items:center;gap:8px;">
                        <span style="width:12px;height:12px;border-radius:50%;background:#eab308;flex-shrink:0;"></span>
                        <span>Medium (avg &ge;0.35)</span>
                    </div>
                    <div style="display:flex;align-items:center;gap:8px;">
                        <span style="width:12px;height:12px;border-radius:50%;background:#22c55e;flex-shrink:0;"></span>
                        <span>Low (avg &lt;0.35)</span>
                    </div>
                </div>
                <div style="margin-top:8px;padding-top:8px;border-top:1px solid rgba(248,250,252,0.1);
                            font-size:11px;color:#64748b;">
                    Circle size = complaint volume<br>
                    Pulse rings = active CRITICAL alerts
                </div>
            </div>
        `;
        return div;
    };
    legend.addTo(leafletMap);
}

// Called after complaint status update to refresh map without full reload
async function refreshHeatmap() {
    if (!leafletMap) return;
    try {
        const heatmapData = await API.getHeatmap();
        renderHeatmapMarkers(heatmapData);
    } catch (e) {
        console.warn('Heatmap refresh failed:', e);
    }
}
