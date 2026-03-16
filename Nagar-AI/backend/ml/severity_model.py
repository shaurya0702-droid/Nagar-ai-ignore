"""
NagarAI — Severity Detection Model
TF-IDF + Logistic Regression classifier auto-trained on embedded training data.
"""

import math
from typing import Optional

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import numpy as np

from ml.preprocessing import (
    clean_text,
    detect_emergency_keywords,
    detect_severity_keywords,
    EMERGENCY_KEYWORDS,
    HIGH_SEVERITY_KEYWORDS,
)


class SeverityModel:
    """
    Severity detection model for citizen complaints.
    Trained on embedded examples at import time — no external files required.
    """

    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=500, ngram_range=(1, 2))
        self.classifier = LogisticRegression(random_state=42, max_iter=1000)
        self.is_trained = False
        self._train()

    # ─────────────────────────────────────────────────────────────────────────
    # TRAINING DATA  (80+ examples embedded)
    # ─────────────────────────────────────────────────────────────────────────

    def _get_training_data(self) -> tuple:
        """
        Returns (texts, labels) where labels are float scores 0.0–1.0.
        """
        data = [
            # ── HIGH SEVERITY  (score 0.85–1.0) — 30 examples ───────────────
            ("Gas leak detected near school emergency children dizzy", 0.95),
            ("Building collapsed trapping residents inside rescue needed urgently", 0.98),
            ("Live electric wire fallen on road children nearby danger", 0.97),
            ("Fire in market area smoke spreading residents evacuating", 0.94),
            ("Sewage overflow flooding homes raw sewage entering ground floor", 0.91),
            ("Explosion heard near gas cylinder warehouse emergency response needed", 0.99),
            ("Dead body found near park emergency police ambulance needed", 0.95),
            ("Woman attacked near dark road at night violence bleeding", 0.88),
            ("Dengue outbreak suspected stagnant water multiple cases reported", 0.86),
            ("Road completely collapsed bridge approach vehicles trapped dangerous", 0.90),
            ("Electric pole fell on parked cars live wires exposed road", 0.96),
            ("Toxic chemical smell spreading from factory residents unconscious", 0.93),
            ("Flood water entering homes ground floor submerged emergency", 0.92),
            ("Massive garbage fire toxic smoke spreading hospital nearby", 0.91),
            ("Short circuit caused fire in residential building smoke everywhere", 0.93),
            ("Sewage pipe burst raw sewage flooding street health emergency", 0.89),
            ("Child fell into open manhole emergency ambulance required", 0.97),
            ("Gas cylinder explosion in apartment building residents trapped", 0.99),
            ("Man electrocuted by exposed wire near water pump area", 0.96),
            ("Riot erupting near market area violence spreading police needed", 0.92),
            ("Bridge structural crack heavy trucks passing collapse risk", 0.87),
            ("Stampede at market emergency crowd out of control injured", 0.94),
            ("Hospital water supply cut emergency patients at risk", 0.91),
            ("Landslide blocking road residents trapped no emergency access", 0.89),
            ("Live wire in standing water electrocution risk immediate danger", 0.98),
            ("Fire engine unable to reach building illegal construction blocking exit", 0.88),
            ("Drowning incident at waterlogged road urgent rescue needed", 0.95),
            ("Poisoning suspected from water supply multiple people hospitalized", 0.93),
            ("Earthquake tremors building crack residents evacuating emergency", 0.96),
            ("Bomb scare near public area police emergency evacuation needed", 0.99),

            # ── MEDIUM-HIGH SEVERITY  (score 0.60–0.84) — 25 examples ────────
            ("Large pothole caused accident today arterial road dangerous night", 0.72),
            ("Water pipe burst road flooded traffic completely disrupted", 0.68),
            ("All street lights failed entire area dark women feel unsafe", 0.65),
            ("Garbage fire started stench unbearable residents complaining health", 0.75),
            ("Illegal construction blocking fire exit emergency vehicle access blocked", 0.70),
            ("Underground water leak developing sinkhole near junction vehicles swerving", 0.73),
            ("Street light pole leaning dangerously could fall any moment", 0.66),
            ("Stray dogs attacking pedestrians three children bitten school area", 0.78),
            ("Pothole swallowed motorbike wheel accident rider injured hospital", 0.76),
            ("Water contamination suspected foul smell multiple residents sick", 0.74),
            ("Road cave-in near drainage area risk of vehicles falling", 0.71),
            ("Overhead tank overflow running for days wastage flooding lane", 0.63),
            ("Electrical transformer sparking near residential block fire risk", 0.80),
            ("Garbage pile attracting rodents disease risk children playing nearby", 0.67),
            ("Broken water main exposing pipeline contamination risk", 0.69),
            ("Collapsed retaining wall blocking footpath danger to pedestrians", 0.72),
            ("Manhole cover missing pedestrian fell in leg fracture reported", 0.79),
            ("Sewage smell in drinking water taps contamination complaint multiple", 0.77),
            ("Tree fallen on road blocking emergency vehicle access hospital route", 0.74),
            ("High tension wire sagging low over road vehicles touching risk", 0.82),
            ("Waterlogged underpass cars stalling people stranded dangerous", 0.64),
            ("Abandoned building being used by criminals residents fear safety", 0.66),
            ("Old building wall crumbling pedestrian risk collapse imminent", 0.71),
            ("Garbage truck not coming disease spreading stray animals multiplying", 0.62),
            ("Water meter burst wasting thousands liters road damaged sinkhole forming", 0.68),

            # ── MEDIUM SEVERITY  (score 0.35–0.59) — 20 examples ─────────────
            ("Garbage not collected for three days bins overflowing smell", 0.50),
            ("Road has potholes needs repair inconvenient for commuters", 0.45),
            ("Street light not working for a week area dark at night", 0.40),
            ("Water supply irregular in our area mornings no water comes", 0.42),
            ("Garbage bins overflowing near market stench in the area", 0.48),
            ("Footpath broken slabs loose pedestrians tripping maintenance needed", 0.43),
            ("Street lights flickering need maintenance electricity department", 0.38),
            ("Water leaking from municipal pipe for two days wastage", 0.46),
            ("Road drainage blocked water logging during rain every time", 0.44),
            ("Stray animals near school children scared daily problem", 0.52),
            ("Public toilet not cleaned in weeks unhygienic residents complaining", 0.50),
            ("Power cut lasting more than eight hours no response from board", 0.55),
            ("Parks have broken equipment children hurt playing needs repair", 0.44),
            ("Noise pollution from construction site all night residents disturbed", 0.47),
            ("Uneven road surface after construction team left it unfinished", 0.40),
            ("Open garbage dumping at park entrance health risk residents annoyed", 0.52),
            ("Street light pole rusted may fall needs replacement inspection", 0.48),
            ("Water billing wrong for three months need correction complaint", 0.36),
            ("Construction debris left on road narrow passage for vehicles", 0.43),
            ("Drainage ditch not covered pedestrians falling in at night", 0.55),

            # ── LOW SEVERITY  (score 0.0–0.34) — 15 examples ─────────────────
            ("Please improve the park benches they are old and uncomfortable", 0.10),
            ("Minor crack on footpath suggest repair when convenient", 0.15),
            ("Could you please plant more trees in our neighborhood area", 0.05),
            ("Request to improve the park lighting slightly dark at evening", 0.12),
            ("Kindly improve garbage collection timing slight inconvenience only", 0.08),
            ("Small pothole near society gate minor inconvenience suggestion", 0.18),
            ("Suggestion to add more benches in the garden maintenance request", 0.07),
            ("Water supply slightly low pressure request improvement if possible", 0.20),
            ("Please add speed bump near school small request for safety", 0.15),
            ("Maintenance request for park fountain not working minor issue", 0.10),
            ("Street sign faded request for new sign when work order available", 0.12),
            ("Slight delay in garbage collection today not major issue", 0.10),
            ("Paint on public wall peeling minor aesthetic improvement request", 0.08),
            ("Request better street naming boards in new residential area", 0.10),
            ("Footpath tiles slightly uneven minor improvement suggestion only", 0.14),
        ]

        texts = [item[0] for item in data]
        labels = [item[1] for item in data]
        return texts, labels

    # ─────────────────────────────────────────────────────────────────────────
    # TRAINING
    # ─────────────────────────────────────────────────────────────────────────

    def _score_to_class(self, score: float) -> int:
        """Map continuous score to one of 4 ordinal classes."""
        if score >= 0.85:
            return 3  # CRITICAL
        elif score >= 0.60:
            return 2  # HIGH
        elif score >= 0.35:
            return 1  # MEDIUM
        else:
            return 0  # LOW

    def _train(self):
        """Fit vectorizer + classifier on embedded training data."""
        texts, scores = self._get_training_data()
        classes = [self._score_to_class(s) for s in scores]

        cleaned = [clean_text(t) for t in texts]
        X = self.vectorizer.fit_transform(cleaned)
        self.classifier.fit(X, classes)
        self.is_trained = True

    # ─────────────────────────────────────────────────────────────────────────
    # PREDICTION
    # ─────────────────────────────────────────────────────────────────────────

    def predict(self, text: str) -> dict:
        """
        Predict severity for a complaint text.

        Returns:
        {
            "severity_score": float (0–1, 2 dp),
            "severity_score_display": float (×10 for display),
            "severity_keywords": list,
            "emergency_override": bool,
            "explanation": str
        }
        """
        if not text or not text.strip():
            return {
                "severity_score": 0.10,
                "severity_score_display": 1.0,
                "severity_keywords": [],
                "emergency_override": False,
                "explanation": "Empty or invalid complaint text.",
            }

        cleaned = clean_text(text)

        # ── 1. TF-IDF class prediction + probabilities ────────────────────
        X = self.vectorizer.transform([cleaned])
        proba = self.classifier.predict_proba(X)[0]  # [P(0), P(1), P(2), P(3)]

        # Weighted base score from class probabilities
        # class centres: 0→0.17, 1→0.47, 2→0.72, 3→0.92
        class_centres = [0.17, 0.47, 0.72, 0.92]
        base_score = sum(p * c for p, c in zip(proba, class_centres))

        # ── 2. Keyword detection ──────────────────────────────────────────
        emergency_kws = detect_emergency_keywords(text)
        severity_kws = detect_severity_keywords(text)
        all_keywords = list(dict.fromkeys(emergency_kws + severity_kws))  # deduplicated

        # ── 3. Keyword boosts and penalties ──────────────────────────────
        boost = 0.0
        from ml.preprocessing import LOW_SEVERITY_KEYWORDS, MEDIUM_SEVERITY_KEYWORDS

        for kw in emergency_kws:
            boost += 0.15  # +0.15 per emergency keyword
        for kw in severity_kws:
            if kw in HIGH_SEVERITY_KEYWORDS and kw not in emergency_kws:
                boost += 0.05  # +0.05 per high-severity keyword

        # Context-aware penalty:
        # If there are LOW-severity qualifier words AND no emergency signals,
        # apply a downward correction to prevent "minor crack" getting high scores.
        has_emergency_signal = bool(emergency_kws)
        low_kw_count = sum(1 for kw in severity_kws if kw in LOW_SEVERITY_KEYWORDS)
        high_kw_count = sum(
            1 for kw in severity_kws if kw in HIGH_SEVERITY_KEYWORDS
        ) + len(emergency_kws)

        if not has_emergency_signal and low_kw_count > 0:
            # Low keywords reduce score, but only when high signals are absent or weak
            if high_kw_count == 0:
                boost -= 0.12 * low_kw_count  # strong penalty when purely low
            elif low_kw_count >= high_kw_count:
                boost -= 0.06 * low_kw_count  # moderate penalty when low >= high signals

        # ── 4. Apply boost, cap at 0.98 ───────────────────────────────────
        final_score = min(base_score + boost, 0.98)
        final_score = max(round(final_score, 2), 0.01)

        # ── 5. Emergency override ─────────────────────────────────────────
        emergency_override = final_score > 0.85

        # ── 6. Explanation ────────────────────────────────────────────────
        if emergency_override:
            level = "CRITICAL — immediate response required"
        elif final_score >= 0.60:
            level = "HIGH — urgent attention needed"
        elif final_score >= 0.35:
            level = "MEDIUM — schedule for resolution"
        else:
            level = "LOW — routine maintenance"

        if all_keywords:
            explanation = (
                f"Severity score {round(final_score * 10, 2)}/10 detected. "
                f"Keywords found: {', '.join(all_keywords[:5])}. "
                f"{level}."
            )
        else:
            explanation = (
                f"Text analysis indicates {level.split('—')[0].strip().lower()} severity complaint. "
                f"Score: {round(final_score * 10, 2)}/10."
            )

        return {
            "severity_score": final_score,
            "severity_score_display": round(final_score * 10, 2),
            "severity_keywords": all_keywords,
            "emergency_override": emergency_override,
            "explanation": explanation,
        }


# Singleton — auto-trains on import
severity_model = SeverityModel()
