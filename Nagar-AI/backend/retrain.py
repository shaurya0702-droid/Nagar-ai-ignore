"""
NagarAI — Severity Model Retraining Script
===========================================
Use this script to retrain the severity model on a real-world dataset.

Usage:
    python retrain.py                          # uses data/complaints_labeled.csv
    python retrain.py --csv path/to/file.csv   # uses a custom CSV path
    python retrain.py --evaluate               # prints accuracy + confusion matrix

CSV format (UTF-8, with header row):
    text,severity_score
    "Gas leak detected near school",0.95
    "Park bench needs painting",0.08
    ...

Columns:
    text           — raw complaint text (any language, any script)
    severity_score — float 0.0–1.0 where:
                       0.85–1.0  = CRITICAL
                       0.60–0.84 = HIGH
                       0.35–0.59 = MEDIUM
                       0.00–0.34 = LOW

After running:
    The updated model takes effect on next server restart.
    No other files need to change.

Production accuracy targets:
    1,000 examples  → 88–91%
    5,000 examples  → 92–94%
    10,000+ examples → ~95%+
"""

import sys
import os
import csv
import argparse

# ── Make sure backend/ is on the path ──────────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def load_csv(csv_path: str) -> tuple:
    """Load text+severity_score from CSV. Returns (texts, scores)."""
    texts, scores = [], []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, 1):
            t = row.get("text", "").strip()
            s = row.get("severity_score", "").strip()
            if not t or not s:
                print(f"  ⚠️  Row {i}: skipping — missing text or score")
                continue
            try:
                scores.append(float(s))
                texts.append(t)
            except ValueError:
                print(f"  ⚠️  Row {i}: invalid score '{s}' — skipping")

    return texts, scores


def evaluate(model, texts: list, scores: list):
    """Print classification accuracy and per-class breakdown."""
    from sklearn.metrics import classification_report, confusion_matrix
    from ml.preprocessing import clean_text

    classes = [model._score_to_class(s) for s in scores]
    cleaned = [clean_text(t) for t in texts]

    X = model.vectorizer.transform(cleaned)
    preds = model.classifier.predict(X)

    label_names = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    print("\n─── Classification Report ───────────────────────────────")
    print(classification_report(classes, preds, target_names=label_names, zero_division=0))

    print("─── Confusion Matrix ────────────────────────────────────")
    print("         " + "  ".join(f"{n:8}" for n in label_names))
    for i, row in enumerate(confusion_matrix(classes, preds, labels=[0,1,2,3])):
        print(f"{label_names[i]:8} " + "  ".join(f"{v:8}" for v in row))

    correct = sum(1 for p, c in zip(preds, classes) if p == c)
    print(f"\nOverall accuracy: {correct}/{len(classes)} = {100*correct/len(classes):.1f}%")

    # Test a few signature complaints
    print("\n─── Spot-check predictions ──────────────────────────────")
    spot_checks = [
        ("Gas leak near school emergency children dizzy", "CRITICAL"),
        ("Live wire fallen on road people gathering dangerous", "CRITICAL"),
        ("Garbage not collected 3 days bins overflowing", "MEDIUM"),
        ("Park bench needs repair minor inconvenience", "LOW"),
        ("gas ki leakage ho rahi hai school ke paas bacche behosh", "CRITICAL"),
        ("Kachra teen din se nahi utha badbu aa rahi", "MEDIUM"),
    ]
    for text, expected in spot_checks:
        result = model.predict(text)
        score = result["severity_score_display"]
        override = "⚡ OVERRIDE" if result["emergency_override"] else ""
        kws = ", ".join(result["severity_keywords"][:3]) if result["severity_keywords"] else "none"
        print(f"  [{expected:8}] {score:4}/10  kw={kws[:30]:30}  {text[:55]} {override}")


def main():
    parser = argparse.ArgumentParser(description="Retrain NagarAI severity model")
    parser.add_argument("--csv", default=None, help="Path to labeled CSV (default: data/complaints_labeled.csv)")
    parser.add_argument("--evaluate", action="store_true", help="Print accuracy report after training")
    parser.add_argument("--sample", action="store_true", help="Train on sample CSV to test the pipeline")
    args = parser.parse_args()

    # ── Resolve CSV path ────────────────────────────────────────────────────
    base_dir = os.path.dirname(os.path.abspath(__file__))

    if args.sample:
        csv_path = os.path.join(base_dir, "data", "complaints_labeled_sample.csv")
        print(f"📄 Using sample CSV: {csv_path}")
    elif args.csv:
        csv_path = args.csv
    else:
        csv_path = os.path.join(base_dir, "data", "complaints_labeled.csv")

    if not os.path.exists(csv_path):
        print(f"\n❌ CSV not found: {csv_path}")
        print("\nTo use production data:")
        print("  1. Create data/complaints_labeled.csv with columns: text, severity_score")
        print("  2. Run: python retrain.py --evaluate")
        print("\nTo test with sample data:")
        print("  python retrain.py --sample --evaluate")
        sys.exit(1)

    # ── Load data ───────────────────────────────────────────────────────────
    print(f"\n📥 Loading: {csv_path}")
    texts, scores = load_csv(csv_path)
    print(f"   Loaded {len(texts)} valid examples")

    if len(texts) < 20:
        print(f"\n❌ Need at least 20 examples to train. Found {len(texts)}.")
        sys.exit(1)

    # ── Retrain ─────────────────────────────────────────────────────────────
    print("\n⚙️  Retraining severity model...")
    from ml.severity_model import SeverityModel
    model = SeverityModel.__new__(SeverityModel)
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    model.vectorizer = TfidfVectorizer(max_features=500, ngram_range=(1, 2), sublinear_tf=True)
    model.classifier = LogisticRegression(random_state=42, max_iter=1000, class_weight="balanced")
    model.is_trained = False

    # Override _get_training_data to use our CSV
    model._csv_texts  = texts
    model._csv_scores = scores
    model._get_training_data = lambda: (model._csv_texts, model._csv_scores)
    model._train()

    print(f"✅ Model retrained on {len(texts)} examples")
    print(f"   Class distribution:")
    for label, lo, hi in [("CRITICAL", 0.85, 1.0), ("HIGH", 0.60, 0.84),
                           ("MEDIUM", 0.35, 0.59), ("LOW", 0.0, 0.34)]:
        n = sum(1 for s in scores if lo <= s <= hi)
        print(f"     {label:8}: {n:4} examples")

    # ── Evaluate ────────────────────────────────────────────────────────────
    if args.evaluate:
        evaluate(model, texts, scores)

    print("\n─────────────────────────────────────────────────────────")
    print("✅ Retraining complete.")
    print()
    print("To apply in production:")
    print("  1. Copy your CSV to: backend/data/complaints_labeled.csv")
    print("  2. Restart the server: docker-compose restart backend")
    print("  3. The model auto-loads the CSV on startup.")
    print()
    print("No other files need to change.")


if __name__ == "__main__":
    main()
