"""
NagarAI — Seed Data Script (Dynamic JSON/YAML driven)
Run: python seed_data.py  (from the backend/ directory)
"""
import sys
import os
import json
import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from passlib.context import CryptContext
from database.connection import SessionLocal, create_tables
from database.models import Officer, Complaint, Zone, CitizenFeedback

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def calc_priority_score(severity_score: float, credibility_score: float, emergency_override: bool) -> float:
    if emergency_override:
        return round(severity_score / 10, 4)
    return round(0.6 * (severity_score / 10) + 0.4 * (credibility_score / 10), 4)

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def load_seed_data():
    data_path = os.path.join(os.path.dirname(__file__), "data", "delhi_seed_data.json")
    with open(data_path, "r", encoding="utf-8") as f:
        return json.load(f)

def main():
    create_tables()
    db = SessionLocal()
    try:
        config = load_config()
        dept_map = config.get("department_map", {})
        
        if db.query(Officer).count() > 0:
            print("Data already seeded. Exiting.")
            return

        seed_data = load_seed_data()
        
        # Parse Zones
        zones = []
        for z in seed_data.get("zones", []):
            zones.append(Zone(id=z["id"], ward_name=z["ward_name"], latitude=z["latitude"], longitude=z["longitude"], description=z["description"]))
        db.add_all(zones)
        db.flush()

        # Parse Officers
        officers = []
        for o in seed_data.get("officers", []):
            officers.append(Officer(
                name=o["name"],
                email=o["email"],
                password_hash=pwd_context.hash(o["password"]),
                role=o["role"],
                ward_id=o["ward_id"]
            ))
        db.add_all(officers)
        db.flush()

        # Parse Complaints
        complaints = []
        for c_data in seed_data.get("complaints", []):
            priority = calc_priority_score(c_data["severity"], c_data["credibility"], c_data["emergency"])
            dept = dept_map.get(c_data["category"], "General Department")
            complaint_id = f"CMP-2025-{c_data['idx']:03d}"

            c = Complaint(
                complaint_id=complaint_id,
                text=c_data["text"],
                category=c_data["category"],
                ward_id=c_data["ward_id"],
                ward_name=c_data["ward_name"],
                severity_score=c_data["severity"],
                credibility_score=c_data["credibility"],
                priority_score=priority,
                priority_label=c_data["label"],
                status=c_data["status"],
                emergency_override=c_data["emergency"],
                sla_hours=c_data["sla_hrs"],
                time_elapsed_hours=c_data["elapsed"],
                sla_breached=c_data["sla_breached"],
                severity_keywords=c_data.get("keywords", []),
                credibility_features=c_data.get("features", []),
                department=dept,
            )
            complaints.append(c)
        db.add_all(complaints)
        db.commit()

        print(f"Seeding complete: {len(complaints)} complaints, {len(officers)} officers, {len(zones)} zones")

    except Exception as e:
        db.rollback()
        print(f"ERROR during seeding: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()
