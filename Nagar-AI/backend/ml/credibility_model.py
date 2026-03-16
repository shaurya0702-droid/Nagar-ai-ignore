"""
NagarAI — Credibility Assessment Model
Rule-based credibility scoring with TF-IDF spam detection.
"""

from typing import Optional

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from ml.preprocessing import (
    clean_text,
    is_spam,
    calculate_text_depth_score,
    has_location_mention,
    has_specific_details,
)

# Verb coherence indicators
_VERB_INDICATORS = [
    "is", "are", "was", "were", "has", "have", "been", "not working",
    "broken", "leaking", "blocked", "damaged", "overflowing", "collapsed",
    "fallen", "spreading", "flooding", "stinking", "causing", "affecting",
    "coming", "going", "happening",
]


class CredibilityModel:
    """
    Credibility assessment for citizen complaints.
    Combines spam detection with signal-based scoring.
    """

    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=200, ngram_range=(1, 1))
        self._spam_matrix = None
        self._genuine_texts = []
        self._fit_spam_detector()

    # ─────────────────────────────────────────────────────────────────────────
    # SPAM DETECTOR  (fit on 20 spam + 20 genuine examples)
    # ─────────────────────────────────────────────────────────────────────────

    def _fit_spam_detector(self):
        spam_texts = [
            "test test test",
            "aaaaaaaaa",
            "hello",
            "dummy complaint",
            "fake report nothing happened",
            "1234567890",
            "zzzzz",
            "hi hi hi",
            "testing testing",
            "please please please please please",
            "nothing",
            "xxx xxx xxx",
            "abc abc abc",
            "hey hey",
            "fake fake fake",
            "test123",
            "qqqqq",
            "lol lol lol",
            "blah blah blah",
            "dummy dummy",
        ]

        self._genuine_texts = [
            "Garbage pile has been growing for 3 days near main market stench unbearable",
            "Water pipe burst on main road flooding for 6 hours supply disrupted 200 households",
            "Large pothole on arterial road caused accident today vehicle damaged urgent repair",
            "All 12 street lights on sector 7 non-functional for 7 days women unsafe",
            "Illegal construction blocking emergency exit fire escape completely blocked elderly",
            "Underground water pipe leaking near junction sinkhole risk near misses",
            "Road collapse near bridge approach large section caved in traffic diverted",
            "Electric pole fell parked cars live wires exposed people gathering dangerously",
            "Water meter leaking ward 5 colony wastage reported twice meter needs replacement",
            "Stray dogs attacking pedestrians near school 3 children bitten this week",
            "Bridge approach road developed dangerous cracks heavy vehicles structural assessment",
            "Sewage overflow flooding residential area raw sewage entering homes children elderly",
            "Garbage collection stopped 8 days multiple residents complained bins overflowing",
            "Main water supply pipeline exposed road work contamination risk quality complaints",
            "Street light pole leaning dangerously lane 4 risk of falling",
            "Ward 1 sector 3 road severe potholes after rains 3 accidents impassable two-wheelers",
            "Water leakage overhead tank building 2 days overflow wasting thousands liters",
            "Abandoned building ward 6 used by miscreants residents afraid illegal activities",
            "Massive garbage fire dumpyard toxic smoke residential area respiratory problems",
            "Emergency water tanker required main supply cut 48 hours hospital running out",
        ]

        all_texts = spam_texts + self._genuine_texts
        cleaned = [clean_text(t) for t in all_texts]
        self.vectorizer.fit(cleaned)
        # Store genuine complaint matrix for duplicate detection
        genuine_cleaned = [clean_text(t) for t in self._genuine_texts]
        self._genuine_matrix = self.vectorizer.transform(genuine_cleaned)

    # ─────────────────────────────────────────────────────────────────────────
    # PREDICT  (main scoring)
    # ─────────────────────────────────────────────────────────────────────────

    def predict(
        self,
        text: str,
        category: str = "",
        ward: str = "",
        location: Optional[str] = None,
    ) -> dict:
        """
        Score credibility of a complaint.

        Signal weights:
          Spam check         → immediate 0.05 if spam
          Text depth         → 0.35
          Location mention   → 0.20
          Specific details   → 0.15
          Category provided  → 0.10
          Ward provided      → 0.10
          Text coherence     → 0.10

        Returns credibility_score (0–1), display (×10), features, spam flags.
        """
        # ── 1. Spam check ─────────────────────────────────────────────────
        spam_detected, spam_reason = is_spam(text)
        if spam_detected:
            return {
                "credibility_score": 0.05,
                "credibility_score_display": 0.5,
                "credibility_features": [],
                "is_spam": True,
                "spam_reason": spam_reason,
            }

        features_detected = []
        score = 0.0

        # ── 2. Text depth (weight 0.35) ───────────────────────────────────
        depth = calculate_text_depth_score(text)
        score += depth * 0.35
        if depth >= 0.7:
            features_detected.append("detailed description provided")
        elif depth >= 0.5:
            features_detected.append("adequate description length")
        else:
            features_detected.append("brief description")

        # ── 3. Location mention (weight 0.20) ─────────────────────────────
        if has_location_mention(text, location):
            score += 0.20
            features_detected.append("location mentioned")

        # ── 4. Specific details (weight 0.15) ─────────────────────────────
        if has_specific_details(text):
            score += 0.15
            features_detected.append("specific details or figures included")

        # ── 5. Category provided (weight 0.10) ────────────────────────────
        if category and category.strip():
            score += 0.10
            features_detected.append("category specified")

        # ── 6. Ward provided (weight 0.10) ────────────────────────────────
        if ward and ward.strip():
            score += 0.10
            features_detected.append("ward identified")

        # ── 7. Text coherence — verb indicators (weight 0.10) ─────────────
        lower = text.lower()
        coherent = any(vi in lower for vi in _VERB_INDICATORS)
        if coherent:
            score += 0.10
            features_detected.append("complaint is coherent and actionable")

        # ── Cap + round ────────────────────────────────────────────────────
        final_score = round(min(score, 1.0), 2)

        return {
            "credibility_score": final_score,
            "credibility_score_display": round(final_score * 10, 2),
            "credibility_features": features_detected,
            "is_spam": False,
            "spam_reason": None,
        }

    # ─────────────────────────────────────────────────────────────────────────
    # DUPLICATE DETECTION
    # ─────────────────────────────────────────────────────────────────────────

    def check_duplicate(self, text: str, existing_complaints: list) -> dict:
        """
        Compare text against existing complaints via TF-IDF cosine similarity.

        existing_complaints: list of dicts with keys 'id' and 'text'
        Returns {is_duplicate, similarity, duplicate_of_id}
        """
        no_dup = {"is_duplicate": False, "similarity": 0.0, "duplicate_of_id": None}

        if not existing_complaints:
            return no_dup

        if not text or not text.strip():
            return no_dup

        # Build corpus from existing complaints + new text
        existing_texts = [c.get("text", "") for c in existing_complaints]
        existing_ids = [c.get("id") for c in existing_complaints]

        try:
            # Fit a fresh vectorizer on the existing corpus + new text combined
            corpus = [clean_text(t) for t in existing_texts]
            new_clean = clean_text(text)

            # Use the fitted spam-detector vectorizer (already trained on varied vocab)
            # Re-transform everything using the shared vectorizer
            all_texts = corpus + [new_clean]
            matrix = self.vectorizer.transform(all_texts)

            existing_matrix = matrix[:-1]
            new_vector = matrix[-1]

            if existing_matrix.shape[0] == 0:
                return no_dup

            similarities = cosine_similarity(new_vector, existing_matrix)[0]
            max_idx = int(np.argmax(similarities))
            max_sim = float(similarities[max_idx])

            if max_sim > 0.80:
                return {
                    "is_duplicate": True,
                    "similarity": round(max_sim, 4),
                    "duplicate_of_id": existing_ids[max_idx],
                }
        except Exception:
            # Gracefully degrade — never crash the pipeline
            pass

        return no_dup


# Singleton — auto-trains on import
credibility_model = CredibilityModel()
