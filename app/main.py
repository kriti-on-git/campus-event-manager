from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles  # 1. FIXED: Imported for static hosting
from sqlalchemy.orm import Session
from datetime import datetime

# 2. FIXED: Swapped relative imports to absolute to avoid 'ImportError' when running server
from app.models import Event, User, Task, Registration
from app.database import Base, engine, get_db
from app.auth import (
    hash_password,
    verify_password,
    create_access_token,
    verify_token,
)
from app.routers.events import router as event_router
from app.routers.registrations import router as registration_router
from app.routers.tasks import router as task_router
from app.routers.announcements import router as announcement_router

# One-time table setup.
Base.metadata.create_all(bind=engine)

app = FastAPI()

# 3. FIXED: Mounted the static directory to serve your style.css and main.js files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")

# Include Routers
app.include_router(event_router)
app.include_router(registration_router)
app.include_router(task_router)
app.include_router(announcement_router)

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
    if db.query(User).filter(User.email == email).first():
        # 4. UX IMPROVEMENT: Avoid a generic raw JSON error string if possible
        return RedirectResponse(
            url="/login",
            status_code=303
        )

    user = User(
        name=name,
        email=email,
        password=hash_password(password),
        role=role,
    )

    db.add(user)
    db.commit()

    return RedirectResponse("/login", status_code=303)


# =========================
# LOGIN
# =========================
@app.get("/login", response_class=HTMLResponse)
def login_page(
    request: Request,
    error: str = None
):
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={
            "error": error
        }
    )

@app.post("/login")
def login(
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):

    user = db.query(User).filter(User.email == email).first()

    if not user or not verify_password(password, user.password): 
        return RedirectResponse(
            url="/login?error=invalid_credentials",
            status_code=303
        )

    token = create_access_token(
        {
            "user_id": user.id,
            "role": user.role,
        }
    )


    response = RedirectResponse("/dashboard", status_code=303)
    

    # 5. SECURITY FIX: Added 'samesite' protection against CSRF token hijacking
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax"
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
    if not token:
        return RedirectResponse("/login", status_code=303)

    payload = verify_token(token)
    if not payload:
        return RedirectResponse("/login", status_code=303)

    user = db.query(User).filter(User.id == payload["user_id"]).first()
    if not user:
        return RedirectResponse("/login", status_code=303)

    # Set normalized comparison role context variable flag
    user_role = str(user.role).strip().lower()
     # DYNAMIC LAYOUT CONTEXT METRICS FOR THE UI VIEW
    stats = {}
    if user_role == "admin":
        stats["total_events"] = db.query(Event).count()
        stats["total_tasks"] = db.query(Task).count()
        stats["total_registrations"] = db.query(Registration).count()
        stats["pending_approvals"] = db.query(Task).filter(Task.status == "Pending").count()
        
    elif user_role == "volunteer":
        # Extract operational tasks assigned specifically to this logged-in account ID
        stats["my_total_tasks"] = db.query(Task).filter(Task.volunteer_id == user.id).count()
        stats["my_pending_tasks"] = db.query(Task).filter(Task.volunteer_id == user.id, Task.status == "Pending").count()
        stats["my_confirmed_tasks"] = db.query(Task).filter(Task.volunteer_id == user.id, Task.status == "Confirmed").count()
        stats["total_registrations_viewable"] = db.query(Registration).count()
        
    elif user_role == "participant":
        stats["my_registrations_count"] = db.query(Registration).filter(Registration.user_id == user.id).count()

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "user": user,
            "role": user_role,
            "stats": stats
        },
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

    response.delete_cookie("access_token")

    return response