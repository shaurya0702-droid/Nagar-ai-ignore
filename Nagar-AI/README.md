# नागरAI NagarAI — AI Municipal Decision Intelligence Platform

> **Smart India Hackathon 2025** | Ministry of Urban Affairs, Government of India

---

## Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────────┐
│                           CITIZEN / OFFICER                          │
└───────────────────────────────┬──────────────────────────────────────┘
                                │  http://localhost:3000
                                ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    NGINX (Frontend Container)                        │
│                                                                      │
│   /          → serves static HTML/CSS/JS (index, complaint,         │
│                 dashboard, transparency, login)                      │
│                                                                      │
│   /api/*     → proxy_pass → backend:8000  (strips /api prefix)      │
│   /health    → proxy_pass → backend:8000/health                     │
│   /docs      → proxy_pass → backend:8000/docs                       │
└───────────┬──────────────────────────────────────────────────────────┘
            │  internal docker network (nagarai-net)
            ▼
┌──────────────────────────────────────────────────────────────────────┐
│                   FASTAPI BACKEND (backend:8000)                     │
│                                                                      │
│   /auth/*        → JWT authentication                                │
│   /complaints/*  → CRUD + ML pipeline per submission                 │
│   /analytics/*   → ward stats, heatmap, city intelligence            │
│   /health        → healthcheck endpoint                              │
│                                                                      │
│   ┌──────────────── ML PIPELINE ──────────────────────────────────┐  │
│   │                                                               │  │
│   │  ┌────────────────┐    ┌──────────────────┐                  │  │
│   │  │  सुरक्षित       │    │  विश्वास           │                  │  │
│   │  │  Surakshit     │    │  Vishwas          │                  │  │
│   │  │  Severity Model│    │  Credibility Model│                  │  │
│   │  │  TF-IDF + LR   │    │  6-signal scoring │                  │  │
│   │  │  0–10 score    │    │  0–10 score       │                  │  │
│   │  └───────┬────────┘    └────────┬──────────┘                  │  │
│   │          │                      │                             │  │
│   │          └──────────┬───────────┘                             │  │
│   │                     ▼                                         │  │
│   │  ┌──────────────────────────────────┐                         │  │
│   │  │  प्राथमिक  Prathmik               │                         │  │
│   │  │  Priority Engine                 │                         │  │
│   │  │  score = 0.6×sev + 0.4×cred     │                         │  │
│   │  │  Labels: CRITICAL/HIGH/MED/LOW   │                         │  │
│   │  │  SLA: 6/36/48/96 hours           │                         │  │
│   │  └──────────────────────────────────┘                         │  │
│   │                     │                                         │  │
│   │                     ▼                                         │  │
│   │  ┌──────────────────────────────────┐                         │  │
│   │  │  निरीक्षण  Nirikshan              │                         │  │
│   │  │  Recommendation Engine           │                         │  │
│   │  │  Ward risk scores                │                         │  │
│   │  │  City health index               │                         │  │
│   │  │  Resource deployment plan        │                         │  │
│   │  └──────────────────────────────────┘                         │  │
│   └───────────────────────────────────────────────────────────────┘  │
│                                                                      │
└───────────┬──────────────────────────────────────────────────────────┘
            │  internal docker network (nagarai-net)
            ▼
┌──────────────────────────────────────────────────────────────────────┐
│                PostgreSQL (postgres:5432)                            │
│                                                                      │
│   officers          complaints        zones                          │
│   citizen_feedback                                                   │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Project Structure

```
nagarai/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py          # Pydantic settings
│   │   └── server.py          # FastAPI app + CORS + startup
│   ├── database/
│   │   ├── connection.py      # SQLAlchemy engine + SessionLocal
│   │   └── models.py          # ORM: Officer, Complaint, Zone, CitizenFeedback
│   ├── ml/
│   │   ├── preprocessing.py   # Text cleaning, keyword detection
│   │   ├── severity_model.py  # Surakshit — TF-IDF + LogisticRegression
│   │   ├── credibility_model.py # Vishwas — 6-signal credibility
│   │   ├── recommendation_engine.py # Nirikshan — city intelligence
│   │   └── shap_explain.py    # SHAP explainability
│   ├── services/
│   │   └── priority_engine.py # Prathmik — orchestrator
│   ├── routes/
│   │   ├── auth.py            # POST /auth/login, GET /auth/me
│   │   ├── complaints.py      # CRUD + ML + feedback
│   │   └── analytics.py       # Analytics, heatmap, emergency mode
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── seed_data.py
│   └── .env.example
│
├── frontend/
│   ├── css/styles.css         # Complete 960-line government design system
│   ├── js/
│   │   ├── api.js             # API client + 25 demo complaints fallback
│   │   ├── auth.js            # Login, requireAuth, logout, font size
│   │   ├── charts.js          # 6 Chart.js chart functions
│   │   ├── heatmap.js         # Leaflet map controller
│   │   └── dashboard.js       # Full dashboard controller (~800 lines)
│   ├── index.html             # Landing page
│   ├── complaint.html         # Citizen complaint + track + feedback
│   ├── login.html             # Officer authentication
│   ├── dashboard.html         # Officer command dashboard (6 tabs)
│   ├── transparency.html      # Public transparency portal
│   ├── nginx.conf             # Nginx config (used by Dockerfile)
│   └── Dockerfile             # nginx:1.25-alpine static server
│
├── nginx/
│   └── nginx.conf             # Master nginx config (also copied to frontend/)
│
├── docker-compose.yml         # Production deployment
├── docker-compose.dev.yml     # Dev override (volume mount + --reload)
└── README.md
```

---

## AI Modules

| Module | Hindi | Function | Model |
|--------|-------|----------|-------|
| Safety Intelligence | सुरक्षित Surakshit | NLP severity scoring, emergency override | TF-IDF + LogisticRegression, 90 training examples |
| Credibility Assessment | विश्वास Vishwas | Spam filter, duplicate detection, 6-signal scoring | TF-IDF cosine similarity (threshold 0.80) |
| Priority Engine | प्राथमिक Prathmik | Weighted score + SLA + escalation | `0.6×severity + 0.4×credibility` (emergency: `0.8×0.2`) |
| City Intelligence | निरीक्षण Nirikshan | Ward risk, spike detection, deployment plan | Ward risk aggregation + recommendation templates |

---

## API Reference

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/auth/login` | — | Officer login → JWT token |
| GET | `/auth/me` | ✅ JWT | Current officer info |
| POST | `/complaints` | — | Submit complaint → full ML analysis |
| GET | `/complaints` | ✅ | List with filters (ward, priority, status, search) |
| GET | `/complaints/stats/summary` | ✅ | Dashboard stats counts |
| GET | `/complaints/{id}` | ✅ | Single complaint detail |
| PATCH | `/complaints/{id}` | ✅ | Update status / assigned officer |
| POST | `/complaints/recalculate` | ✅ | Rerun ML on all complaints |
| POST | `/complaints/{id}/feedback` | — | Citizen star rating |
| GET | `/analytics` | ✅ | Full analytics bundle |
| GET | `/analytics/heatmap` | ✅ | Ward density data |
| POST | `/analytics/emergency-mode` | ✅ | Toggle emergency weight mode |
| GET | `/health` | — | Container healthcheck |

> **Note:** All `/api/*` requests from the frontend are proxied by Nginx to the backend.
> The backend routes start at `/auth`, `/complaints`, `/analytics` (Nginx strips the `/api` prefix).

---

## Priority Labels

| Label | Score Range | SLA | Default Weights |
|-------|-------------|-----|-----------------|
| CRITICAL | ≥ 0.75 | 6 hours | 0.6 × severity + 0.4 × credibility |
| HIGH | ≥ 0.55 | 36 hours | (same) |
| MEDIUM | ≥ 0.35 | 48 hours | (same) |
| LOW | < 0.35 | 96 hours | (same) |
| Emergency Override | sev > 0.85 | 6 hours | 0.8 × severity + 0.2 × credibility |

---

## Demo Credentials

| Email | Password | Ward |
|-------|----------|------|
| `officer@nagarai.gov.in` | `NagarAI@123` | Ward 1 |
| `officer@gov.in` | `123456` | Ward 2 |

---

## Deployment Guide

### Prerequisites

- Docker ≥ 24.0
- Docker Compose ≥ 2.20

### Production (no hot-reload, no volume mount)

```bash
git clone <repo>
cd nagarai

# Build and start all 3 containers
docker-compose up --build -d

# Check container health
docker-compose ps

# View logs
docker-compose logs -f
```

Expected containers:
```
nagarai-postgres   → port 5432
nagarai-backend    → port 8000
nagarai-frontend   → port 3000 (nginx → proxies /api/ to backend)
```

### Development (hot-reload)

```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build
```

This enables:
- `--reload` on uvicorn (backend hot-reload)
- `./backend` volume mount (live code changes without rebuild)

---

## Deployment Test Checklist

After `docker-compose up --build`, run these tests in order:

### Test 1 — Backend Health
```
GET http://localhost:8000/health
```
Expected:
```json
{"status": "healthy", "service": "nagarai-backend"}
```

### Test 2 — API Documentation
```
http://localhost:8000/docs
```
Swagger UI should load with all endpoints.

### Test 3 — Frontend Landing Page
```
http://localhost:3000
```
NagarAI landing page should appear with government stripe, navbar, hero section.

### Test 4 — Nginx API Proxy
```
http://localhost:3000/api/health
```
Expected (proxied through nginx):
```json
{"status": "healthy", "service": "nagarai-backend"}
```

### Test 5 — Officer Login
```
http://localhost:3000/login.html
Email:    officer@gov.in
Password: 123456
```
Should redirect to `dashboard.html`.

### Test 6 — ML Pipeline (Critical complaint)
Submit via `http://localhost:3000/complaint.html`:
```
Category:    Emergency
Ward:        Ward 3
Description: Gas leak detected near school. Children showing dizziness symptoms. Emergency response needed immediately.
```
Expected result:
```
Priority:  CRITICAL
Score:     9.x / 10
Urgency:   IMMEDIATE
Authority: Disaster Management Cell
Action:    🚨 URGENT: Deploy emergency response team...
```

### Test 7 — Transparency Portal
```
http://localhost:3000/transparency.html
```
City Transparency Score, ward rankings, and charts should all load.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | HTML5, CSS3, Vanilla JS |
| Fonts | Syne (headings), DM Sans (body), JetBrains Mono (code) |
| Charts | Chart.js 4.4 |
| Map | Leaflet.js 1.9 + CartoDB dark tiles |
| Backend | FastAPI 0.104, Python 3.11 |
| ML | scikit-learn 1.3 (TF-IDF, LogisticRegression) |
| ORM | SQLAlchemy 2.0 |
| Database | PostgreSQL 15 |
| Auth | JWT (python-jose) + bcrypt (passlib) |
| Container | Docker + Nginx 1.25-alpine |

---

## Known Fixes Applied (vs initial build)

| # | Issue | Fix |
|---|-------|-----|
| 1 | Frontend `API_BASE` was `http://localhost:8000` — bypassed nginx | Changed to auto-detect: uses `/api` when served on port 3000, fallback to `localhost:8000` for local dev |
| 2 | Nginx `proxy_pass` hostname correctness | Confirmed: service name is `backend`, Docker DNS resolves correctly ✅ |
| 3 | `nginx.conf` started with `nginxserver {` (invalid syntax) | Fixed to `server {` — nginx would have crashed on startup otherwise |
| 4 | `uvicorn --reload` in production Docker | Removed `--reload` from production; moved to `docker-compose.dev.yml` only |
| 5 | `volumes: ./backend:/app` overrode Dockerfile COPY in production | Volumes now dev-only (`docker-compose.dev.yml`); production uses COPY'd code |
| 6 | Missing `include /etc/nginx/mime.types` | Added — fonts, JSON, JS files now served with correct Content-Type |

---

*© 2025 NagarAI — Ministry of Urban Affairs, Government of India | Smart India Hackathon 2025 Prototype*
