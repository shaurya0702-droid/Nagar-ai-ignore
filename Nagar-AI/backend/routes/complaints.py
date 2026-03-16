"""
NagarAI — Complaint Routes
Full ML pipeline on submission, CRUD, stats, feedback.
"""

import json
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import desc, or_
from sqlalchemy.orm import Session

from database.connection import get_db
from database.models import Complaint, CitizenFeedback, Officer
from routes.auth import get_current_officer
from services.priority_engine import priority_engine

router = APIRouter()


# ─────────────────────────────────────────────────────────────────────────────
# PYDANTIC SCHEMAS
# ─────────────────────────────────────────────────────────────────────────────

class ComplaintCreate(BaseModel):
    text: str
    category: str
    ward_id: int
    ward_name: str
    location: Optional[str] = None


class ComplaintUpdate(BaseModel):
    status: Optional[str] = None
    assigned_officer_id: Optional[int] = None


class FeedbackCreate(BaseModel):
    complaint_id: str
    rating: int        # 1–5
    comment: Optional[str] = None


class RecalculateRequest(BaseModel):
    pass  # body not needed, but keeps schema consistent


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def generate_complaint_id(db: Session) -> str:
    """Generate a unique CMP-2025-NNN complaint ID."""
    count = db.query(Complaint).count()
    for attempt in range(200):   # try up to 200 collision avoidances
        candidate = f"CMP-2025-{count + 1 + attempt:03d}"
        exists = db.query(Complaint).filter(
            Complaint.complaint_id == candidate
        ).first()
        if not exists:
            return candidate
    # Fallback with timestamp suffix
    ts = int(datetime.utcnow().timestamp())
    return f"CMP-2025-{ts}"


def _serialize_complaint(complaint: Complaint) -> dict:
    """Convert Complaint ORM object to a clean dict, parsing ai_recommendation JSON."""
    ai_rec = None
    if complaint.ai_recommendation:
        try:
            ai_rec = json.loads(complaint.ai_recommendation)
        except (json.JSONDecodeError, TypeError):
            ai_rec = {"raw": complaint.ai_recommendation}

    return {
        "id": complaint.id,
        "complaint_id": complaint.complaint_id,
        "text": complaint.text,
        "category": complaint.category,
        "ward_id": complaint.ward_id,
        "ward_name": complaint.ward_name,
        "location": complaint.location,
        "image_url": complaint.image_url,
        "severity_score": complaint.severity_score,
        "credibility_score": complaint.credibility_score,
        "priority_score": complaint.priority_score,
        "priority_label": complaint.priority_label,
        "status": complaint.status,
        "assigned_officer_id": complaint.assigned_officer_id,
        "is_duplicate": complaint.is_duplicate,
        "duplicate_of": complaint.duplicate_of,
        "emergency_override": complaint.emergency_override,
        "severity_keywords": complaint.severity_keywords or [],
        "credibility_features": complaint.credibility_features or [],
        "sla_hours": complaint.sla_hours,
        "time_elapsed_hours": complaint.time_elapsed_hours,
        "sla_breached": complaint.sla_breached,
        "ai_recommendation": ai_rec,
        "department": complaint.department,
        "created_at": complaint.created_at.isoformat() if complaint.created_at else None,
        "updated_at": complaint.updated_at.isoformat() if complaint.updated_at else None,
    }


# ─────────────────────────────────────────────────────────────────────────────
# POST /complaints  — submit new complaint, run full ML pipeline
# ─────────────────────────────────────────────────────────────────────────────

@router.post("", status_code=status.HTTP_201_CREATED)
def create_complaint(payload: ComplaintCreate, db: Session = Depends(get_db)):
    """
    Submit a new citizen complaint.
    Runs the full ML pipeline: severity → credibility → priority → recommendation → explanation.
    """
    # Fetch existing complaints for duplicate check (text + id)
    existing_rows = db.query(Complaint.id, Complaint.text).all()
    existing_complaints = [{"id": row.id, "text": row.text} for row in existing_rows]

    # Run full ML pipeline
    analysis = priority_engine.analyze_complaint(
        text=payload.text,
        category=payload.category,
        ward=payload.ward_name,
        location=payload.location,
        existing_complaints=existing_complaints,
    )

    # Generate complaint ID
    complaint_id = generate_complaint_id(db)

    # Determine duplicate linkage
    duplicate_of_id = None
    if analysis["is_duplicate"] and analysis["duplicate_of_id"]:
        # Map internal DB id back to complaint sequential id
        duplicate_of_id = analysis["duplicate_of_id"]

    # Serialize recommendation dict to JSON string for storage
    rec_json = json.dumps(analysis["recommendation"]) if analysis.get("recommendation") else None

    complaint = Complaint(
        complaint_id=complaint_id,
        text=payload.text,
        category=payload.category,
        ward_id=payload.ward_id,
        ward_name=payload.ward_name,
        location=payload.location,
        severity_score=analysis["severity_score"],
        credibility_score=analysis["credibility_score"],
        priority_score=analysis["priority_score"],
        priority_label=analysis["priority_label"],
        status="Pending",
        emergency_override=analysis["emergency_override"],
        is_duplicate=analysis["is_duplicate"],
        duplicate_of=duplicate_of_id,
        severity_keywords=analysis["severity_keywords"],
        credibility_features=analysis["credibility_features"],
        sla_hours=analysis["sla_hours"],
        time_elapsed_hours=0.0,
        sla_breached=False,
        ai_recommendation=rec_json,
        department=analysis["department"],
    )

    db.add(complaint)
    db.commit()
    db.refresh(complaint)

    # Build full response — include analysis details
    response = _serialize_complaint(complaint)
    response["analysis"] = {
        "severity_score_display": analysis["severity_score_display"],
        "credibility_score_display": analysis["credibility_score_display"],
        "explanation": analysis.get("explanation", {}),
    }
    return response


# ─────────────────────────────────────────────────────────────────────────────
# GET /complaints  — list with filters
# ─────────────────────────────────────────────────────────────────────────────

@router.get("")
def list_complaints(
    ward: Optional[str] = Query(None, description="Filter by ward name"),
    priority: Optional[str] = Query(None, description="Filter by priority label"),
    status: Optional[str] = Query(None, description="Filter by status"),
    search: Optional[str] = Query(None, description="Full-text search on complaint text"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    _: Officer = Depends(get_current_officer),
):
    """List complaints with optional filters. Ordered by priority_score DESC, then created_at DESC."""
    query = db.query(Complaint)

    if ward:
        query = query.filter(Complaint.ward_name == ward)
    if priority:
        query = query.filter(Complaint.priority_label == priority.upper())
    if status:
        query = query.filter(Complaint.status == status)
    if search:
        query = query.filter(Complaint.text.ilike(f"%{search}%"))

    total = query.count()
    complaints = (
        query
        .order_by(desc(Complaint.priority_score), desc(Complaint.created_at))
        .offset(offset)
        .limit(limit)
        .all()
    )

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "complaints": [_serialize_complaint(c) for c in complaints],
    }


# ─────────────────────────────────────────────────────────────────────────────
# GET /complaints/stats/summary  — aggregated stats
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/stats/summary")
def get_stats_summary(
    db: Session = Depends(get_db),
    _: Officer = Depends(get_current_officer),
):
    """Return aggregated complaint statistics for the dashboard."""
    all_complaints = db.query(Complaint).all()
    total = len(all_complaints)

    critical = sum(1 for c in all_complaints if c.priority_label == "CRITICAL")
    high = sum(1 for c in all_complaints if c.priority_label == "HIGH")
    medium = sum(1 for c in all_complaints if c.priority_label == "MEDIUM")
    low = sum(1 for c in all_complaints if c.priority_label == "LOW")

    pending = sum(1 for c in all_complaints if c.status == "Pending")
    resolved = sum(1 for c in all_complaints if c.status == "Resolved")
    escalated = sum(1 for c in all_complaints if c.status == "Escalated")
    in_progress = sum(1 for c in all_complaints if c.status == "In Progress")
    assigned = sum(1 for c in all_complaints if c.status == "Assigned")

    sla_breached = sum(1 for c in all_complaints if c.sla_breached)
    emergency_overrides = sum(1 for c in all_complaints if c.emergency_override)

    return {
        "total": total,
        "critical": critical,
        "high": high,
        "medium": medium,
        "low": low,
        "pending": pending,
        "resolved": resolved,
        "escalated": escalated,
        "in_progress": in_progress,
        "assigned": assigned,
        "sla_breached": sla_breached,
        "emergency_overrides": emergency_overrides,
    }


# ─────────────────────────────────────────────────────────────────────────────
# GET /complaints/{complaint_id}  — single complaint
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/{complaint_id}")
def get_complaint(
    complaint_id: str,
    db: Session = Depends(get_db),
    _: Officer = Depends(get_current_officer),
):
    """Fetch a single complaint by its complaint_id (e.g. CMP-2025-001)."""
    complaint = db.query(Complaint).filter(
        Complaint.complaint_id == complaint_id
    ).first()

    if not complaint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Complaint {complaint_id} not found",
        )

    return _serialize_complaint(complaint)


# ─────────────────────────────────────────────────────────────────────────────
# PATCH /complaints/{complaint_id}  — update status / assigned officer
# ─────────────────────────────────────────────────────────────────────────────

@router.patch("/{complaint_id}")
def update_complaint(
    complaint_id: str,
    payload: ComplaintUpdate,
    db: Session = Depends(get_db),
    _: Officer = Depends(get_current_officer),
):
    """Update complaint status and/or assigned officer."""
    complaint = db.query(Complaint).filter(
        Complaint.complaint_id == complaint_id
    ).first()

    if not complaint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Complaint {complaint_id} not found",
        )

    if payload.status is not None:
        complaint.status = payload.status
    if payload.assigned_officer_id is not None:
        # Validate officer exists
        officer = db.query(Officer).filter(
            Officer.id == payload.assigned_officer_id
        ).first()
        if not officer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Officer {payload.assigned_officer_id} not found",
            )
        complaint.assigned_officer_id = payload.assigned_officer_id

    complaint.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(complaint)

    return _serialize_complaint(complaint)


# ─────────────────────────────────────────────────────────────────────────────
# POST /complaints/recalculate  — recalculate all priority scores
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/recalculate")
def recalculate_priorities(
    db: Session = Depends(get_db),
    _: Officer = Depends(get_current_officer),
):
    """
    Recalculate priority_score for ALL complaints using current engine weights.
    Useful after toggling Emergency Mode.
    """
    complaints = db.query(Complaint).all()
    sev_weight, cred_weight = priority_engine.get_weights()
    updated = 0

    for complaint in complaints:
        new_score = round(
            sev_weight * complaint.severity_score
            + cred_weight * complaint.credibility_score,
            4,
        )
        if complaint.emergency_override:
            new_score = max(new_score, 0.90)

        new_label = priority_engine.get_priority_label(new_score)

        complaint.priority_score = new_score
        complaint.priority_label = new_label
        complaint.sla_hours = priority_engine.get_sla_hours(new_label)
        complaint.updated_at = datetime.utcnow()
        updated += 1

    db.commit()

    return {
        "message": f"Recalculated priority scores for {updated} complaints",
        "updated_count": updated,
        "weights_used": {
            "severity_weight": sev_weight,
            "credibility_weight": cred_weight,
        },
        "emergency_mode": priority_engine.is_emergency_mode(),
    }


# ─────────────────────────────────────────────────────────────────────────────
# POST /complaints/{complaint_id}/feedback  — citizen feedback
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/{complaint_id}/feedback")
def submit_feedback(
    complaint_id: str,
    payload: FeedbackCreate,
    db: Session = Depends(get_db),
):
    """Submit citizen satisfaction feedback for a resolved complaint."""
    # Validate complaint exists
    complaint = db.query(Complaint).filter(
        Complaint.complaint_id == complaint_id
    ).first()
    if not complaint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Complaint {complaint_id} not found",
        )

    # Validate rating range
    if not (1 <= payload.rating <= 5):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Rating must be between 1 and 5",
        )

    feedback = CitizenFeedback(
        complaint_id=complaint_id,
        rating=payload.rating,
        comment=payload.comment,
    )
    db.add(feedback)
    db.commit()

    return {"message": "Feedback submitted", "complaint_id": complaint_id, "rating": payload.rating}
