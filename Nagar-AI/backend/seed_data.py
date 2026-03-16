"""
NagarAI — Seed Data Script
Run: python seed_data.py  (from the backend/ directory)
"""

import sys
import os

# Ensure backend/ is on the path so imports resolve correctly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from passlib.context import CryptContext
from database.connection import SessionLocal, create_tables
from database.models import Officer, Complaint, Zone, CitizenFeedback

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ─────────────────────────────────────────────
# DEPARTMENT MAPPING
# ─────────────────────────────────────────────
DEPARTMENT_MAP = {
    "Emergency": "Disaster Management Cell",
    "Garbage Issue": "Sanitation Department",
    "Road Damage": "Public Works Department",
    "Water Leakage": "Jal Board",
    "Street Light Failure": "Electricity Department",
    "Public Safety": "Municipal Security & Police Coordination",
}


def calc_priority_score(severity_score: float, credibility_score: float, emergency_override: bool) -> float:
    if emergency_override:
        return round(severity_score / 10, 4)
    return round(0.6 * (severity_score / 10) + 0.4 * (credibility_score / 10), 4)


def main():
    # Ensure tables exist
    create_tables()

    db = SessionLocal()

    try:
        # Guard: do not re-seed
        if db.query(Officer).count() > 0:
            print("Data already seeded. Exiting.")
            return

        # ─────────────────────────────────────────────
        # OFFICERS
        # ─────────────────────────────────────────────
        officers = [
            Officer(
                name="Officer Amit Sharma",
                email="officer@nagarai.gov.in",
                password_hash=pwd_context.hash("NagarAI@123"),
                role="officer",
                ward_id=3,   # Karol Bagh
            ),
            Officer(
                name="Officer Priya Malhotra",
                email="officer@gov.in",
                password_hash=pwd_context.hash("123456"),
                role="officer",
                ward_id=2,   # Civil Lines
            ),
        ]
        db.add_all(officers)
        db.flush()  # get IDs without committing

        # ─────────────────────────────────────────────
        # ZONES — real Delhi locality coordinates
        # ─────────────────────────────────────────────
        zones = [
            Zone(id=1, ward_name="Connaught Place", latitude=28.6315, longitude=77.2167, description="Central Business District"),
            Zone(id=2, ward_name="Civil Lines",     latitude=28.6810, longitude=77.2290, description="North Delhi Administrative Zone"),
            Zone(id=3, ward_name="Karol Bagh",      latitude=28.6514, longitude=77.1907, description="West Delhi Commercial Hub"),
            Zone(id=4, ward_name="Rohini",          latitude=28.7384, longitude=77.1172, description="North-West Delhi Residential"),
            Zone(id=5, ward_name="Dwarka",          latitude=28.5921, longitude=77.0460, description="South-West Delhi Sector"),
            Zone(id=6, ward_name="Lajpat Nagar",    latitude=28.5700, longitude=77.2373, description="South Delhi Market Area"),
        ]
        db.add_all(zones)
        db.flush()

        # ─────────────────────────────────────────────
        # COMPLAINTS — raw data rows
        # Format: (idx, ward_id, ward_name, category, severity, credibility,
        #           label, status, emergency, sla_hrs, elapsed, sla_breached)
        # ward_name now uses locality names, not "Ward N"
        # ─────────────────────────────────────────────
        raw = [
            # 001
            (1,  3, "Karol Bagh",      "Emergency",            9.5, 8.0, "CRITICAL",  "Pending",     True,  6,  2.0,   False),
            # 002
            (2,  2, "Civil Lines",     "Garbage Issue",        6.4, 8.6, "HIGH",      "Pending",     False, 24, 30.0,  True),
            # 003
            (3,  5, "Dwarka",          "Water Leakage",        6.4, 6.6, "HIGH",      "Assigned",    False, 36, 18.0,  False),
            # 004
            (4,  1, "Connaught Place", "Road Damage",          6.7, 6.7, "HIGH",      "Pending",     False, 48, 52.0,  True),
            # 005
            (5,  4, "Rohini",          "Street Light Failure", 4.3, 8.8, "HIGH",      "Escalated",   False, 48, 170.0, True),
            # 006
            (6,  6, "Lajpat Nagar",   "Public Safety",        7.9, 8.9, "CRITICAL",  "Pending",     False, 12, 8.0,   False),
            # 007
            (7,  2, "Civil Lines",     "Water Leakage",        5.7, 8.4, "HIGH",      "Assigned",    False, 36, 12.0,  False),
            # 008
            (8,  3, "Karol Bagh",      "Road Damage",          4.4, 7.7, "HIGH",      "Pending",     False, 48, 96.0,  True),
            # 009
            (9,  1, "Connaught Place", "Emergency",            9.9, 9.5, "CRITICAL",  "In Progress", True,  6,  4.0,   False),
            # 010
            (10, 4, "Rohini",          "Road Damage",          2.2, 1.5, "LOW",       "Pending",     False, 96, 20.0,  False),
            # 011
            (11, 5, "Dwarka",          "Water Leakage",        5.8, 8.3, "HIGH",      "Pending",     False, 36, 6.0,   False),
            # 012
            (12, 6, "Lajpat Nagar",   "Garbage Issue",        5.0, 4.3, "MEDIUM",    "Pending",     False, 24, 48.0,  True),
            # 013
            (13, 3, "Karol Bagh",      "Public Safety",        9.5, 8.5, "CRITICAL",  "Pending",     True,  12, 10.0,  False),
            # 014
            (14, 6, "Lajpat Nagar",   "Road Damage",          9.5, 8.4, "CRITICAL",  "Assigned",    True,  48, 36.0,  False),
            # 015
            (15, 1, "Connaught Place", "Street Light Failure", 4.0, 6.7, "MEDIUM",    "Pending",     False, 48, 72.0,  True),
            # 016
            (16, 4, "Rohini",          "Emergency",            9.2, 8.6, "CRITICAL",  "Pending",     True,  6,  1.0,   False),
            # 017
            (17, 5, "Dwarka",          "Garbage Issue",        3.0, 8.8, "MEDIUM",    "Escalated",   False, 24, 192.0, True),
            # 018
            (18, 2, "Civil Lines",     "Water Leakage",        6.0, 7.7, "HIGH",      "In Progress", False, 36, 14.0,  False),
            # 019
            (19, 3, "Karol Bagh",      "Street Light Failure", 6.5, 1.0, "LOW",       "Pending",     False, 48, 25.0,  False),
            # 020
            (20, 1, "Connaught Place", "Road Damage",          2.1, 9.3, "MEDIUM",    "Pending",     False, 48, 120.0, True),
            # 021
            (21, 4, "Rohini",          "Water Leakage",        6.5, 8.3, "HIGH",      "Pending",     False, 36, 3.0,   False),
            # 022
            (22, 6, "Lajpat Nagar",   "Public Safety",        7.6, 7.4, "HIGH",      "Pending",     False, 12, 240.0, True),
            # 023
            (23, 3, "Karol Bagh",      "Garbage Issue",        9.1, 8.8, "CRITICAL",  "Pending",     True,  24, 56.0,  True),
            # 024
            (24, 5, "Dwarka",          "Emergency",            9.4, 7.2, "CRITICAL",  "Pending",     True,  6,  2.0,   False),
            # 025
            (25, 2, "Civil Lines",     "Street Light Failure", 4.5, 7.2, "MEDIUM",    "Pending",     False, 48, 16.0,  False),
        ]

        texts = [
            # 001 — Karol Bagh Emergency
            "Emergency! Gas leak detected near Karol Bagh market. Multiple residents reporting strong smell. Children in nearby school showing symptoms of dizziness.",
            # 002 — Civil Lines Garbage
            "Garbage pile has been growing for 3 days near Civil Lines main market. Stench is unbearable and attracting rats. Health hazard for nearby residents.",
            # 003 — Dwarka Water
            "Major water pipe burst on Dwarka main road. Water flowing for 6 hours, road waterlogged. Municipal water supply disrupted to 200+ households.",
            # 004 — Connaught Place Road
            "Large pothole on Connaught Place arterial road caused accident today. Vehicle damaged. Road is dangerous especially at night. Requires urgent repair.",
            # 005 — Rohini Street Light
            "All 12 street lights on Rohini sector 7 road have been non-functional for 7 days. Area completely dark at night, women feel unsafe, 2 chain snatching incidents reported.",
            # 006 — Lajpat Nagar Safety
            "Illegal construction blocking emergency exit of residential building in Lajpat Nagar. Fire escape completely blocked. Building has elderly and children residents.",
            # 007 — Civil Lines Water
            "Underground water pipe leaking near Civil Lines junction for 4 days. Road developing sinkhole risk. Multiple vehicles have had near misses.",
            # 008 — Karol Bagh Road
            "Road collapse near Karol Bagh bridge approach. Large section of road has caved in. Traffic diverted but area still risky.",
            # 009 — Connaught Place Emergency
            "URGENT: Electric pole fell on parked cars in Connaught Place. Live wires exposed on road. People gathering dangerously close. Need immediate response.",
            # 010 — Rohini Road LOW
            "Small crack on park pathway in Rohini. Not urgent but should be repaired eventually.",
            # 011 — Dwarka Water
            "Water meter leaking in Dwarka colony C block. Wastage of water. Has been reported twice before. Meter needs replacement.",
            # 012 — Lajpat Nagar Garbage
            "Garbage dumping happening at Lajpat Nagar park entrance. Residents dump garbage at night illegally.",
            # 013 — Karol Bagh Safety
            "Stray dogs attacking pedestrians near Karol Bagh school. 3 children bitten this week. Parents afraid to send children to school. Animal control needed urgently.",
            # 014 — Lajpat Nagar Road
            "Bridge approach road in Lajpat Nagar has developed dangerous cracks. Heavy vehicles using this route daily. Structural assessment needed before it fails completely.",
            # 015 — Connaught Place Street Light
            "Street lights near Connaught Place park not working for 3 days. Park area dark at night.",
            # 016 — Rohini Emergency
            "EMERGENCY: Sewage overflow flooding Rohini residential area. Raw sewage entering ground floor homes. Children and elderly at serious health risk. URGENT.",
            # 017 — Dwarka Garbage
            "Garbage collection stopped in Dwarka for 8 days. Multiple residents complained. Bins overflowing.",
            # 018 — Civil Lines Water
            "Main water supply pipeline exposed in Civil Lines due to road work. Risk of contamination if not covered. Water quality complaints from nearby residents.",
            # 019 — Karol Bagh Street Light
            "Street light pole leaning dangerously in Karol Bagh lane 4.",
            # 020 — Connaught Place Road
            "Entire Connaught Place sector 3 road has developed severe potholes after recent rains. 3 accidents reported. Road practically impassable for two-wheelers. Urgent repair needed.",
            # 021 — Rohini Water
            "Water leakage from overhead tank in Rohini building B. Overflow running for 2 days wasting thousands of liters.",
            # 022 — Lajpat Nagar Safety
            "Abandoned building in Lajpat Nagar being used by miscreants. Residents afraid. Illegal activities suspected. Children warned to stay away. Police and municipal action needed.",
            # 023 — Karol Bagh Garbage
            "URGENT: Massive garbage fire in Karol Bagh dumpyard. Toxic smoke spreading to nearby residential area. People with respiratory problems severely affected. Fire brigade needed.",
            # 024 — Dwarka Emergency
            "Emergency water tanker required in Dwarka. Main supply cut for 48 hours. Hospital nearby running out of water. Critical situation.",
            # 025 — Civil Lines Street Light
            "Several street lights blinking/not working near Civil Lines bus stop area for 2 weeks.",
        ]

        keywords_list = [
            ["gas", "leak", "emergency", "children"],
            ["garbage", "stench", "health hazard"],
            ["water", "burst", "pipe"],
            ["pothole", "accident", "dangerous"],
            ["dark", "unsafe", "incidents"],
            ["illegal", "fire escape", "blocked", "emergency"],
            ["sinkhole", "leaking", "risk"],
            ["collapse", "road", "risky"],
            ["electric", "live wires", "urgent", "dangerous"],
            ["crack"],
            ["leaking", "wastage"],
            ["garbage", "illegal"],
            ["attacking", "bitten", "danger", "children"],
            ["dangerous", "structural", "cracks", "bridge"],
            ["dark"],
            ["sewage", "flooding", "emergency", "health risk"],
            ["overflowing", "garbage"],
            ["contamination", "exposed", "pipeline"],
            ["leaning", "dangerously"],
            ["potholes", "accidents"],
            ["overflow", "waste", "leakage"],
            ["illegal", "miscreants", "unsafe"],
            ["fire", "toxic", "smoke", "urgent"],
            ["emergency", "hospital", "critical", "48 hours"],
            ["blinking", "not working"],
        ]

        features_list = [
            ["detailed description", "location mentioned", "specific symptoms"],
            ["specific duration mentioned", "location mentioned", "health impact described"],
            ["duration specified", "impact quantified"],
            ["incident reported", "location mentioned"],
            ["count specified", "duration mentioned", "incidents reported"],
            ["specific hazard described", "vulnerable residents mentioned"],
            ["duration specified", "safety risk noted"],
            ["specific location", "traffic impact described"],
            ["urgent tone", "specific incident", "immediate risk"],
            [],
            ["repeated complaint", "specific block mentioned"],
            [],
            ["incidents quantified", "specific location", "vulnerable group"],
            ["specific risk", "technical assessment demanded"],
            ["duration mentioned"],
            ["emergency flag", "vulnerable groups", "immediate impact"],
            ["duration specified", "multiple residents"],
            ["cause identified", "risk described"],
            [],
            ["incidents quantified", "thorough description", "urgency noted"],
            ["duration specified", "quantified waste"],
            ["community concern", "specific location"],
            ["health impact specific", "emergency indicated", "vulnerable affected"],
            ["hospital mentioned", "duration specified"],
            ["duration specified", "location mentioned"],
        ]

        complaints = []
        for i, row in enumerate(raw):
            idx, ward_id, ward_name, category, severity, credibility, label, status, emergency, sla_hrs, elapsed, sla_breached = row
            priority = calc_priority_score(severity, credibility, emergency)
            dept = DEPARTMENT_MAP.get(category, "General Department")
            complaint_id = f"CMP-2025-{idx:03d}"

            c = Complaint(
                complaint_id=complaint_id,
                text=texts[i],
                category=category,
                ward_id=ward_id,
                ward_name=ward_name,
                severity_score=severity,
                credibility_score=credibility,
                priority_score=priority,
                priority_label=label,
                status=status,
                emergency_override=emergency,
                sla_hours=sla_hrs,
                time_elapsed_hours=elapsed,
                sla_breached=sla_breached,
                severity_keywords=keywords_list[i],
                credibility_features=features_list[i],
                department=dept,
            )
            complaints.append(c)

        db.add_all(complaints)
        db.commit()

        print("Seeding complete: 25 complaints, 2 officers, 6 zones")

    except Exception as e:
        db.rollback()
        print(f"ERROR during seeding: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
