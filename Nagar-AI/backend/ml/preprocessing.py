"""
NagarAI — ML Preprocessing Utilities
Shared constants and helper functions used across all ML modules.
"""

import re
import string
from typing import Optional


# ─────────────────────────────────────────────────────────────────────────────
# KEYWORD LISTS
# ─────────────────────────────────────────────────────────────────────────────

EMERGENCY_KEYWORDS = [
    "fire", "explosion", "gas leak", "flood", "collapse", "accident", "dead", "death",
    "hospital", "ambulance", "electric shock", "short circuit", "drowning", "riot",
    "violence", "shooting", "bomb", "bleeding", "unconscious", "sewage overflow",
    "building collapse", "live wire", "toxic", "poisoning", "earthquake",
]

HIGH_SEVERITY_KEYWORDS = [
    "danger", "urgent", "emergency", "critical", "severe", "hazard", "attack",
    "injury", "trapped", "smoke", "fire", "burst", "collapse", "overflow", "leak",
    "broken", "crack", "fall", "exposed", "contamination", "threat",
]

MEDIUM_SEVERITY_KEYWORDS = [
    "pothole", "garbage", "stench", "dark", "broken light", "water cut", "power cut",
    "blocked", "damaged", "dirty", "smell", "noise", "dust", "missing", "repair needed",
]

LOW_SEVERITY_KEYWORDS = [
    "request", "suggestion", "inconvenience", "minor", "small", "slight",
    "improve", "please", "kindly", "maintenance",
]

SPAM_PATTERNS = [
    r"^test",
    r"testing",
    r"^aaa+",
    r"^[0-9]+$",
    r"^(.)\1{4,}$",
    r"^(hello|hi|hey)[\s!]*$",
    r"^dummy",
    r"^fake",
]

DEPARTMENT_MAP = {
    "Emergency": "Disaster Management Cell",
    "Garbage Issue": "Sanitation Department",
    "Road Damage": "Public Works Department",
    "Water Leakage": "Jal Board",
    "Street Light Failure": "Electricity Department",
    "Public Safety": "Municipal Security & Police Coordination",
}

# Location indicator words
_LOCATION_WORDS = [
    "ward", "near", "opposite", "beside", "street", "road",
    "lane", "sector", "block", "colony", "area", "junction",
]

# Detail indicators
_DETAIL_WORDS = [
    "today", "yesterday", "morning", "night", "hours", "days",
    "minutes", "km", "meters",
]

# Verb coherence indicators
_VERB_INDICATORS = [
    "is", "are", "was", "were", "has", "have", "been", "not working",
    "broken", "leaking", "blocked", "damaged", "overflowing", "collapsed",
    "fallen", "spreading", "flooding", "stinking",
]


# ─────────────────────────────────────────────────────────────────────────────
# FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────

def clean_text(text: str) -> str:
    """Lowercase, remove special chars except spaces, strip whitespace."""
    if not text:
        return ""
    text = text.lower()
    # Keep letters, digits and spaces; remove everything else
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def detect_emergency_keywords(text: str) -> list:
    """Return list of EMERGENCY_KEYWORDS matched in text (case insensitive, word-boundary aware)."""
    lower = text.lower()
    matched = []
    for kw in EMERGENCY_KEYWORDS:
        # Multi-word keywords: use substring (e.g. "gas leak", "live wire")
        # Single-word keywords: word-boundary regex to avoid partial matches ("flood" != "flooding")
        if " " in kw:
            if kw in lower:
                matched.append(kw)
        else:
            if re.search(r"\b" + re.escape(kw) + r"\b", lower):
                matched.append(kw)
    return matched


def detect_severity_keywords(text: str) -> list:
    """
    Check against HIGH + MEDIUM + LOW severity keywords.
    Returns all matched keywords sorted by severity tier (high first).
    Uses word-boundary matching for single-word keywords.
    """
    lower = text.lower()

    def _match_kw(kw: str) -> bool:
        if " " in kw:
            return kw in lower
        return bool(re.search(r"\b" + re.escape(kw) + r"\b", lower))

    matched_high = [kw for kw in HIGH_SEVERITY_KEYWORDS if _match_kw(kw)]
    matched_medium = [kw for kw in MEDIUM_SEVERITY_KEYWORDS if _match_kw(kw)]
    matched_low = [kw for kw in LOW_SEVERITY_KEYWORDS if _match_kw(kw)]
    # High tier first, then medium, then low
    return matched_high + matched_medium + matched_low


def is_spam(text: str) -> tuple:
    """
    Check against SPAM_PATTERNS and word count < 3.
    Returns (is_spam: bool, reason: str).
    """
    if not text or not text.strip():
        return True, "Empty complaint text"

    stripped = text.strip()
    word_count = len(stripped.split())

    if word_count < 3:
        return True, f"Too short: only {word_count} word(s)"

    lower = stripped.lower()
    for pattern in SPAM_PATTERNS:
        if re.search(pattern, lower, re.IGNORECASE):
            return True, f"Matches spam pattern: '{pattern}'"

    return False, ""


def calculate_text_depth_score(text: str) -> float:
    """
    Word count scoring:
      < 5 words  → 0.1
      5–10       → 0.3
      10–20      → 0.5
      20–40      → 0.7
      40–60      → 0.85
      60+        → 1.0
    """
    if not text:
        return 0.1
    words = text.split()
    count = len(words)
    if count < 5:
        return 0.1
    elif count < 10:
        return 0.3
    elif count < 20:
        return 0.5
    elif count < 40:
        return 0.7
    elif count < 60:
        return 0.85
    else:
        return 1.0


def has_location_mention(text: str, location: Optional[str] = None) -> bool:
    """
    True if text contains location indicator words or location param is provided.
    """
    if location and location.strip():
        return True
    lower = text.lower()
    for word in _LOCATION_WORDS:
        if word in lower:
            return True
    return False


def has_specific_details(text: str) -> bool:
    """
    True if text contains numbers, dates or time references.
    """
    lower = text.lower()
    # Check for any digit
    if re.search(r"\d", lower):
        return True
    # Check detail words
    for word in _DETAIL_WORDS:
        if word in lower:
            return True
    return False


def get_department(category: str) -> str:
    """Return department for given category, default 'General Administration'."""
    return DEPARTMENT_MAP.get(category, "General Administration")
