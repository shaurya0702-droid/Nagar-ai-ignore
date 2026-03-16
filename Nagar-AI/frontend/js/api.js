/* ═══════════════════════════════════════════════════════════════════════════
   NagarAI — API Client + Demo Data
   ═══════════════════════════════════════════════════════════════════════════ */

// When running via Docker (nginx proxy): relative path /api → proxied to backend:8000
// When running locally (no Docker): change to 'http://localhost:8000'
const API_BASE = (window.location.port === '3000' || window.location.hostname !== 'localhost')
  ? '/api'
  : 'http://localhost:8000';

/* ── Demo Complaints (all 25) ──────────────────────────────────────────────── */
const DEMO_COMPLAINTS = [
  { id:1, complaint_id:'CMP-2025-001', text:'Emergency! Gas leak detected near Karol Bagh market. Multiple residents reporting strong smell. Children in nearby school showing symptoms of dizziness.', category:'Emergency', ward_id:3, ward_name:'Karol Bagh', severity_score:0.95, credibility_score:0.80, priority_score:0.95, priority_label:'CRITICAL', status:'Pending', emergency_override:true, is_duplicate:false, report_count:7, sla_hours:6, time_elapsed_hours:2.0, sla_breached:false, severity_keywords:['gas leak','emergency','children'], credibility_features:['detailed description','location mentioned','specific symptoms'], department:'Disaster Management Cell', ai_recommendation:{ action:'🚨 URGENT: Deploy emergency response team immediately to Karol Bagh', reason:'AI detected keywords: gas leak, emergency, children. Severity: 9.5/10. Credibility: 8.0/10.', impact:'Prevent potential disaster affecting 500+ residents and reduce escalation risk.', authority:'Disaster Management Cell', urgency:'IMMEDIATE', ai_summary:'CRITICAL priority Emergency in Karol Bagh. IMMEDIATE response by Disaster Management Cell recommended.' } },
  { id:2, complaint_id:'CMP-2025-002', text:'Garbage pile has been growing for 3 days near Civil Lines main market. Stench is unbearable and attracting rats. Health hazard for nearby residents.', category:'Garbage Issue', ward_id:2, ward_name:'Civil Lines', severity_score:0.64, credibility_score:0.86, priority_score:0.73, priority_label:'HIGH', status:'Pending', emergency_override:false, is_duplicate:false, report_count:1, sla_hours:24, time_elapsed_hours:30.0, sla_breached:true, severity_keywords:['garbage','stench','health hazard'], credibility_features:['specific duration mentioned','location mentioned','health impact described'], department:'Sanitation Department', ai_recommendation:{ action:'Deploy sanitation crew to Civil Lines within 4 hours', reason:'AI detected keywords: garbage, stench, health hazard. Severity: 6.4/10. Credibility: 8.6/10.', impact:'Reduce health hazard risk for 200+ residents.', authority:'Sanitation Department', urgency:'SAME_DAY', ai_summary:'HIGH priority Garbage Issue in Civil Lines. SAME DAY response by Sanitation Department recommended.' } },
  { id:3, complaint_id:'CMP-2025-003', text:'Major water pipe burst on Dwarka main road. Water flowing for 6 hours, road waterlogged. Municipal water supply disrupted to 200+ households.', category:'Water Leakage', ward_id:5, ward_name:'Dwarka', severity_score:0.64, credibility_score:0.66, priority_score:0.65, priority_label:'HIGH', status:'Assigned', emergency_override:false, is_duplicate:false, report_count:1, sla_hours:36, time_elapsed_hours:18.0, sla_breached:false, severity_keywords:['water','burst','pipe'], credibility_features:['duration specified','impact quantified'], department:'Jal Board', ai_recommendation:{ action:'Send Jal Board emergency plumbing unit to Dwarka', reason:'AI detected keywords: burst, pipe. Severity: 6.4/10. Credibility: 6.6/10.', impact:'Restore water supply for 200+ households.', authority:'Jal Board', urgency:'WITHIN_24H', ai_summary:'HIGH priority Water Leakage in Dwarka. WITHIN 24H response by Jal Board recommended.' } },
  { id:4, complaint_id:'CMP-2025-004', text:'Large pothole on Connaught Place arterial road caused accident today. Vehicle damaged. Road is dangerous especially at night. Requires urgent repair.', category:'Road Damage', ward_id:1, ward_name:'Connaught Place', severity_score:0.67, credibility_score:0.67, priority_score:0.67, priority_label:'HIGH', status:'Pending', emergency_override:false, is_duplicate:false, report_count:1, sla_hours:48, time_elapsed_hours:52.0, sla_breached:true, severity_keywords:['pothole','accident','dangerous'], credibility_features:['incident reported','location mentioned'], department:'Public Works Department', ai_recommendation:{ action:'Dispatch Public Works repair team to Connaught Place', reason:'AI detected keywords: pothole, accident. Severity: 6.7/10.', impact:'Prevent accidents for 200+ commuters.', authority:'Public Works Department', urgency:'WITHIN_48H', ai_summary:'HIGH priority Road Damage in Connaught Place. WITHIN 48H response by Public Works Department recommended.' } },
  { id:5, complaint_id:'CMP-2025-005', text:'All 12 street lights on Rohini sector 7 road have been non-functional for 7 days. Area completely dark at night, women feel unsafe, 2 chain snatching incidents reported.', category:'Street Light Failure', ward_id:4, ward_name:'Rohini', severity_score:0.43, credibility_score:0.88, priority_score:0.61, priority_label:'HIGH', status:'Escalated', emergency_override:false, is_duplicate:false, report_count:3, sla_hours:48, time_elapsed_hours:170.0, sla_breached:true, severity_keywords:['dark','unsafe','incidents'], credibility_features:['count specified','duration mentioned','incidents reported'], department:'Electricity Department', ai_recommendation:{ action:'Dispatch electrical maintenance crew to Rohini', reason:'AI detected keywords: unsafe, dark. Severity: 4.3/10. Credibility: 8.8/10.', impact:'Improve night safety for 200+ citizens.', authority:'Electricity Department', urgency:'WITHIN_48H', ai_summary:'HIGH priority Street Light Failure in Rohini. WITHIN 48H response by Electricity Department recommended.' } },
  { id:6, complaint_id:'CMP-2025-006', text:'Illegal construction blocking emergency exit of residential building in Lajpat Nagar. Fire escape completely blocked. Building has elderly and children residents.', category:'Public Safety', ward_id:6, ward_name:'Lajpat Nagar', severity_score:0.79, credibility_score:0.89, priority_score:0.83, priority_label:'CRITICAL', status:'Pending', emergency_override:false, is_duplicate:false, report_count:1, sla_hours:12, time_elapsed_hours:8.0, sla_breached:false, severity_keywords:['illegal','fire escape','blocked','emergency'], credibility_features:['specific hazard described','vulnerable residents mentioned'], department:'Municipal Security & Police Coordination', ai_recommendation:{ action:'Coordinate Municipal Security and Police patrol to Lajpat Nagar', reason:'AI detected keywords: fire escape, blocked, emergency. Severity: 7.9/10.', impact:'Ensure safety for 500+ residents.', authority:'Municipal Security & Police Coordination', urgency:'WITHIN_24H', ai_summary:'CRITICAL priority Public Safety in Lajpat Nagar. WITHIN 24H response recommended.' } },
  { id:7, complaint_id:'CMP-2025-007', text:'Underground water pipe leaking near Civil Lines junction for 4 days. Road developing sinkhole risk. Multiple vehicles have had near misses.', category:'Water Leakage', ward_id:2, ward_name:'Civil Lines', severity_score:0.57, credibility_score:0.84, priority_score:0.68, priority_label:'HIGH', status:'Assigned', emergency_override:false, is_duplicate:false, report_count:1, sla_hours:36, time_elapsed_hours:12.0, sla_breached:false, severity_keywords:['sinkhole','leaking','risk'], credibility_features:['duration specified','safety risk noted'], department:'Jal Board', ai_recommendation:{ action:'Send Jal Board emergency plumbing unit to Civil Lines', reason:'AI detected: sinkhole, leaking. Severity: 5.7/10.', impact:'Prevent contamination for 200+ households.', authority:'Jal Board', urgency:'WITHIN_24H', ai_summary:'HIGH priority Water Leakage in Civil Lines. WITHIN 24H response by Jal Board recommended.' } },
  { id:8, complaint_id:'CMP-2025-008', text:'Road collapse near Karol Bagh bridge approach. Large section of road has caved in. Traffic diverted but area still risky.', category:'Road Damage', ward_id:3, ward_name:'Karol Bagh', severity_score:0.44, credibility_score:0.77, priority_score:0.57, priority_label:'HIGH', status:'Pending', emergency_override:false, is_duplicate:false, report_count:1, sla_hours:48, time_elapsed_hours:96.0, sla_breached:true, severity_keywords:['collapse','road','risky'], credibility_features:['specific location','traffic impact described'], department:'Public Works Department', ai_recommendation:{ action:'Dispatch Public Works repair team to Karol Bagh', reason:'AI detected: collapse, road. Severity: 4.4/10.', impact:'Prevent accidents for 200+ commuters.', authority:'Public Works Department', urgency:'WITHIN_48H', ai_summary:'HIGH priority Road Damage in Karol Bagh. WITHIN 48H response recommended.' } },
  { id:9, complaint_id:'CMP-2025-009', text:'URGENT: Electric pole fell on parked cars in Connaught Place. Live wires exposed on road. People gathering dangerously close. Need immediate response.', category:'Emergency', ward_id:1, ward_name:'Connaught Place', severity_score:0.99, credibility_score:0.95, priority_score:0.99, priority_label:'CRITICAL', status:'In Progress', emergency_override:true, is_duplicate:false, report_count:1, sla_hours:6, time_elapsed_hours:4.0, sla_breached:false, severity_keywords:['electric','live wires','urgent','dangerous'], credibility_features:['urgent tone','specific incident','immediate risk'], department:'Disaster Management Cell', ai_recommendation:{ action:'🚨 URGENT: Deploy emergency response team immediately to Connaught Place', reason:'AI detected: live wires, urgent, dangerous. Severity: 9.9/10. EMERGENCY OVERRIDE.', impact:'Prevent potential disaster affecting 500+ residents.', authority:'Disaster Management Cell', urgency:'IMMEDIATE', ai_summary:'CRITICAL priority Emergency in Connaught Place. IMMEDIATE response by Disaster Management Cell required.' } },
  { id:10, complaint_id:'CMP-2025-010', text:'Small crack on park pathway in Rohini. Not urgent but should be repaired eventually.', category:'Road Damage', ward_id:4, ward_name:'Rohini', severity_score:0.22, credibility_score:0.15, priority_score:0.19, priority_label:'LOW', status:'Pending', emergency_override:false, is_duplicate:false, report_count:1, sla_hours:96, time_elapsed_hours:20.0, sla_breached:false, severity_keywords:['crack'], credibility_features:[], department:'Public Works Department', ai_recommendation:{ action:'Dispatch Public Works repair team to Rohini', reason:'Low severity complaint. Severity: 2.2/10. Credibility: 1.5/10.', impact:'Address concern for 50+ residents.', authority:'Public Works Department', urgency:'WITHIN_48H', ai_summary:'LOW priority Road Damage in Rohini.' } },
  { id:11, complaint_id:'CMP-2025-011', text:'Water meter leaking in Dwarka colony C block. Wastage of water. Has been reported twice before. Meter needs replacement.', category:'Water Leakage', ward_id:5, ward_name:'Dwarka', severity_score:0.58, credibility_score:0.83, priority_score:0.68, priority_label:'HIGH', status:'Pending', emergency_override:false, is_duplicate:false, report_count:1, sla_hours:36, time_elapsed_hours:6.0, sla_breached:false, severity_keywords:['leaking','wastage'], credibility_features:['repeated complaint','specific block mentioned'], department:'Jal Board', ai_recommendation:{ action:'Send Jal Board emergency plumbing unit to Dwarka', reason:'Repeated complaint. Severity: 5.8/10.', impact:'Restore supply and prevent contamination.', authority:'Jal Board', urgency:'WITHIN_24H', ai_summary:'HIGH priority Water Leakage in Dwarka. WITHIN 24H response by Jal Board recommended.' } },
  { id:12, complaint_id:'CMP-2025-012', text:'Garbage dumping happening at Lajpat Nagar park entrance. Residents dump garbage at night illegally.', category:'Garbage Issue', ward_id:6, ward_name:'Lajpat Nagar', severity_score:0.50, credibility_score:0.43, priority_score:0.47, priority_label:'MEDIUM', status:'Pending', emergency_override:false, is_duplicate:false, report_count:1, sla_hours:24, time_elapsed_hours:48.0, sla_breached:true, severity_keywords:['garbage','illegal'], credibility_features:[], department:'Sanitation Department', ai_recommendation:{ action:'Deploy sanitation crew to Lajpat Nagar within 4 hours', reason:'Severity: 5.0/10. Credibility: 4.3/10.', impact:'Reduce health hazard for 100+ residents.', authority:'Sanitation Department', urgency:'SAME_DAY', ai_summary:'MEDIUM priority Garbage Issue in Lajpat Nagar.' } },
  { id:13, complaint_id:'CMP-2025-013', text:'Stray dogs attacking pedestrians near Karol Bagh school. 3 children bitten this week. Parents afraid to send children to school. Animal control needed urgently.', category:'Public Safety', ward_id:3, ward_name:'Karol Bagh', severity_score:0.95, credibility_score:0.85, priority_score:0.95, priority_label:'CRITICAL', status:'Pending', emergency_override:true, is_duplicate:false, report_count:3, sla_hours:12, time_elapsed_hours:10.0, sla_breached:false, severity_keywords:['attacking','bitten','danger','children'], credibility_features:['incidents quantified','specific location','vulnerable group'], department:'Municipal Security & Police Coordination', ai_recommendation:{ action:'🚨 URGENT: Coordinate Municipal Security and Police patrol to Karol Bagh', reason:'AI detected: attacking, bitten, children. Severity: 9.5/10. EMERGENCY OVERRIDE.', impact:'Ensure safety for 500+ residents.', authority:'Municipal Security & Police Coordination', urgency:'IMMEDIATE', ai_summary:'CRITICAL priority Public Safety in Karol Bagh. IMMEDIATE response required.' } },
  { id:14, complaint_id:'CMP-2025-014', text:'Bridge approach road in Lajpat Nagar has developed dangerous cracks. Heavy vehicles using this route daily. Structural assessment needed before it fails completely.', category:'Road Damage', ward_id:6, ward_name:'Lajpat Nagar', severity_score:0.95, credibility_score:0.84, priority_score:0.95, priority_label:'CRITICAL', status:'Assigned', emergency_override:true, is_duplicate:false, report_count:1, sla_hours:48, time_elapsed_hours:36.0, sla_breached:false, severity_keywords:['dangerous','structural','cracks','bridge'], credibility_features:['specific risk','technical assessment demanded'], department:'Public Works Department', ai_recommendation:{ action:'🚨 URGENT: Dispatch Public Works repair team to Lajpat Nagar', reason:'AI detected: dangerous, structural, cracks. Severity: 9.5/10. EMERGENCY OVERRIDE.', impact:'Prevent accidents for 500+ commuters.', authority:'Public Works Department', urgency:'IMMEDIATE', ai_summary:'CRITICAL priority Road Damage in Lajpat Nagar. IMMEDIATE response required.' } },
  { id:15, complaint_id:'CMP-2025-015', text:'Street lights near Connaught Place park not working for 3 days. Park area dark at night.', category:'Street Light Failure', ward_id:1, ward_name:'Connaught Place', severity_score:0.40, credibility_score:0.67, priority_score:0.51, priority_label:'MEDIUM', status:'Pending', emergency_override:false, is_duplicate:false, report_count:1, sla_hours:48, time_elapsed_hours:72.0, sla_breached:true, severity_keywords:['dark'], credibility_features:['duration mentioned'], department:'Electricity Department', ai_recommendation:{ action:'Dispatch electrical maintenance crew to Connaught Place', reason:'Severity: 4.0/10. Credibility: 6.7/10.', impact:'Improve night safety for 100+ citizens.', authority:'Electricity Department', urgency:'WITHIN_48H', ai_summary:'MEDIUM priority Street Light Failure in Connaught Place.' } },
  { id:16, complaint_id:'CMP-2025-016', text:'EMERGENCY: Sewage overflow flooding Rohini residential area. Raw sewage entering ground floor homes. Children and elderly at serious health risk. URGENT.', category:'Emergency', ward_id:4, ward_name:'Rohini', severity_score:0.92, credibility_score:0.86, priority_score:0.92, priority_label:'CRITICAL', status:'Pending', emergency_override:true, is_duplicate:false, report_count:5, sla_hours:6, time_elapsed_hours:1.0, sla_breached:false, severity_keywords:['sewage','flooding','emergency','health risk'], credibility_features:['emergency flag','vulnerable groups','immediate impact'], department:'Disaster Management Cell', ai_recommendation:{ action:'🚨 URGENT: Deploy emergency response team immediately to Rohini', reason:'AI detected: sewage, flooding, emergency. Severity: 9.2/10. EMERGENCY OVERRIDE.', impact:'Prevent disaster affecting 500+ residents.', authority:'Disaster Management Cell', urgency:'IMMEDIATE', ai_summary:'CRITICAL priority Emergency in Rohini. IMMEDIATE response by Disaster Management Cell required.' } },
  { id:17, complaint_id:'CMP-2025-017', text:'Garbage collection stopped in Dwarka for 8 days. Multiple residents complained. Bins overflowing.', category:'Garbage Issue', ward_id:5, ward_name:'Dwarka', severity_score:0.30, credibility_score:0.88, priority_score:0.53, priority_label:'MEDIUM', status:'Escalated', emergency_override:false, is_duplicate:false, report_count:1, sla_hours:24, time_elapsed_hours:192.0, sla_breached:true, severity_keywords:['overflowing','garbage'], credibility_features:['duration specified','multiple residents'], department:'Sanitation Department', ai_recommendation:{ action:'Deploy sanitation crew to Dwarka within 4 hours', reason:'Severity: 3.0/10. Duration: 8 days.', impact:'Reduce health hazard for 100+ residents.', authority:'Sanitation Department', urgency:'SAME_DAY', ai_summary:'MEDIUM priority Garbage Issue in Dwarka.' } },
  { id:18, complaint_id:'CMP-2025-018', text:'Main water supply pipeline exposed in Civil Lines due to road work. Risk of contamination if not covered. Water quality complaints from nearby residents.', category:'Water Leakage', ward_id:2, ward_name:'Civil Lines', severity_score:0.60, credibility_score:0.77, priority_score:0.67, priority_label:'HIGH', status:'In Progress', emergency_override:false, is_duplicate:false, report_count:1, sla_hours:36, time_elapsed_hours:14.0, sla_breached:false, severity_keywords:['contamination','exposed','pipeline'], credibility_features:['cause identified','risk described'], department:'Jal Board', ai_recommendation:{ action:'Send Jal Board emergency plumbing unit to Civil Lines', reason:'AI detected: contamination, exposed. Severity: 6.0/10.', impact:'Prevent contamination for 200+ households.', authority:'Jal Board', urgency:'WITHIN_24H', ai_summary:'HIGH priority Water Leakage in Civil Lines. WITHIN 24H response recommended.' } },
  { id:19, complaint_id:'CMP-2025-019', text:'Street light pole leaning dangerously in Karol Bagh lane 4.', category:'Street Light Failure', ward_id:3, ward_name:'Karol Bagh', severity_score:0.65, credibility_score:0.10, priority_score:0.43, priority_label:'MEDIUM', status:'Pending', emergency_override:false, is_duplicate:false, report_count:1, sla_hours:48, time_elapsed_hours:25.0, sla_breached:false, severity_keywords:['leaning','dangerously'], credibility_features:[], department:'Electricity Department', ai_recommendation:{ action:'Dispatch electrical maintenance crew to Karol Bagh', reason:'Severity: 6.5/10. Credibility: 1.0/10.', impact:'Improve night safety for 100+ citizens.', authority:'Electricity Department', urgency:'WITHIN_48H', ai_summary:'MEDIUM priority Street Light Failure in Karol Bagh.' } },
  { id:20, complaint_id:'CMP-2025-020', text:'Entire Connaught Place sector 3 road has developed severe potholes after recent rains. 3 accidents reported. Road practically impassable for two-wheelers. Urgent repair needed.', category:'Road Damage', ward_id:1, ward_name:'Connaught Place', severity_score:0.21, credibility_score:0.93, priority_score:0.50, priority_label:'MEDIUM', status:'Pending', emergency_override:false, is_duplicate:false, report_count:1, sla_hours:48, time_elapsed_hours:120.0, sla_breached:true, severity_keywords:['potholes','accidents'], credibility_features:['incidents quantified','thorough description','urgency noted'], department:'Public Works Department', ai_recommendation:{ action:'Dispatch Public Works repair team to Connaught Place', reason:'AI detected: potholes, accidents. Severity: 2.1/10. Credibility: 9.3/10.', impact:'Prevent accidents for 100+ commuters.', authority:'Public Works Department', urgency:'WITHIN_48H', ai_summary:'MEDIUM priority Road Damage in Connaught Place.' } },
  { id:21, complaint_id:'CMP-2025-021', text:'Water leakage from overhead tank in Rohini building B. Overflow running for 2 days wasting thousands of liters.', category:'Water Leakage', ward_id:4, ward_name:'Rohini', severity_score:0.65, credibility_score:0.83, priority_score:0.72, priority_label:'HIGH', status:'Pending', emergency_override:false, is_duplicate:false, report_count:1, sla_hours:36, time_elapsed_hours:3.0, sla_breached:false, severity_keywords:['overflow','waste','leakage'], credibility_features:['duration specified','quantified waste'], department:'Jal Board', ai_recommendation:{ action:'Send Jal Board emergency plumbing unit to Rohini', reason:'AI detected: overflow, leakage. Severity: 6.5/10.', impact:'Restore supply for 200+ households.', authority:'Jal Board', urgency:'WITHIN_24H', ai_summary:'HIGH priority Water Leakage in Rohini. WITHIN 24H response by Jal Board recommended.' } },
  { id:22, complaint_id:'CMP-2025-022', text:'Abandoned building in Lajpat Nagar being used by miscreants. Residents afraid. Illegal activities suspected. Children warned to stay away. Police and municipal action needed.', category:'Public Safety', ward_id:6, ward_name:'Lajpat Nagar', severity_score:0.76, credibility_score:0.74, priority_score:0.75, priority_label:'CRITICAL', status:'Pending', emergency_override:false, is_duplicate:false, report_count:1, sla_hours:12, time_elapsed_hours:240.0, sla_breached:true, severity_keywords:['illegal','miscreants','unsafe'], credibility_features:['community concern','specific location'], department:'Municipal Security & Police Coordination', ai_recommendation:{ action:'Coordinate Municipal Security and Police patrol to Lajpat Nagar', reason:'AI detected: illegal, unsafe. Severity: 7.6/10.', impact:'Ensure safety for 500+ residents.', authority:'Municipal Security & Police Coordination', urgency:'WITHIN_24H', ai_summary:'CRITICAL priority Public Safety in Lajpat Nagar.' } },
  { id:23, complaint_id:'CMP-2025-023', text:'URGENT: Massive garbage fire in Karol Bagh dumpyard. Toxic smoke spreading to nearby residential area. People with respiratory problems severely affected. Fire brigade needed.', category:'Garbage Issue', ward_id:3, ward_name:'Karol Bagh', severity_score:0.91, credibility_score:0.88, priority_score:0.91, priority_label:'CRITICAL', status:'Pending', emergency_override:true, is_duplicate:false, report_count:4, sla_hours:24, time_elapsed_hours:56.0, sla_breached:true, severity_keywords:['fire','toxic','smoke','urgent'], credibility_features:['health impact specific','emergency indicated','vulnerable affected'], department:'Sanitation Department', ai_recommendation:{ action:'🚨 URGENT: Deploy sanitation crew to Karol Bagh within 4 hours', reason:'AI detected: fire, toxic, smoke. Severity: 9.1/10. EMERGENCY OVERRIDE.', impact:'Reduce health hazard for 500+ residents.', authority:'Sanitation Department', urgency:'IMMEDIATE', ai_summary:'CRITICAL priority Garbage Issue in Karol Bagh. IMMEDIATE response required.' } },
  { id:24, complaint_id:'CMP-2025-024', text:'Emergency water tanker required Dwarka. Main supply cut for 48 hours. Hospital nearby running out of water. Critical situation.', category:'Emergency', ward_id:5, ward_name:'Dwarka', severity_score:0.94, credibility_score:0.72, priority_score:0.94, priority_label:'CRITICAL', status:'Pending', emergency_override:true, is_duplicate:false, report_count:1, sla_hours:6, time_elapsed_hours:2.0, sla_breached:false, severity_keywords:['emergency','hospital','critical','48 hours'], credibility_features:['hospital mentioned','duration specified'], department:'Disaster Management Cell', ai_recommendation:{ action:'🚨 URGENT: Deploy emergency response team immediately to Dwarka', reason:'AI detected: emergency, hospital, critical. Severity: 9.4/10. EMERGENCY OVERRIDE.', impact:'Prevent disaster affecting 500+ residents including hospital.', authority:'Disaster Management Cell', urgency:'IMMEDIATE', ai_summary:'CRITICAL priority Emergency in Dwarka. IMMEDIATE response by Disaster Management Cell required.' } },
  { id:25, complaint_id:'CMP-2025-025', text:'Several street lights blinking/not working near Civil Lines bus stop area for 2 weeks.', category:'Street Light Failure', ward_id:2, ward_name:'Civil Lines', severity_score:0.45, credibility_score:0.72, priority_score:0.56, priority_label:'HIGH', status:'Pending', emergency_override:false, is_duplicate:false, report_count:1, sla_hours:48, time_elapsed_hours:16.0, sla_breached:false, severity_keywords:['blinking','not working'], credibility_features:['duration specified','location mentioned'], department:'Electricity Department', ai_recommendation:{ action:'Dispatch electrical maintenance crew to Civil Lines', reason:'Severity: 4.5/10. Duration: 2 weeks.', impact:'Improve night safety for 200+ citizens.', authority:'Electricity Department', urgency:'WITHIN_48H', ai_summary:'HIGH priority Street Light Failure in Civil Lines.' } }
];

const DEMO_STATS = {
  total:25, critical:8, high:10, medium:5, low:2,
  pending:18, resolved:0, escalated:2, in_progress:2, assigned:3,
  sla_breached:10, emergency_overrides:7
};

const DEMO_ANALYTICS = {
  complaints_per_ward: { 'Connaught Place':4, 'Civil Lines':4, 'Karol Bagh':5, 'Rohini':4, 'Dwarka':4, 'Lajpat Nagar':4 },
  daily_trend: [
    { day:'Day 1', date:'', count:3 }, { day:'Day 2', date:'', count:5 },
    { day:'Day 3', date:'', count:4 }, { day:'Day 4', date:'', count:6 },
    { day:'Day 5', date:'', count:2 }, { day:'Day 6', date:'', count:4 }, { day:'Day 7', date:'', count:1 }
  ],
  priority_distribution: { CRITICAL:8, HIGH:10, MEDIUM:5, LOW:2 },
  category_distribution: { 'Emergency':4, 'Garbage Issue':4, 'Road Damage':4, 'Water Leakage':5, 'Street Light Failure':4, 'Public Safety':4 },
  avg_response_time_per_ward: { 'Connaught Place':66, 'Civil Lines':18, 'Karol Bagh':39.8, 'Rohini':48.5, 'Dwarka':54.6, 'Lajpat Nagar':83.2 },
  escalation_vs_resolution: [
    { day:'Day 1', escalated:0, resolved:0 }, { day:'Day 2', escalated:1, resolved:0 },
    { day:'Day 3', escalated:0, resolved:0 }, { day:'Day 4', escalated:1, resolved:0 },
    { day:'Day 5', escalated:0, resolved:0 }, { day:'Day 6', escalated:0, resolved:0 }, { day:'Day 7', escalated:0, resolved:0 }
  ],
  ward_risk_scores: { 'Connaught Place':1.8, 'Civil Lines':2.0, 'Karol Bagh':3.2, 'Rohini':2.4, 'Dwarka':1.9, 'Lajpat Nagar':2.8 },
  spike_detection: { detected:true, ward:'Karol Bagh', count:5 },
  incident_clusters: [
    {
      ward:'Karol Bagh', category:'Emergency', count:5, avg_priority:0.93,
      severity:'CRITICAL', incident_severity:'CRITICAL', severity_icon:'🚨',
      has_critical:true, has_emergency:true, department:'Disaster Management Cell',
      citizens_affected:1200, estimated_citizens:1200, max_elapsed_hours:10.0,
      possible_cause:'Possible area-wide hazard or infrastructure failure',
      recommended_action:'🚨 URGENT: Deploy emergency response team immediately',
      alert_title:'Possible Urban Incident Detected',
      alert_subtitle:'Emergency Cluster — Karol Bagh',
      alert_message:'Possible urban incident detected — 5 Emergency complaints in Karol Bagh'
    },
    {
      ward:'Rohini', category:'Emergency', count:4, avg_priority:0.84,
      severity:'CRITICAL', incident_severity:'CRITICAL', severity_icon:'🚨',
      has_critical:true, has_emergency:true, department:'Disaster Management Cell',
      citizens_affected:960, estimated_citizens:960, max_elapsed_hours:170.0,
      possible_cause:'Possible area-wide hazard or infrastructure failure',
      recommended_action:'🚨 URGENT: Deploy emergency response team immediately',
      alert_title:'Possible Urban Incident Detected',
      alert_subtitle:'Emergency Cluster — Rohini',
      alert_message:'Possible urban incident detected — 4 Emergency complaints in Rohini'
    },
    {
      ward:'Civil Lines', category:'Water Leakage', count:4, avg_priority:0.65,
      severity:'HIGH', incident_severity:'HIGH', severity_icon:'⚠️',
      has_critical:false, has_emergency:false, department:'Jal Board',
      citizens_affected:744, estimated_citizens:744, max_elapsed_hours:30.0,
      possible_cause:'Possible underground pipeline failure or main supply burst',
      recommended_action:'Send Jal Board emergency repair team and isolate affected pipeline section',
      alert_title:'Possible Urban Incident Detected',
      alert_subtitle:'Water Leakage Cluster — Civil Lines',
      alert_message:'Possible urban incident detected — 4 Water Leakage complaints in Civil Lines'
    },
    {
      ward:'Lajpat Nagar', category:'Road Damage', count:4, avg_priority:0.72,
      severity:'HIGH', incident_severity:'HIGH', severity_icon:'⚠️',
      has_critical:true, has_emergency:true, department:'Public Works Department',
      citizens_affected:840, estimated_citizens:840, max_elapsed_hours:240.0,
      possible_cause:'Possible structural deterioration after recent rainfall or heavy traffic',
      recommended_action:'Dispatch Public Works rapid response team for structural safety assessment',
      alert_title:'Possible Urban Incident Detected',
      alert_subtitle:'Road Damage Cluster — Lajpat Nagar',
      alert_message:'Possible urban incident detected — 4 Road Damage complaints in Lajpat Nagar'
    },
    {
      ward:'Dwarka', category:'Garbage Issue', count:4, avg_priority:0.58,
      severity:'HIGH', incident_severity:'HIGH', severity_icon:'⚠️',
      has_critical:false, has_emergency:false, department:'Sanitation Department',
      citizens_affected:598, estimated_citizens:598, max_elapsed_hours:192.0,
      possible_cause:'Possible sanitation schedule failure or illegal dumping activity',
      recommended_action:'Deploy sanitation emergency crew and initiate health hazard assessment',
      alert_title:'Possible Urban Incident Detected',
      alert_subtitle:'Garbage Issue Cluster — Dwarka',
      alert_message:'Possible urban incident detected — 4 Garbage Issue complaints in Dwarka'
    },
    {
      ward:'Connaught Place', category:'Street Light Failure', count:4, avg_priority:0.55,
      severity:'HIGH', incident_severity:'HIGH', severity_icon:'⚠️',
      has_critical:false, has_emergency:false, department:'Electricity Department',
      citizens_affected:432, estimated_citizens:432, max_elapsed_hours:120.0,
      possible_cause:'Possible substation fault or cable damage affecting the entire sector',
      recommended_action:'Dispatch Electricity Department crew to inspect substation and sector cabling',
      alert_title:'Possible Urban Incident Detected',
      alert_subtitle:'Street Light Failure Cluster — Connaught Place',
      alert_message:'Possible urban incident detected — 4 Street Light Failure complaints in Connaught Place'
    }
  ],
  severity_keyword_frequency: { 'emergency':4, 'garbage':4, 'leak':4, 'dangerous':3, 'toxic':2, 'accident':3, 'overflow':2, 'contamination':2 },
  sla_breaches: DEMO_COMPLAINTS.filter(c => c.sla_breached).map(c => ({ complaint_id:c.complaint_id, ward_name:c.ward_name, category:c.category, time_elapsed_hours:c.time_elapsed_hours, sla_hours:c.sla_hours })),
  city_recommendation: {
    city_health_index: 0.32, city_health_label: 'High Risk',
    top_priority_ward: 'Karol Bagh', top_priority_action: 'Deploy emergency response team immediately to Karol Bagh',
    total_citizens_at_risk: 3200,
    recommendations: [
      { ward:'Karol Bagh', risk_score:3.2, recommended_action:'Deploy emergency response team', reason:'5 complaints, 3 CRITICAL', dominant_issue:'Emergency', priority_teams:['Disaster Management Cell','Public Works Department'] },
      { ward:'Lajpat Nagar', risk_score:2.8, recommended_action:'Dispatch Public Works + Security patrol', reason:'4 complaints, 2 CRITICAL', dominant_issue:'Road Damage', priority_teams:['Public Works Department','Municipal Security & Police Coordination'] },
      { ward:'Rohini', risk_score:2.4, recommended_action:'Deploy emergency + Jal Board units', reason:'4 complaints, 2 CRITICAL', dominant_issue:'Emergency', priority_teams:['Disaster Management Cell','Jal Board'] }
    ],
    resource_deployment_plan: [
      { team:'Disaster Management Cell', ward:'Karol Bagh', action:'Emergency response and evacuation' },
      { team:'Public Works Department', ward:'Lajpat Nagar', action:'Bridge inspection and repair' },
      { team:'Sanitation Department', ward:'Rohini', action:'Sewage overflow containment' }
    ],
    transparency_score: 72.4
  },
  transparency: {
    resolution_rate: 0, avg_response_time_hours: 52.8, sla_compliance_rate: 60,
    ward_performance: [
      { ward:'Civil Lines', total:4, resolved:0, avg_response_hours:18, performance_label:'Good', performance_score:65 },
      { ward:'Dwarka', total:4, resolved:0, avg_response_hours:54.6, performance_label:'Moderate', performance_score:42 },
      { ward:'Connaught Place', total:4, resolved:0, avg_response_hours:66, performance_label:'Needs Improvement', performance_score:28 },
      { ward:'Rohini', total:4, resolved:0, avg_response_hours:48.5, performance_label:'Needs Improvement', performance_score:25 },
      { ward:'Lajpat Nagar', total:4, resolved:0, avg_response_hours:83.2, performance_label:'Needs Improvement', performance_score:20 },
      { ward:'Karol Bagh', total:5, resolved:0, avg_response_hours:39.8, performance_label:'Needs Improvement', performance_score:18 }
    ],
    city_transparency_score: 72.4,
    citizen_satisfaction_avg: 0
  },
  responsible_ai: { model_confidence:92.4, false_positive_risk:'Low', explainability_enabled:true, bias_detection_active:true },
  impact: { citizens_served:300, avg_resolution_hours:52.8, high_risk_prevented:7, emergency_auto_boosts:7 },
  system_intelligence: { avg_resolution_time:52.8, escalated_count:2, emergency_auto_boosts:7, most_problematic_ward:'Karol Bagh', active_sla_breaches:10, environmental_alerts:3 }
};

const DEMO_HEATMAP = [
  { ward:'Karol Bagh',      lat:28.6514, lng:77.1907, count:5, critical:3, high:1, medium:1, low:0, avg_priority:0.82, density:'Critical' },
  { ward:'Lajpat Nagar',    lat:28.5700, lng:77.2373, count:4, critical:2, high:1, medium:1, low:0, avg_priority:0.74, density:'Critical' },
  { ward:'Rohini',          lat:28.7384, lng:77.1172, count:4, critical:2, high:1, medium:0, low:1, avg_priority:0.76, density:'Critical' },
  { ward:'Civil Lines',     lat:28.6810, lng:77.2290, count:4, critical:0, high:2, medium:1, low:1, avg_priority:0.58, density:'High'     },
  { ward:'Dwarka',          lat:28.5921, lng:77.0460, count:4, critical:1, high:2, medium:1, low:0, avg_priority:0.67, density:'Critical' },
  { ward:'Connaught Place', lat:28.6315, lng:77.2167, count:4, critical:1, high:2, medium:1, low:0, avg_priority:0.71, density:'Critical' }
];

/* ── Token / Auth management ───────────────────────────────────────────────── */
const Auth = {
  getToken:    ()  => localStorage.getItem('nagarai_token'),
  setToken:    (t) => localStorage.setItem('nagarai_token', t),
  getOfficer:  ()  => JSON.parse(localStorage.getItem('nagarai_officer') || 'null'),
  setOfficer:  (o) => localStorage.setItem('nagarai_officer', JSON.stringify(o)),
  clear:       ()  => { localStorage.removeItem('nagarai_token'); localStorage.removeItem('nagarai_officer'); },
  isLoggedIn:  ()  => !!localStorage.getItem('nagarai_token')
};

/* ── Core fetch wrapper ─────────────────────────────────────────────────────── */
async function apiFetch(endpoint, options = {}) {
  const token = Auth.getToken();
  const headers = { 'Content-Type': 'application/json', ...options.headers };
  if (token) headers['Authorization'] = `Bearer ${token}`;
  const response = await fetch(`${API_BASE}${endpoint}`, { ...options, headers });
  if (response.status === 401) { Auth.clear(); window.location.href = 'login.html'; throw new Error('Unauthorized'); }
  if (!response.ok) { const err = await response.json().catch(() => ({})); throw new Error(err.detail || `HTTP ${response.status}`); }
  return response.json();
}

/* ── API Object ─────────────────────────────────────────────────────────────── */
const API = {
  login: async (email, password) => {
    try {
      const data = await apiFetch('/auth/login', { method:'POST', body: JSON.stringify({ email, password }) });
      Auth.setToken(data.access_token);
      Auth.setOfficer(data.officer);
      return { success: true, officer: data.officer };
    } catch (e) {
      // Demo fallback: accept two known credential pairs
      const valid = (email === 'officer@gov.in' && password === '123456') ||
                    (email === 'officer@nagarai.gov.in' && password === 'NagarAI@123');
      if (valid) {
        const demoToken = 'demo-token-' + Date.now();
        const demoOfficer = { id:1, name: email === 'officer@gov.in' ? 'Officer Priya Singh' : 'Officer Rajesh Kumar', email, role:'officer', ward_id:1 };
        Auth.setToken(demoToken);
        Auth.setOfficer(demoOfficer);
        return { success:true, officer:demoOfficer };
      }
      return { success:false, error:'Invalid email or password' };
    }
  },

  submitComplaint: async (formData) => {
    try {
      return await apiFetch('/complaints', { method:'POST', body: JSON.stringify(formData) });
    } catch (e) {
      // Simulate ML analysis for demo
      const sev = (formData.text.toLowerCase().includes('emergency') || formData.text.toLowerCase().includes('urgent')) ? 0.92 : Math.random() * 0.4 + 0.4;
      const cred = Math.min(0.5 + (formData.text.split(' ').length / 40), 1.0);
      const pri = Math.round((0.6 * sev + 0.4 * cred) * 100) / 100;
      const label = pri >= 0.75 ? 'CRITICAL' : pri >= 0.55 ? 'HIGH' : pri >= 0.35 ? 'MEDIUM' : 'LOW';
      const slaMap = { CRITICAL:6, HIGH:36, MEDIUM:48, LOW:96 };
      const deptMap = { 'Emergency':'Disaster Management Cell', 'Garbage Issue':'Sanitation Department', 'Road Damage':'Public Works Department', 'Water Leakage':'Jal Board', 'Street Light Failure':'Electricity Department', 'Public Safety':'Municipal Security & Police Coordination' };
      const cid = 'CMP-2025-' + String(DEMO_COMPLAINTS.length + 1).padStart(3,'0');
      const emergency = sev > 0.85;
      return {
        complaint_id: cid,
        text: formData.text,
        category: formData.category,
        ward_name: formData.ward_name,
        severity_score: sev,
        credibility_score: cred,
        priority_score: pri,
        priority_label: label,
        status: 'Pending',
        emergency_override: emergency,
        sla_hours: slaMap[label],
        department: deptMap[formData.category] || 'General Administration',
        severity_keywords: formData.text.toLowerCase().match(/\b(emergency|urgent|leak|garbage|accident|dark|broken)\b/g) || [],
        credibility_features: ['description provided', formData.location ? 'location mentioned' : null, 'category specified'].filter(Boolean),
        ai_recommendation: {
          action: (emergency ? '🚨 URGENT: ' : '') + 'Deploy ' + (deptMap[formData.category] || 'municipal team') + ' to ' + formData.ward_name,
          reason: `AI analysis: Severity ${(sev*10).toFixed(1)}/10, Credibility ${(cred*10).toFixed(1)}/10.`,
          impact: `Address concern for ${label === 'CRITICAL' ? 500 : label === 'HIGH' ? 200 : 100}+ residents.`,
          authority: deptMap[formData.category] || 'General Administration',
          urgency: emergency ? 'IMMEDIATE' : label === 'HIGH' ? 'WITHIN_24H' : 'WITHIN_48H',
          ai_summary: `${label} priority ${formData.category} in ${formData.ward_name}.`
        },
        analysis: { severity_score_display: +(sev*10).toFixed(2), credibility_score_display: +(cred*10).toFixed(2), explanation:{ ai_summary: `${label} priority detected.` } }
      };
    }
  },

  getComplaints: async (filters = {}) => {
    try {
      const params = new URLSearchParams();
      if (filters.ward)     params.set('ward',     filters.ward);
      if (filters.priority) params.set('priority', filters.priority);
      if (filters.status)   params.set('status',   filters.status);
      if (filters.search)   params.set('search',   filters.search);
      const data = await apiFetch(`/complaints?${params}`);
      return data.complaints || data;
    } catch (e) {
      let result = [...DEMO_COMPLAINTS];
      if (filters.ward)     result = result.filter(c => c.ward_name === filters.ward);
      if (filters.priority) result = result.filter(c => c.priority_label === filters.priority.toUpperCase());
      if (filters.status)   result = result.filter(c => c.status === filters.status);
      if (filters.search)   result = result.filter(c => c.text.toLowerCase().includes(filters.search.toLowerCase()));
      return result;
    }
  },

  getComplaint: async (idOrComplaintId) => {
    try {
      return await apiFetch(`/complaints/${idOrComplaintId}`);
    } catch (e) {
      return DEMO_COMPLAINTS.find(c => c.id === idOrComplaintId || c.complaint_id === idOrComplaintId) || null;
    }
  },

  updateComplaint: async (complaintId, data) => {
    try {
      return await apiFetch(`/complaints/${complaintId}`, { method:'PATCH', body: JSON.stringify(data) });
    } catch (e) {
      const c = DEMO_COMPLAINTS.find(x => x.complaint_id === complaintId);
      if (c && data.status) c.status = data.status;
      return c;
    }
  },

  getStats: async () => {
    try { return await apiFetch('/complaints/stats/summary'); }
    catch (e) { return DEMO_STATS; }
  },

  getAnalytics: async () => {
    try { return await apiFetch('/analytics'); }
    catch (e) { return DEMO_ANALYTICS; }
  },

  getHeatmap: async () => {
    try { return await apiFetch('/analytics/heatmap'); }
    catch (e) { return DEMO_HEATMAP; }
  },

  recalculate: async () => {
    try { return await apiFetch('/complaints/recalculate', { method:'POST' }); }
    catch (e) { return { updated_count:25, message:'Recalculated 25 complaints (demo)' }; }
  },

  setEmergencyMode: async (enabled) => {
    try { return await apiFetch('/analytics/emergency-mode', { method:'POST', body: JSON.stringify({ enabled }) }); }
    catch (e) { return { emergency_mode:enabled, message: enabled ? '⚠️ Emergency Mode ACTIVATED (demo)' : '✅ Emergency Mode DEACTIVATED (demo)' }; }
  },

  trackComplaint: async (complaintId) => {
    try {
      const data = await apiFetch('/complaints?search=' + complaintId);
      const list = data.complaints || data;
      return list.find(c => c.complaint_id === complaintId) || null;
    } catch (e) {
      return DEMO_COMPLAINTS.find(c => c.complaint_id === complaintId) || null;
    }
  },

  submitFeedback: async (complaintId, rating, comment) => {
    try {
      return await apiFetch(`/complaints/${complaintId}/feedback`, {
        method:'POST',
        body: JSON.stringify({ complaint_id:complaintId, rating, comment })
      });
    } catch (e) {
      return { message:'Feedback submitted (demo)', complaint_id:complaintId, rating };
    }
  }
};
