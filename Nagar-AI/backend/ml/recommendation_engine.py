"""
NagarAI — AI Recommendation Engine
Transforms raw complaint data into decision-ready intelligence for city officials.
"""

from typing import Optional


class RecommendationEngine:
    """
    Generates actionable recommendations for city officials based on complaint analysis.
    Transforms raw complaint data into decision-ready intelligence.
    """

    RECOMMENDATION_TEMPLATES = {
        "Emergency": {
            "action": "Deploy emergency response team immediately to {ward}",
            "base_impact": "Prevent potential disaster affecting {residents}+ residents",
            "authority": "Disaster Management Cell",
            "urgency": "IMMEDIATE",
        },
        "Garbage Issue": {
            "action": "Deploy sanitation crew to {ward} within 4 hours",
            "base_impact": "Reduce health hazard risk for {residents}+ residents",
            "authority": "Sanitation Department",
            "urgency": "SAME_DAY",
        },
        "Road Damage": {
            "action": "Dispatch Public Works repair team to {ward}",
            "base_impact": "Prevent accidents and restore safe traffic flow for {residents}+ commuters",
            "authority": "Public Works Department",
            "urgency": "WITHIN_48H",
        },
        "Water Leakage": {
            "action": "Send Jal Board emergency plumbing unit to {ward}",
            "base_impact": "Restore water supply and prevent contamination for {residents}+ households",
            "authority": "Jal Board",
            "urgency": "WITHIN_24H",
        },
        "Street Light Failure": {
            "action": "Dispatch electrical maintenance crew to {ward}",
            "base_impact": "Improve night safety for {residents}+ citizens, reduce crime risk",
            "authority": "Electricity Department",
            "urgency": "WITHIN_48H",
        },
        "Public Safety": {
            "action": "Coordinate Municipal Security and Police patrol to {ward}",
            "base_impact": "Ensure safety for {residents}+ residents in affected area",
            "authority": "Municipal Security & Police Coordination",
            "urgency": "WITHIN_24H",
        },
    }

    # Fallback template for unknown categories
    _DEFAULT_TEMPLATE = {
        "action": "Assign municipal officer to investigate and resolve issue in {ward}",
        "base_impact": "Address concern for {residents}+ affected residents",
        "authority": "General Administration",
        "urgency": "WITHIN_48H",
    }

    RESIDENT_ESTIMATES = {
        "CRITICAL": 500,
        "HIGH": 200,
        "MEDIUM": 100,
        "LOW": 50,
    }

    # ─────────────────────────────────────────────────────────────────────────
    # SINGLE COMPLAINT RECOMMENDATION
    # ─────────────────────────────────────────────────────────────────────────

    def generate_single(
        self,
        complaint_text: str,
        category: str,
        ward_name: str,
        priority_label: str,
        severity_score: float,
        credibility_score: float,
        severity_keywords: list,
        emergency_override: bool,
    ) -> dict:
        """
        Generate recommendation for a single complaint.

        Returns:
        {
            "action": str,
            "reason": str,
            "impact": str,
            "authority": str,
            "urgency": str,
            "ai_summary": str
        }
        """
        template = self.RECOMMENDATION_TEMPLATES.get(category, self._DEFAULT_TEMPLATE)
        residents = self.RESIDENT_ESTIMATES.get(priority_label, 100)

        # ── Build action string ───────────────────────────────────────────
        action = template["action"].format(ward=ward_name)
        if emergency_override:
            action = f"🚨 URGENT: {action}"

        # ── Build reason string ───────────────────────────────────────────
        sev_display = round(severity_score * 10, 1)
        cred_display = round(credibility_score * 10, 1)

        if severity_keywords:
            kw_str = ", ".join(severity_keywords[:4])
            reason = (
                f"AI detected keywords: {kw_str}. "
                f"Severity: {sev_display}/10. "
                f"High-credibility report — credibility: {cred_display}/10."
            )
        else:
            reason = (
                f"Complaint analysis scored severity at {sev_display}/10 "
                f"with credibility at {cred_display}/10. "
                f"Priority label: {priority_label}."
            )

        if emergency_override:
            reason = f"⚠️ Emergency override triggered. {reason}"

        # ── Build impact string ───────────────────────────────────────────
        impact_template = template["base_impact"].format(residents=residents)
        if emergency_override or priority_label == "CRITICAL":
            impact = (
                f"{impact_template}. "
                f"Could prevent health hazard for {residents}+ residents "
                f"and reduce escalation risk."
            )
        else:
            impact = f"{impact_template}."

        # ── Build ai_summary ─────────────────────────────────────────────
        urgency_label = template["urgency"].replace("_", " ")
        ai_summary = (
            f"{priority_label} priority {category} in {ward_name}. "
            f"{urgency_label} response by {template['authority']} recommended."
        )

        return {
            "action": action,
            "reason": reason,
            "impact": impact,
            "authority": template["authority"],
            "urgency": template["urgency"],
            "ai_summary": ai_summary,
        }

    # ─────────────────────────────────────────────────────────────────────────
    # WARD-LEVEL RECOMMENDATION
    # ─────────────────────────────────────────────────────────────────────────

    def generate_ward_recommendation(
        self,
        ward_name: str,
        complaints: list,
        ward_risk_score: float,
    ) -> dict:
        """
        Generate strategic recommendation for a ward based on complaint cluster.

        complaints: list of dicts with keys 'category', 'priority_label', 'count'
        Returns ward-level strategic recommendation dict.
        """
        if not complaints:
            return {
                "ward": ward_name,
                "risk_score": round(ward_risk_score, 3),
                "dominant_issue": "None",
                "recommended_action": "Monitor ward for incoming complaints",
                "reason": "No active complaints in this ward",
                "estimated_impact": "0 residents affected",
                "priority_teams": [],
            }

        # ── 1. Find dominant issue (most frequent category) ───────────────
        category_counts: dict = {}
        for c in complaints:
            cat = c.get("category", "General")
            count = c.get("count", 1)
            category_counts[cat] = category_counts.get(cat, 0) + count
        dominant_issue = max(category_counts, key=lambda k: category_counts[k])

        # ── 2. Count critical / high ──────────────────────────────────────
        critical_count = sum(
            c.get("count", 1)
            for c in complaints
            if c.get("priority_label") == "CRITICAL"
        )
        high_count = sum(
            c.get("count", 1)
            for c in complaints
            if c.get("priority_label") == "HIGH"
        )
        total_count = sum(c.get("count", 1) for c in complaints)

        # ── 3. Build recommended_action ───────────────────────────────────
        template = self.RECOMMENDATION_TEMPLATES.get(dominant_issue, self._DEFAULT_TEMPLATE)
        dominant_residents = self.RESIDENT_ESTIMATES.get("HIGH", 200)
        recommended_action = template["action"].format(
            ward=ward_name, residents=dominant_residents
        )

        # ── 4. Reason ─────────────────────────────────────────────────────
        reason = (
            f"{total_count} complaint(s) in {ward_name}, "
            f"{critical_count} CRITICAL, {high_count} HIGH. "
            f"Dominant issue: {dominant_issue}. "
            f"Ward risk score: {round(ward_risk_score, 2)}."
        )

        # ── 5. Estimated impact ────────────────────────────────────────────
        max_label = "CRITICAL" if critical_count > 0 else ("HIGH" if high_count > 0 else "MEDIUM")
        affected = self.RESIDENT_ESTIMATES.get(max_label, 100) * total_count
        estimated_impact = f"{affected}+ residents affected across {ward_name}"

        # ── 6. Priority teams (unique departments) ─────────────────────────
        seen_depts = set()
        priority_teams = []
        for c in complaints:
            cat = c.get("category", "")
            dept = self.RECOMMENDATION_TEMPLATES.get(
                cat, self._DEFAULT_TEMPLATE
            )["authority"]
            if dept not in seen_depts:
                priority_teams.append(dept)
                seen_depts.add(dept)

        return {
            "ward": ward_name,
            "risk_score": round(ward_risk_score, 3),
            "dominant_issue": dominant_issue,
            "recommended_action": recommended_action,
            "reason": reason,
            "estimated_impact": estimated_impact,
            "priority_teams": priority_teams,
        }

    # ─────────────────────────────────────────────────────────────────────────
    # CITY-LEVEL SUMMARY
    # ─────────────────────────────────────────────────────────────────────────

    def generate_city_summary(
        self,
        all_complaints: list,
        ward_risk_scores: dict,
        stats: dict,
    ) -> dict:
        """
        Generate city-level strategic recommendation summary.

        all_complaints: list of complaint dicts (must have 'priority_score', 'priority_label',
                        'category', 'ward_name', 'status', 'time_elapsed_hours')
        ward_risk_scores: {ward_name: risk_score}
        stats: dict with optional keys 'resolved_count', 'total_count', 'avg_elapsed_hours'

        Returns full city-level intelligence dict.
        """
        if not all_complaints:
            return {
                "city_health_index": 1.0,
                "city_health_label": "Excellent",
                "top_priority_ward": "N/A",
                "top_priority_action": "No active complaints",
                "total_citizens_at_risk": 0,
                "recommendations": [],
                "resource_deployment_plan": [],
                "transparency_score": 60.0,
            }

        # ── City health index ─────────────────────────────────────────────
        priority_scores = [
            c.get("priority_score", 0.0) for c in all_complaints
        ]
        avg_priority = sum(priority_scores) / len(priority_scores)
        city_health_index = round(1.0 - avg_priority, 4)

        # ── City health label ─────────────────────────────────────────────
        if city_health_index > 0.85:
            city_health_label = "Excellent"
        elif city_health_index > 0.70:
            city_health_label = "Good"
        elif city_health_index > 0.55:
            city_health_label = "Moderate Risk"
        elif city_health_index > 0.40:
            city_health_label = "High Risk"
        else:
            city_health_label = "Critical"

        # ── Top priority ward ─────────────────────────────────────────────
        top_priority_ward = "N/A"
        top_priority_action = "Monitor city complaints"
        if ward_risk_scores:
            top_priority_ward = max(ward_risk_scores, key=lambda w: ward_risk_scores[w])
            top_template = self._DEFAULT_TEMPLATE
            # Find most common category in top ward
            top_ward_complaints = [
                c for c in all_complaints
                if c.get("ward_name") == top_priority_ward
            ]
            if top_ward_complaints:
                cat_count: dict = {}
                for c in top_ward_complaints:
                    cat = c.get("category", "")
                    cat_count[cat] = cat_count.get(cat, 0) + 1
                top_cat = max(cat_count, key=lambda k: cat_count[k])
                top_template = self.RECOMMENDATION_TEMPLATES.get(
                    top_cat, self._DEFAULT_TEMPLATE
                )
            top_priority_action = top_template["action"].format(
                ward=top_priority_ward, residents=500
            )

        # ── Total citizens at risk ────────────────────────────────────────
        total_citizens_at_risk = 0
        for c in all_complaints:
            label = c.get("priority_label", "LOW")
            total_citizens_at_risk += self.RESIDENT_ESTIMATES.get(label, 50)

        # ── Top 3 ward recommendations ────────────────────────────────────
        sorted_wards = sorted(
            ward_risk_scores.items(), key=lambda x: x[1], reverse=True
        )[:3]

        recommendations = []
        for ward_name, risk_score in sorted_wards:
            ward_complaints = [
                c for c in all_complaints if c.get("ward_name") == ward_name
            ]
            # Build simplified complaints list for generate_ward_recommendation
            cat_count: dict = {}
            for c in ward_complaints:
                cat = c.get("category", "")
                label = c.get("priority_label", "LOW")
                key = (cat, label)
                cat_count[key] = cat_count.get(key, 0) + 1

            complaints_for_ward = [
                {"category": cat, "priority_label": label, "count": count}
                for (cat, label), count in cat_count.items()
            ]
            rec = self.generate_ward_recommendation(
                ward_name, complaints_for_ward, risk_score
            )
            recommendations.append(rec)

        # ── Resource deployment plan ──────────────────────────────────────
        resource_deployment_plan = []
        for ward_name, risk_score in sorted_wards:
            ward_complaints = [
                c for c in all_complaints if c.get("ward_name") == ward_name
            ]
            cat_count: dict = {}
            for c in ward_complaints:
                cat = c.get("category", "")
                cat_count[cat] = cat_count.get(cat, 0) + 1
            if not cat_count:
                continue
            top_cat = max(cat_count, key=lambda k: cat_count[k])
            tmpl = self.RECOMMENDATION_TEMPLATES.get(top_cat, self._DEFAULT_TEMPLATE)
            resource_deployment_plan.append({
                "team": tmpl["authority"],
                "ward": ward_name,
                "action": tmpl["action"].format(ward=ward_name, residents=200),
            })

        # ── Transparency score ────────────────────────────────────────────
        total_count = stats.get("total_count", len(all_complaints))
        resolved_count = stats.get("resolved_count", 0)
        avg_elapsed_hours = stats.get("avg_elapsed_hours", 24.0)

        transparency = 60.0
        if total_count > 0:
            resolution_rate = resolved_count / total_count
            transparency += resolution_rate * 25
        if avg_elapsed_hours > 0:
            speed_bonus = min((1.0 / avg_elapsed_hours) * 10, 15)
            transparency += speed_bonus

        transparency = round(min(transparency, 100.0), 1)

        return {
            "city_health_index": city_health_index,
            "city_health_label": city_health_label,
            "top_priority_ward": top_priority_ward,
            "top_priority_action": top_priority_action,
            "total_citizens_at_risk": total_citizens_at_risk,
            "recommendations": recommendations,
            "resource_deployment_plan": resource_deployment_plan,
            "transparency_score": transparency,
        }


# Singleton instance
recommendation_engine = RecommendationEngine()
