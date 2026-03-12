"""FastAPI dependencies: DB session, current user extraction."""

from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .auth import decode_session_token
from .config import COOKIE_NAME
from .database import get_db
from .models import User


def get_current_user(
    db: Session = Depends(get_db),
    csr_session: str | None = Cookie(default=None, alias=COOKIE_NAME),
) -> User:
    if not csr_session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    user_id = decode_session_token(csr_session)
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired session")
    user = db.query(User).filter(User.id == user_id, User.is_active.is_(True)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return user
