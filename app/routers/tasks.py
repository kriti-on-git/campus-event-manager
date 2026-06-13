from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates

from app.database import get_db
from app.models import Task, User, Event
from app.dependencies import require_login, require_admin

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# ==========================================================================
# 1. LIST TASKS (ACCESS CONTROLLED & RELATIONALLY EXTENDED)
# ==========================================================================
@router.get("/tasks")
def list_tasks(
    request: Request,
    db: Session = Depends(get_db)
):
    # Enforce active login state across all roles
    user = require_login(request, db)

    # Base query joining Task, linked Event, and assigned Volunteer tables together
    query = (
        db.query(Task, Event, User)
        .join(Event, Task.event_id == Event.id)
        .join(User, Task.volunteer_id == User.id)
    )

    # Hard Access Isolation Layer: Filter based on user profile permission hierarchy
    if user.role == "volunteer":
        # Volunteers can only pull rows containing their matching unique account ID
        records = query.filter(Task.volunteer_id == user.id).all()
    elif user.role == "admin":
        # System administrators can review the entire global campus pipeline matrix
        records = query.all()
    else:
        # Standard participants are forcefully kicked back out to the main landing view
        return RedirectResponse("/dashboard", status_code=303)

    # Flatten out data parameters cleanly for accurate Jinja template iterations
    parsed_tasks = []
    for task, event, volunteer in records:
        parsed_tasks.append({
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "status": task.status or "Pending",
            "event_title": event.title,
            "volunteer_name": volunteer.name,
            "volunteer_id": volunteer.id
        })

    return templates.TemplateResponse(
        request=request,
        name="tasks.html",
        context={
            "tasks": parsed_tasks,
            "user": user
        }
    )


# ==========================================================================
# 2. CREATE TASK PAGE (ADMIN RESTRICTED GATEWAY LAYER)
# ==========================================================================
@router.get("/tasks/create")
def create_task_page(
    request: Request, 
    db: Session = Depends(get_db)
):
    admin = require_admin(request, db)

    volunteers = db.query(User).filter(User.role == "volunteer").all()
    events = db.query(Event).all()

    return templates.TemplateResponse(
        request=request,
        name="create_task.html",
        context={
            "volunteers": volunteers,
            "events": events,
            "user": admin
        }
    )


# ==========================================================================
# 3. CONSTRUCT EVENT OPERATIONS POST PIPELINE (ADMIN RESTRICTED ENGINE)
# ==========================================================================
@router.post("/tasks/create")
def create_task(
    request: Request,
    title: str = Form(...),
    description: str = Form(...),
    event_id: int = Form(...),
    volunteer_id: int = Form(...),
    db: Session = Depends(get_db)
):
    admin = require_admin(request, db)

    task = Task(
        title=title,
        description=description,
        event_id=event_id,
        volunteer_id=volunteer_id,
        status="Pending" # Set standardized baseline default value configuration
    )

    db.add(task)
    db.commit()

    return RedirectResponse("/tasks", status_code=303)


# ==========================================================================
# 4. STATUS UPDATES & OPERATIONS CONFIRMATIONS (VOLUNTEER EXCLUSIVE)
# ==========================================================================
@router.get("/tasks/update/{task_id}/{status}")
def update_task_status(
    task_id: int,
    status: str,
    request: Request,
    db: Session = Depends(get_db)
):
    user = require_login(request, db)

    # 1. Validate status inputs against the new pipeline workflow rules
    valid_statuses = ["Pending", "Confirmed", "Rejected", "Completed"]
    if status not in valid_statuses:
        return RedirectResponse("/tasks", status_code=303)

    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        return RedirectResponse("/tasks", status_code=303)

    # 2. ROLE CHECK A: Volunteer Permissions (Can only confirm or reject assignments given to them)
    if user.role == "volunteer":
        if task.volunteer_id != user.id:
            return RedirectResponse("/tasks", status_code=303)
        if status not in ["Confirmed", "Rejected"]:
            return RedirectResponse("/tasks", status_code=303)

    # 3. ROLE CHECK B: Admin Permissions (Can only mark a task as completed)
    elif user.role == "admin":
        if status != "Completed":
            return RedirectResponse("/tasks", status_code=303)
        # Admins can only complete a task if the volunteer has confirmed it first
        if task.status != "Confirmed":
            return RedirectResponse("/tasks", status_code=303)

    else:
        return RedirectResponse("/dashboard", status_code=303)

    # Apply state transitions and commit securely
    task.status = status
    db.commit()

    return RedirectResponse("/tasks", status_code=303)

