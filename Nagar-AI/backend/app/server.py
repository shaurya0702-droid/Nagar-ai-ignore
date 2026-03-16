"""
NagarAI — FastAPI Application Server
AI Municipal Decision Intelligence Platform — Delhi Municipal Intelligence
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from database.connection import create_tables
from routes import auth, complaints, analytics

app = FastAPI(
    title="NagarAI API",
    description="AI Municipal Decision Intelligence Platform — Delhi Municipal Intelligence",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS — allow all origins for demo ───────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(complaints.router, prefix="/complaints", tags=["Complaints"])
app.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])


# ── Startup event ─────────────────────────────────────────────────────────────
@app.on_event("startup")
async def startup_event():
    """Create tables on startup, seed demo data if DB is empty."""
    create_tables()
    try:
        from database.connection import SessionLocal
        from database.models import Officer
        db = SessionLocal()
        count = db.query(Officer).count()
        db.close()
        if count == 0:
            import subprocess
            import sys
            subprocess.run([sys.executable, "seed_data.py"], check=True)
            print("✅ Demo data seeded successfully")
        else:
            print(f"✅ DB ready — {count} officer(s) found")
    except Exception as e:
        print(f"⚠️ Seed data error (non-fatal): {e}")


# ── Health / root endpoints ───────────────────────────────────────────────────
@app.get("/", tags=["Root"])
def root():
    return {
        "status": "NagarAI API Running",
        "version": "1.0.0",
        "project": "AI Municipal Decision Intelligence Platform",
        "initiative": "Ministry of Urban Affairs, Government of India",
        "docs": "/docs",
    }


@app.get("/health", tags=["Root"])
def health():
    return {"status": "healthy", "service": "nagarai-backend"}
