"""
NagarAI — Authentication Routes
JWT-based login and officer identity endpoints.
"""

from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config import settings
from database.connection import get_db
from database.models import Officer

router = APIRouter()

# ─────────────────────────────────────────────────────────────────────────────
# SECURITY SETUP
# ─────────────────────────────────────────────────────────────────────────────

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# ─────────────────────────────────────────────────────────────────────────────
# PYDANTIC SCHEMAS
# ─────────────────────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    officer: dict


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def create_access_token(data: dict) -> str:
    """Create a JWT access token with expiry."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def get_current_officer(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Officer:
    """Decode JWT and return the authenticated officer, or raise 401."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: Optional[str] = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    officer = db.query(Officer).filter(Officer.email == email).first()
    if officer is None:
        raise credentials_exception
    return officer


def _officer_dict(officer: Officer) -> dict:
    """Serialize Officer for API response."""
    return {
        "id": officer.id,
        "name": officer.name,
        "email": officer.email,
        "role": officer.role,
        "ward_id": officer.ward_id,
    }


# ─────────────────────────────────────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate officer and return JWT access token."""
    officer = db.query(Officer).filter(Officer.email == request.email).first()

    if not officer or not verify_password(request.password, officer.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(data={"sub": officer.email})

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        officer=_officer_dict(officer),
    )


@router.get("/me")
def get_me(current_officer: Officer = Depends(get_current_officer)):
    """Return currently authenticated officer's profile."""
    return _officer_dict(current_officer)
