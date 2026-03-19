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
        self.vectorizer = TfidfVectorizer(max_features=500, ngram_range=(1, 2), sublinear_tf=True)
        self._spam_matrix = None
        self._genuine_texts = []
        self._fit_spam_detector()

    # ─────────────────────────────────────────────────────────────────────────
    # SPAM DETECTOR  (fit on 20 spam + 20 genuine examples)
    # ─────────────────────────────────────────────────────────────────────────

    def _fit_spam_detector(self):
        import os
        import json
        json_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "credibility_training.json")
        spam_texts, genuine_texts = [], []
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                spam_texts = data.get("spam_texts", [])
                genuine_texts = data.get("genuine_texts", [])
        except Exception as e:
            print(f"Warning: Could not load credibility training data: {e}")
            
        self._genuine_texts = genuine_texts
        all_texts = spam_texts + genuine_texts
        if not all_texts:
            return  # Safety fallback
            
        cleaned = [clean_text(t) for t in all_texts]
        self.vectorizer.fit(cleaned)
        
        genuine_cleaned = [clean_text(t) for t in self._genuine_texts]
        if genuine_cleaned:
            self._genuine_matrix = self.vectorizer.transform(genuine_cleaned)
        else:
            self._genuine_matrix = None

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
