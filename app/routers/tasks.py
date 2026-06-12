from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates

from app.database import get_db
from app.models import Task, User, Event
from app.dependencies import require_login, require_admin

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")

@router.get("/tasks")
def list_tasks(
    request: Request,
    db: Session = Depends(get_db)
):
    user = require_login(request, db)

    if user.role == "volunteer":
        tasks = db.query(Task).filter(Task.volunteer_id == user.id).all()
    else:
        tasks = db.query(Task).all()

    return templates.TemplateResponse(
        request=request,
        name="tasks.html",
        context={
            "tasks": tasks,
            "user": user
        }
    )


@router.get("/tasks/create")
def create_task_page(request: Request, db: Session = Depends(get_db)):
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
        volunteer_id=volunteer_id
    )

    db.add(task)
    db.commit()

    return RedirectResponse("/tasks", status_code=303)

@router.get("/tasks/update/{task_id}/{status}")
def update_task_status(
    task_id: int,
    status: str,
    request: Request,
    db: Session = Depends(get_db)
):
    user = require_login(request, db)

    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        return RedirectResponse("/tasks")

    if user.role != "volunteer" or task.volunteer_id != user.id:
        return RedirectResponse("/tasks")

    task.status = status
    db.commit()

    return RedirectResponse("/tasks")