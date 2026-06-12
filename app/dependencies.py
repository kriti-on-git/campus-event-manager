from fastapi import Request
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from .database import get_db
from .models import User

from .auth import verify_token


def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
):
    token = request.cookies.get("access_token")

    if not token:
        return None

    payload = verify_token(token)

    if not payload:
        return None

    user = (
        db.query(User)
        .filter(User.id == payload["user_id"])
        .first()
    )

    return user


def require_login(
    request: Request,
    db: Session = Depends(get_db)
):
    user = get_current_user(
        request=request,
        db=db
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Login required"
        )

    return user


def require_admin(
    request: Request,
    db: Session = Depends(get_db)
):
    user = require_login(
        request=request,
        db=db
    )

    if user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )

    return user