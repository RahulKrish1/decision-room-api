from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.dependencies import get_db
from app.core.security import hash_password, verify_password, create_access_token
from app.crud.users import get_user_by_email, create_user
from app.schemas.auth import SignupRequest, LoginRequest, TokenResponse, MeResponse
from app.core.dependencies_auth import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/signup", response_model=MeResponse, status_code=201)
def signup(payload: SignupRequest, db: Session = Depends(get_db)):
    existing = get_user_by_email(db, payload.email)
    if existing:
        raise HTTPException(status_code=409, detail="email_already_registered")

    try:
        user = create_user(db, email=payload.email, password_hash=hash_password(payload.password))
        return MeResponse(id=user.id, email=user.email)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="email_already_registered")

@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = get_user_by_email(db, payload.email)
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid_credentials")

    token = create_access_token(
        subject=str(user.id),
        secret=settings.jwt_secret,
        expires_minutes=settings.jwt_expires_minutes,
        extra_claims={"email": user.email},
    )
    return TokenResponse(access_token=token)

@router.get("/me", response_model=MeResponse)
def me(current_user = Depends(get_current_user)):
    return MeResponse(id=current_user.id, email=current_user.email)
