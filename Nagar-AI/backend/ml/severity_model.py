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
        self.vectorizer = TfidfVectorizer(max_features=500, ngram_range=(1, 2), sublinear_tf=True)
        self.classifier = LogisticRegression(random_state=42, max_iter=1000, class_weight="balanced")
        self.is_trained = False
        self._train()

    # ─────────────────────────────────────────────────────────────────────────
    # TRAINING DATA  (80+ examples embedded)
    # ─────────────────────────────────────────────────────────────────────────

    def _get_training_data(self) -> tuple:
        """
        Returns (texts, labels) read from external storage.
        """
        import os
        import csv
        texts, labels = [], []
        csv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "severity_training.csv")
        try:
            with open(csv_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    texts.append(row["text"])
                    labels.append(float(row["severity_score"]))
        except Exception as e:
            print(f"Warning: Could not load severity training data: {e}")
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
