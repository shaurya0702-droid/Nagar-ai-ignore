import json
import random
import os

ZONES = [
    {"id": 1, "ward_name": "Connaught Place", "latitude": 28.6315, "longitude": 77.2167, "description": "Central Business District"},
    {"id": 2, "ward_name": "Civil Lines", "latitude": 28.6810, "longitude": 77.2290, "description": "North Delhi Administrative Zone"},
    {"id": 3, "ward_name": "Karol Bagh", "latitude": 28.6514, "longitude": 77.1907, "description": "West Delhi Commercial Hub"},
    {"id": 4, "ward_name": "Rohini", "latitude": 28.7384, "longitude": 77.1172, "description": "North-West Delhi Residential"},
    {"id": 5, "ward_name": "Dwarka", "latitude": 28.5921, "longitude": 77.0460, "description": "South-West Delhi Sector"},
    {"id": 6, "ward_name": "Lajpat Nagar", "latitude": 28.5700, "longitude": 77.2373, "description": "South Delhi Market Area"},
    {"id": 7, "ward_name": "Vasant Kunj", "latitude": 28.5293, "longitude": 77.1558, "description": "South West Delhi Upscale Residential"},
    {"id": 8, "ward_name": "Chandni Chowk", "latitude": 28.6505, "longitude": 77.2303, "description": "Old Delhi Historical Zone"},
    {"id": 9, "ward_name": "Okhla", "latitude": 28.5552, "longitude": 77.2828, "description": "South East Delhi Industrial Hub"},
    {"id": 10, "ward_name": "Pitampura", "latitude": 28.6981, "longitude": 77.1388, "description": "North-West Delhi Elite Residential"}
]

OFFICERS = [
    {"name": "Officer Amit Sharma", "email": "officer@nagarai.gov.in", "role": "officer", "ward_id": 3, "password": "NagarAI@123"},
    {"name": "Officer Priya Malhotra", "email": "officer2@gov.in", "role": "officer", "ward_id": 2, "password": "123456"},
    {"name": "Officer Rahul Verma", "email": "rahul.v@nagarai.gov.in", "role": "officer", "ward_id": 8, "password": "password123"},
    {"name": "Officer Sunita Rao", "email": "sunita.r@nagarai.gov.in", "role": "officer", "ward_id": 5, "password": "password123"},
    {"name": "Officer Vivek Singh", "email": "vivek.s@nagarai.gov.in", "role": "officer", "ward_id": 1, "password": "password123"}
]

DELHI_LANDMARKS = [
    "Red Fort", "India Gate", "Qutub Minar", "Lotus Temple", "Akshardham Temple", 
    "Jama Masjid", "Jantar Mantar", "Humayun's Tomb", "Rashtrapati Bhavan", 
    "Chandni Chowk Market", "Khari Baoli", "Sarojini Nagar Market", "Select Citywalk Mall"
]

COMPLAINT_TEMPLATES = {
    "Emergency": [
        "URGENT: Gas leak detected near {landmark} in {ward_name}. Multiple people complaining of dizziness.",
        "Major fire outbreak at an apartment building in {ward_name} near {landmark}. Smoke spreading rapidly.",
        "Live high-tension wire fell on the main road of {ward_name}. People are gathering, extreme electric shock danger.",
        "Sewage overflow flooding homes in {ward_name}. Raw sewage entering ground floor houses near {landmark}.",
        "Building collapse reported in narrow lane of {ward_name}. People trapped inside, urgent ambulance and rescue needed."
    ],
    "Garbage Issue": [
        "Massive garbage pile accumulating near {landmark} in {ward_name}. Rats and stray animals multiplying daily.",
        "Garbage collection stopped for 8 days in {ward_name}. Smell is unbearable to nearby households.",
        "Illegal garbage burning in an empty plot at {ward_name}. Toxic smoke is affecting residents.",
        "Bins overflowing for a week outside the market in {ward_name}. Serious health hazard.",
        "Stink from uncollected waste near {landmark} in {ward_name} has made it impossible to breathe."
    ],
    "Road Damage": [
        "Massive pothole causing accidents near {landmark} in {ward_name}. Motorbike damaged tonight.",
        "Road caved in near {ward_name} main junction. Sinkhole risk for passing traffic.",
        "Broken footpaths in {ward_name} making it hard for pedestrians. Multiple elderly have tripped.",
        "Large structural crack developed on the flyover approach in {ward_name}. Needs urgent assessment.",
        "Extensive potholes on the main road in {ward_name}. Causing huge traffic jams during rush hour."
    ],
    "Water Leakage": [
        "Major water pipe burst on {ward_name} main road. Water flooding the street for hours.",
        "Underground pipeline leak causing road to subside near {landmark} in {ward_name}.",
        "Contaminated, foul-smelling water coming from taps in {ward_name}. Health risk.",
        "Wastage of thousands of liters of water due to broken municipal tap in {ward_name}.",
        "Overhead tank leaking continuously for 3 days in {ward_name} public park."
    ],
    "Street Light Failure": [
        "Entire stretch of street lights off in {ward_name} for the past 5 days. Very dark and unsafe at night.",
        "Pole leaning dangerously ready to collapse in {ward_name} near {landmark}.",
        "Dim and flickering street lights in {ward_name} sector causing safety concerns for women commuting late.",
        "Wiring exposed at the base of the street light in {ward_name}. Risk of electric shock.",
        "Park lighting in {ward_name} not working, area totally unlit."
    ],
    "Public Safety": [
        "Stray monkey attacks increasing near {landmark} in {ward_name}. 5 children injured this week.",
        "Illegal construction blocking the fire exit of a residential building in {ward_name}.",
        "Abandoned building near {ward_name} market used for suspicious activities at night. Residents afraid.",
        "Dengue hotspot: Stagnant water pool near {ward_name} has become a mosquito breeding ground. Multiple cases reported.",
        "Uncovered deep manhole in {ward_name}. Someone could easily fall in at night."
    ]
}

def generate_complaints(num=100):
    complaints = []
    for i in range(num):
        zone = random.choice(ZONES)
        category = random.choice(list(COMPLAINT_TEMPLATES.keys()))
        template = random.choice(COMPLAINT_TEMPLATES[category])
        landmark = random.choice(DELHI_LANDMARKS)
        text = template.format(ward_name=zone["ward_name"], landmark=landmark)
        
        c = {
            "idx": i + 1,
            "ward_id": zone["id"],
            "ward_name": zone["ward_name"],
            "category": category,
            "text": text,
            "status": "Pending" if random.random() > 0.3 else "In Progress",
            "sla_hrs": random.choice([6, 12, 24, 48, 72]),
            "elapsed": round(random.uniform(1.0, 100.0), 1)
        }
        # Approximate values that models/rules would normally generate, but we provide mock seed base data:
        c["severity"] = round(random.uniform(8.0, 10.0) if category == "Emergency" else random.uniform(2.0, 8.5), 1)
        c["credibility"] = round(random.uniform(5.0, 9.5), 1)
        
        if c["severity"] >= 8.5: c["label"] = "CRITICAL"
        elif c["severity"] >= 6.0: c["label"] = "HIGH"
        elif c["severity"] >= 3.5: c["label"] = "MEDIUM"
        else: c["label"] = "LOW"
        
        c["emergency"] = (c["label"] == "CRITICAL" or category == "Emergency")
        c["sla_breached"] = c["elapsed"] > c["sla_hrs"]
        
        # Simple keywords for mock
        c["keywords"] = text.split()[:3]
        c["features"] = ["location mentioned"]
        
        complaints.append(c)
    return complaints

if __name__ == "__main__":
    data = {"zones": ZONES, "officers": OFFICERS, "complaints": generate_complaints(150)}
    path = os.path.join(os.path.dirname(__file__), "..", "data", "delhi_seed_data.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    print(f"Generated {len(data['complaints'])} complaints in {path}")
