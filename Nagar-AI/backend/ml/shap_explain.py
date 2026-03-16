"""
NagarAI — SHAP-Style Explainability Module
Rule-based explanation of AI decisions (no external SHAP library needed).
"""


class SHAPExplainer:
    """
    Provides human-readable explanations for severity, credibility, and priority decisions.
    Designed to give city officials transparent insight into AI scoring.
    """

    # ─────────────────────────────────────────────────────────────────────────
    # SEVERITY EXPLANATION
    # ─────────────────────────────────────────────────────────────────────────

    def explain_severity(
        self, text: str, severity_score: float, keywords: list
    ) -> str:
        """
        Returns a human-readable severity explanation string.
        """
        score_display = round(severity_score * 10, 2)

        if severity_score > 0.85:
            level = "CRITICAL"
            urgency_str = "Requires immediate action."
        elif severity_score >= 0.60:
            level = "HIGH"
            urgency_str = "Urgent attention needed within 24–48 hours."
        elif severity_score >= 0.35:
            level = "MEDIUM"
            urgency_str = "Should be scheduled for resolution this week."
        else:
            level = "LOW"
            urgency_str = "Can be addressed during routine operations."

        if keywords:
            kw_str = ", ".join(keywords[:5])
            return (
                f"Severity score {score_display}/10 detected. "
                f"Emergency keywords found: {kw_str}. "
                f"{level} urgency classification. {urgency_str}"
            )
        else:
            return (
                f"Text analysis indicates {level.lower()} severity complaint. "
                f"Score: {score_display}/10. {urgency_str}"
            )

    # ─────────────────────────────────────────────────────────────────────────
    # CREDIBILITY EXPLANATION
    # ─────────────────────────────────────────────────────────────────────────

    def explain_credibility(self, features: list, score: float) -> str:
        """
        Returns a human-readable credibility explanation string.
        """
        score_display = round(score * 10, 2)

        if score < 0.3:
            return (
                f"Low credibility: insufficient detail provided. "
                f"Score: {score_display}/10. "
                "Consider requesting additional information from the citizen."
            )

        if features:
            features_str = ", ".join(features)
            return (
                f"Credibility score {score_display}/10. "
                f"Positive signals: {features_str}."
            )
        else:
            return (
                f"Credibility score {score_display}/10. "
                "Complaint accepted with basic validation."
            )

    # ─────────────────────────────────────────────────────────────────────────
    # PRIORITY EXPLANATION
    # ─────────────────────────────────────────────────────────────────────────

    def explain_priority(
        self,
        severity: float,
        credibility: float,
        label: str,
        emergency_override: bool,
    ) -> str:
        """
        Returns a human-readable priority decision explanation string.
        """
        computed_score = round(0.6 * severity + 0.4 * credibility, 4)
        override_note = ""
        if emergency_override:
            final = max(computed_score, 0.90)
            override_note = (
                f" Emergency override applied — score raised to {round(final, 2)} "
                f"(minimum 0.90 for emergency complaints)."
            )

        return (
            f"Priority {label} assigned. "
            f"Formula: 0.6 × {severity:.2f} + 0.4 × {credibility:.2f} = {computed_score:.2f}."
            f"{override_note}"
        )

    # ─────────────────────────────────────────────────────────────────────────
    # FULL EXPLANATION (combines all three)
    # ─────────────────────────────────────────────────────────────────────────

    def get_full_explanation(
        self,
        severity_result: dict,
        credibility_result: dict,
        priority_result: dict,
    ) -> dict:
        """
        Build complete explanation dict from severity, credibility, priority result dicts.

        Returns:
        {
            "severity_explanation": str,
            "credibility_explanation": str,
            "priority_explanation": str,
            "keywords_detected": list,
            "credibility_features": list,
            "ai_summary": str
        }
        """
        severity_score = severity_result.get("severity_score", 0.0)
        severity_keywords = severity_result.get("severity_keywords", [])
        severity_text = severity_result.get("explanation", "")

        credibility_score = credibility_result.get("credibility_score", 0.0)
        credibility_features = credibility_result.get("credibility_features", [])

        priority_label = priority_result.get("priority_label", "LOW")
        priority_score = priority_result.get("priority_score", 0.0)
        emergency_override = priority_result.get("emergency_override", False)

        # Build individual explanations
        sev_explanation = self.explain_severity("", severity_score, severity_keywords)
        cred_explanation = self.explain_credibility(credibility_features, credibility_score)
        pri_explanation = self.explain_priority(
            severity_score, credibility_score, priority_label, emergency_override
        )

        # Build compact ai_summary
        sev_display = round(severity_score * 10, 1)
        cred_display = round(credibility_score * 10, 1)
        pri_display = round(priority_score, 2)

        if emergency_override:
            ai_summary = (
                f"🚨 EMERGENCY OVERRIDE: {priority_label} priority. "
                f"Severity {sev_display}/10, Credibility {cred_display}/10. "
                f"Immediate response required."
            )
        else:
            ai_summary = (
                f"{priority_label} priority complaint. "
                f"Severity {sev_display}/10 | Credibility {cred_display}/10 | "
                f"Priority score {pri_display}."
            )

        return {
            "severity_explanation": sev_explanation,
            "credibility_explanation": cred_explanation,
            "priority_explanation": pri_explanation,
            "keywords_detected": severity_keywords,
            "credibility_features": credibility_features,
            "ai_summary": ai_summary,
        }


# Singleton instance
shap_explainer = SHAPExplainer()
