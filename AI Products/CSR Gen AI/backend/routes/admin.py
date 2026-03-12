"""Admin routes: user management."""

import secrets

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..auth import hash_password
from ..database import get_db
from ..deps import require_admin
from ..models import User
from ..schemas import UserOut, CreateUserRequest, UpdateUserRequest

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    users = db.query(User).order_by(User.created_at.desc()).all()
    return [UserOut.model_validate(u) for u in users]


@router.post("/users")
def create_user(
    body: CreateUserRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    if db.query(User).filter(User.username == body.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    if db.query(User).filter(User.email == body.email).first():
        raise HTTPException(status_code=400, detail="Email already exists")

    user = User(
        username=body.username,
        email=body.email,
        full_name=body.full_name,
        hashed_password=hash_password(body.temp_password),
        role=body.role,
        force_password_change=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"detail": "User created", "user_id": user.id, "username": user.username}


@router.put("/users/{user_id}", response_model=UserOut)
def update_user(
    user_id: int,
    body: UpdateUserRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if body.is_active is not None:
        user.is_active = body.is_active
    if body.role is not None:
        user.role = body.role
    if body.full_name is not None:
        user.full_name = body.full_name

    db.commit()
    db.refresh(user)
    return UserOut.model_validate(user)


@router.post("/users/{user_id}/reset-password")
def reset_password(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    temp_pw = secrets.token_urlsafe(12)
    user.hashed_password = hash_password(temp_pw)
    user.force_password_change = True
    db.commit()
    return {"temp_password": temp_pw, "username": user.username, "detail": "Password reset"}
