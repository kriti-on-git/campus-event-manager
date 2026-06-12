
from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime
from .models import Event

from .database import Base, engine, get_db
from .models import User
from .auth import (
    hash_password,
    verify_password,
    create_access_token,
    verify_token,
)
from .routers.events import router as event_router
from .routers.registrations import router as registration_router
from .routers.tasks import router as task_router

# One-time table setup. Future migrations can bully this later.
Base.metadata.create_all(bind=engine)

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

app.include_router(
    event_router
)

app.include_router(
    registration_router
)

app.include_router(task_router)

@app.get("/")
def home():
    return RedirectResponse("/login", status_code=302)


# =========================
# REGISTER
# =========================

@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="register.html",
    )


@app.post("/register")
def register(
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    role: str = Form(...),
    db: Session = Depends(get_db),
):
    # Nobody likes duplicate accounts.
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(
            status_code=400,
            detail="Email already registered",
        )

    user = User(
        name=name,
        email=email,
        password=hash_password(password),  # Security first.
        role=role,
    )

    db.add(user)
    db.commit()

    return RedirectResponse("/login", status_code=303)


# =========================
# LOGIN
# =========================

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html",
    )


@app.post("/login")
def login(
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.email == email).first()

    # Either the email is wrong or someone forgot their password again.
    if not user or not verify_password(password, user.password):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
        )

    token = create_access_token(
        {
            "user_id": user.id,
            "role": user.role,
        }
    )

    response = RedirectResponse(
        "/dashboard",
        status_code=303,
    )

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
    )

    return response


# =========================
# DASHBOARD
# =========================

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(
    request: Request,
    db: Session = Depends(get_db),
):
    token = request.cookies.get("access_token")

    # No token, no party.
    if not token:
        return RedirectResponse("/login", status_code=303)

    payload = verify_token(token)

    if not payload:
        return RedirectResponse("/login", status_code=303)

    user = db.query(User).filter(
        User.id == payload["user_id"]
    ).first()

    if not user:
        return RedirectResponse("/login", status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={"user": user},
    )


# =========================
# LOGOUT
# =========================

@app.get("/logout")
def logout():
    response = RedirectResponse(
        "/login",
        status_code=303,
    )

    # See you next login.
    response.delete_cookie("access_token")

    return response