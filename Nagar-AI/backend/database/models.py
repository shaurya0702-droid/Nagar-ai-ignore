from sqlalchemy import (
    Column, Integer, String, Text, Float, Boolean, DateTime, JSON,
    ForeignKey, Index
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.connection import Base


class Officer(Base):
    __tablename__ = "officers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    ward_id = Column(Integer, nullable=True)
    role = Column(String(50), default="officer")
    created_at = Column(DateTime, server_default=func.now())

    complaints = relationship("Complaint", back_populates="assigned_officer")


class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, autoincrement=True)
    complaint_id = Column(String(20), unique=True, index=True)
    text = Column(Text, nullable=False)
    category = Column(String(100), nullable=False)
    ward_id = Column(Integer, nullable=False)
    ward_name = Column(String(50), nullable=False)
    location = Column(String(255), nullable=True)
    image_url = Column(String(500), nullable=True)
    severity_score = Column(Float, default=0.0)
    credibility_score = Column(Float, default=0.0)
    priority_score = Column(Float, default=0.0)
    priority_label = Column(String(20), default="LOW")
    status = Column(String(50), default="Pending")
    assigned_officer_id = Column(Integer, ForeignKey("officers.id"), nullable=True)
    is_duplicate = Column(Boolean, default=False)
    duplicate_of = Column(Integer, nullable=True)
    emergency_override = Column(Boolean, default=False)
    severity_keywords = Column(JSON, nullable=True)
    credibility_features = Column(JSON, nullable=True)
    sla_hours = Column(Integer, default=48)
    time_elapsed_hours = Column(Float, default=0.0)
    sla_breached = Column(Boolean, default=False)
    ai_recommendation = Column(Text, nullable=True)
    department = Column(String(100), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now(), nullable=True)

    assigned_officer = relationship("Officer", back_populates="complaints")


class Zone(Base):
    __tablename__ = "zones"

    id = Column(Integer, primary_key=True)
    ward_name = Column(String(50), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    description = Column(String(255), nullable=True)


class CitizenFeedback(Base):
    __tablename__ = "citizen_feedback"

    id = Column(Integer, primary_key=True, autoincrement=True)
    complaint_id = Column(String(20), nullable=False)
    rating = Column(Integer, nullable=False)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
