from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Event, User
from app.auth import verify_token

router = APIRouter()

templates = Jinja2Templates(
    directory="app/templates"
)


from app.dependencies import get_current_user
from app.dependencies import require_admin

@router.get("/events")
def list_events(
    request: Request,
    db: Session = Depends(get_db),
):
    events = db.query(Event).all()

    user = get_current_user(
        request,
        db,
    )

    return templates.TemplateResponse(
        request=request,
        name="events.html",
        context={
            "events": events,
            "user": user,
        },
    )


@router.get("/events/create")
def create_event_page(
    request: Request,
    db: Session = Depends(get_db),
):
    user = get_current_user(
        request,
        db,
    )

    if not user or user.role != "admin":
        return RedirectResponse(
            "/login",
            status_code=303,
        )

    return templates.TemplateResponse(
        request=request,
        name="create_events.html",
    )


@router.post("/events/create")
def create_event(
    request: Request,
    title: str = Form(...),
    description: str = Form(...),
    venue: str = Form(...),
    date: str = Form(...),
    time: str = Form(...),
    capacity: int = Form(...),
    category: str = Form(...),
    db: Session = Depends(get_db),
):
    user = get_current_user(
        request,
        db,
    )

    if not user or user.role != "admin":
        return RedirectResponse(
            "/login",
            status_code=303,
        )

    event = Event(
        title=title,
        description=description,
        venue=venue,
        date=date,
        time=time,
        capacity=capacity,
        category=category,
        created_by=user.id,
    )

    db.add(event)
    db.commit()
    db.refresh(event)

    return RedirectResponse(
        "/events",
        status_code=303,
    )


@router.get("/events/delete/{event_id}")
def delete_event(
    event_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    user = get_current_user(
        request,
        db,
    )

    if not user or user.role != "admin":
        return RedirectResponse(
            "/login",
            status_code=303,
        )

    event = (
        db.query(Event)
        .filter(
            Event.id == event_id
        )
        .first()
    )

    if event:
        db.delete(event)
        db.commit()

    return RedirectResponse(
        "/events",
        status_code=303,
    )