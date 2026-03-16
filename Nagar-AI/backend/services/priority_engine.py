"""
NagarAI — Priority Engine
Orchestrates the full ML pipeline: severity → credibility → priority → recommendation → explanation.
"""

from typing import Optional

from ml.severity_model import SeverityModel
from ml.credibility_model import CredibilityModel
from ml.shap_explain import SHAPExplainer
from ml.recommendation_engine import RecommendationEngine
from ml.preprocessing import get_department


class PriorityEngine:
    """
    Central orchestrator for NagarAI's ML pipeline.
    Stateful: supports Emergency Mode (shifts weights to 0.8 severity / 0.2 credibility).
    """

    _emergency_mode: bool = False  # class-level shared state

    def __init__(self):
        self.severity_model = SeverityModel()
        self.credibility_model = CredibilityModel()
        self.explainer = SHAPExplainer()
        self.recommender = RecommendationEngine()

    # ─────────────────────────────────────────────────────────────────────────
    # EMERGENCY MODE CONTROL
    # ─────────────────────────────────────────────────────────────────────────

    @classmethod
    def set_emergency_mode(cls, enabled: bool) -> None:
        cls._emergency_mode = enabled

    @classmethod
    def is_emergency_mode(cls) -> bool:
        return cls._emergency_mode

    def get_weights(self) -> tuple:
        """Return (severity_weight, credibility_weight) based on current mode."""
        if self._emergency_mode:
            return (0.8, 0.2)
        return (0.6, 0.4)

    # ─────────────────────────────────────────────────────────────────────────
    # PRIORITY HELPERS
    # ─────────────────────────────────────────────────────────────────────────

    def get_priority_label(self, score: float) -> str:
        """Map priority score to label."""
        if score >= 0.75:
            return "CRITICAL"
        elif score >= 0.55:
            return "HIGH"
        elif score >= 0.35:
            return "MEDIUM"
        else:
            return "LOW"

    def get_sla_hours(self, label: str) -> int:
        """Return SLA hours for a given priority label."""
        sla_map = {
            "CRITICAL": 6,
            "HIGH": 36,
            "MEDIUM": 48,
            "LOW": 96,
        }
        return sla_map.get(label, 48)

    # ─────────────────────────────────────────────────────────────────────────
    # FULL PIPELINE
    # ─────────────────────────────────────────────────────────────────────────

    def analyze_complaint(
        self,
        text: str,
        category: str,
        ward: str,
        location: Optional[str] = None,
        existing_complaints: Optional[list] = None,
    ) -> dict:
        """
        Run the full NagarAI ML pipeline on a complaint.

        Steps:
        1.  severity_model.predict(text)
        2.  credibility_model.predict(text, category, ward, location)
        3.  credibility_model.check_duplicate(text, existing_complaints)
        4.  Calculate priority_score with current mode weights
        5.  If emergency_override: force priority_score = max(priority_score, 0.90)
        6.  get_priority_label(priority_score)
        7.  get_sla_hours(label)
        8.  get_department(category)
        9.  recommendation_engine.generate_single(...)
        10. explainer.get_full_explanation(...)

        Returns complete analysis dict.
        """
        # ── Step 1: Severity ──────────────────────────────────────────────
        severity_result = self.severity_model.predict(text)
        severity_score = severity_result["severity_score"]
        emergency_override = severity_result["emergency_override"]
        severity_keywords = severity_result["severity_keywords"]

        # ── Step 2: Credibility ───────────────────────────────────────────
        credibility_result = self.credibility_model.predict(
            text, category, ward, location
        )
        credibility_score = credibility_result["credibility_score"]
        credibility_features = credibility_result["credibility_features"]

        # ── Step 3: Duplicate check ───────────────────────────────────────
        is_duplicate = False
        duplicate_of_id = None
        if existing_complaints:
            dup_result = self.credibility_model.check_duplicate(
                text, existing_complaints
            )
            is_duplicate = dup_result.get("is_duplicate", False)
            duplicate_of_id = dup_result.get("duplicate_of_id")

        # ── Step 4: Priority score with mode-aware weights ────────────────
        sev_weight, cred_weight = self.get_weights()
        priority_score = round(
            sev_weight * severity_score + cred_weight * credibility_score, 4
        )

        # ── Step 5: Emergency override forces minimum 0.90 ────────────────
        if emergency_override:
            priority_score = max(priority_score, 0.90)
        priority_score = min(round(priority_score, 4), 1.0)

        # ── Step 6: Priority label ────────────────────────────────────────
        priority_label = self.get_priority_label(priority_score)

        # ── Step 7: SLA hours ─────────────────────────────────────────────
        sla_hours = self.get_sla_hours(priority_label)

        # ── Step 8: Department ────────────────────────────────────────────
        department = get_department(category)

        # ── Step 9: AI Recommendation ─────────────────────────────────────
        recommendation = self.recommender.generate_single(
            complaint_text=text,
            category=category,
            ward_name=ward,
            priority_label=priority_label,
            severity_score=severity_score,
            credibility_score=credibility_score,
            severity_keywords=severity_keywords,
            emergency_override=emergency_override,
        )

        # ── Step 10: Explanation ──────────────────────────────────────────
        priority_result_for_explainer = {
            "priority_label": priority_label,
            "priority_score": priority_score,
            "emergency_override": emergency_override,
        }
        explanation = self.explainer.get_full_explanation(
            severity_result, credibility_result, priority_result_for_explainer
        )

        return {
            # Severity
            "severity_score": severity_score,
            "severity_score_display": severity_result["severity_score_display"],
            # Credibility
            "credibility_score": credibility_score,
            "credibility_score_display": credibility_result["credibility_score_display"],
            # Priority
            "priority_score": priority_score,
            "priority_label": priority_label,
            "emergency_override": emergency_override,
            # Duplicate
            "is_duplicate": is_duplicate,
            "duplicate_of_id": duplicate_of_id,
            # Keywords / features
            "severity_keywords": severity_keywords,
            "credibility_features": credibility_features,
            # SLA
            "sla_hours": sla_hours,
            # Department
            "department": department,
            # AI modules
            "recommendation": recommendation,
            "explanation": explanation,
        }

    # ─────────────────────────────────────────────────────────────────────────
    # INCIDENT CLUSTER DETECTION
    # ─────────────────────────────────────────────────────────────────────────

    def detect_incident_clusters(self, complaints: list, min_count: int = 4) -> list:
        """
        Detect urban incident clusters — groups of complaints from the same
        ward+category that suggest a real infrastructure failure, not just
        individual reports.

        Logic:
          - Group complaints by (ward_name, category)
          - If count >= min_count → possible incident
          - Compute avg priority, dominant status, estimated citizens affected
          - Generate a recommended action and severity level

        complaints: list of dicts with keys:
            ward_name, category, priority_score, priority_label,
            emergency_override, status, time_elapsed_hours

        Returns: list of incident dicts, sorted by severity DESC.
        """
        from ml.preprocessing import DEPARTMENT_MAP

        RESIDENT_PER_COMPLAINT = {
            "Emergency":            150,
            "Water Leakage":        120,
            "Garbage Issue":        80,
            "Road Damage":          100,
            "Street Light Failure": 60,
            "Public Safety":        130,
        }

        INCIDENT_ACTIONS = {
            "Emergency":            "Deploy emergency response team immediately",
            "Water Leakage":        "Send Jal Board emergency repair team and isolate affected pipeline section",
            "Garbage Issue":        "Deploy sanitation emergency crew and initiate health hazard assessment",
            "Road Damage":          "Dispatch Public Works rapid response team for structural safety assessment",
            "Street Light Failure": "Dispatch Electricity Department crew to inspect substation and sector cabling",
            "Public Safety":        "Coordinate Municipal Security and Police for area patrol and crowd control",
        }

        # Doc §22: inferred systemic cause per category
        CAUSE_INFERENCE = {
            "Water Leakage":        "Possible underground pipeline failure or main supply burst",
            "Emergency":            "Possible area-wide hazard or infrastructure failure",
            "Garbage Issue":        "Possible sanitation schedule failure or illegal dumping activity",
            "Road Damage":          "Possible structural deterioration after recent rainfall or heavy traffic",
            "Street Light Failure": "Possible substation fault or cable damage affecting the entire sector",
            "Public Safety":        "Possible escalating community safety event requiring coordinated response",
        }

        # ── Group by (ward, category) ─────────────────────────────────────
        buckets: dict = {}
        for c in complaints:
            key = (c.get("ward_name", "Unknown"), c.get("category", "Unknown"))
            buckets.setdefault(key, []).append(c)

        incidents = []
        for (ward, category), items in buckets.items():
            if len(items) < min_count:
                continue

            count = len(items)
            scores = [c.get("priority_score", 0.0) for c in items]
            avg_priority = round(sum(scores) / count, 3)
            has_critical = any(c.get("priority_label") == "CRITICAL" for c in items)
            has_emergency = any(c.get("emergency_override", False) for c in items)
            max_elapsed = max((c.get("time_elapsed_hours", 0) for c in items), default=0)

            # ── Severity classification ───────────────────────────────────
            if has_emergency or avg_priority >= 0.75:
                severity = "CRITICAL"
                severity_icon = "🚨"
            elif has_critical or avg_priority >= 0.55:
                severity = "HIGH"
                severity_icon = "⚠️"
            elif avg_priority >= 0.35:
                severity = "MEDIUM"
                severity_icon = "🟡"
            else:
                severity = "LOW"
                severity_icon = "📋"

            # ── Citizens affected ─────────────────────────────────────────
            base_per_complaint = RESIDENT_PER_COMPLAINT.get(category, 90)
            spread_multiplier = min(1.0 + (count - min_count) * 0.1, 2.0)
            citizens_affected = int(base_per_complaint * count * spread_multiplier)

            # ── Recommended action ────────────────────────────────────────
            action = INCIDENT_ACTIONS.get(category, "Assign municipal officer to investigate")
            if severity == "CRITICAL":
                action = f"🚨 URGENT: {action}"

            # ── Doc §22 fields ────────────────────────────────────────────
            possible_cause = CAUSE_INFERENCE.get(category, "Pattern suggests systemic infrastructure issue")
            alert_title    = "Possible Urban Incident Detected"
            alert_subtitle = f"{category} Cluster — {ward}"

            incidents.append({
                "ward":               ward,
                "category":           category,
                "count":              count,
                "avg_priority":       avg_priority,
                # Severity (both names: frontend uses severity, doc §22 uses incident_severity)
                "severity":           severity,
                "incident_severity":  severity,
                "severity_icon":      severity_icon,
                "has_critical":       has_critical,
                "has_emergency":      has_emergency,
                "department":         DEPARTMENT_MAP.get(category, "General Administration"),
                "recommended_action": action,
                # Citizens (both names: frontend uses citizens_affected, doc uses estimated_citizens)
                "citizens_affected":  citizens_affected,
                "estimated_citizens": citizens_affected,
                "max_elapsed_hours":  round(max_elapsed, 1),
                # Doc §22 intelligence fields
                "possible_cause":     possible_cause,
                "alert_title":        alert_title,
                "alert_subtitle":     alert_subtitle,
                "alert_message": (
                    f"Possible urban incident detected — {count} {category} "
                    f"complaints in {ward}"
                ),
            })

        # Sort: CRITICAL first, then by count DESC
        severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        incidents.sort(key=lambda x: (severity_order.get(x["severity"], 9), -x["count"]))
        return incidents

    # ─────────────────────────────────────────────────────────────────────────
    # SPIKE DETECTION
    # ─────────────────────────────────────────────────────────────────────────

    def detect_spike(self, ward_counts: dict, threshold: int = 4) -> dict:
        """
        Detect if any ward has reached or exceeded the complaint threshold.
        ward_counts: {ward_name: count}

        Returns {"detected": bool, "ward": str or None, "count": int}
        """
        for ward, count in ward_counts.items():
            if count >= threshold:
                return {"detected": True, "ward": ward, "count": count}
        return {"detected": False, "ward": None, "count": 0}

    # ─────────────────────────────────────────────────────────────────────────
    # WARD RISK SCORES
    # ─────────────────────────────────────────────────────────────────────────

    def calculate_ward_risk_scores(self, complaints: list) -> dict:
        """
        Calculate risk score per ward.
        risk_score = avg(priority_score) * count

        complaints: list of dicts with 'ward_name' and 'priority_score'
        Returns: {"Ward 1": 2.4, "Ward 2": 1.8, ...}
        """
        ward_scores: dict = {}
        ward_counts: dict = {}

        for c in complaints:
            ward = c.get("ward_name", "Unknown")
            score = c.get("priority_score", 0.0)
            if ward not in ward_scores:
                ward_scores[ward] = 0.0
                ward_counts[ward] = 0
            ward_scores[ward] += score
            ward_counts[ward] += 1

        result = {}
        for ward in ward_scores:
            count = ward_counts[ward]
            avg_score = ward_scores[ward] / count if count > 0 else 0.0
            result[ward] = round(avg_score * count, 4)

        return result


# Singleton — shared across the app
priority_engine = PriorityEngine()
