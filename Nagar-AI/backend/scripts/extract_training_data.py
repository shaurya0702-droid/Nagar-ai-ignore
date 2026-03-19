import os
import csv
import json

base_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

severity_data = [
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

spam_texts = [
    "test test test", "aaaaaaaaa", "hello", "dummy complaint",
    "fake report nothing happened", "1234567890", "zzzzz", "hi hi hi",
    "testing testing", "please please please please please", "nothing",
    "xxx xxx xxx", "abc abc abc", "hey hey", "fake fake fake",
    "test123", "qqqqq", "lol lol lol", "blah blah blah", "dummy dummy"
]

genuine_texts = [
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

def export_data():
    with open(os.path.join(base_dir, "severity_training.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["text", "severity_score"])
        for text, score in severity_data:
            w.writerow([text, score])
            
    with open(os.path.join(base_dir, "credibility_training.json"), "w", encoding="utf-8") as f:
        json.dump({"spam_texts": spam_texts, "genuine_texts": genuine_texts}, f, indent=4)

if __name__ == "__main__":
    export_data()
