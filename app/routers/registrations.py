from fastapi import APIRouter
from fastapi import Depends
from fastapi import Request

from fastapi.responses import RedirectResponse

from sqlalchemy.orm import Session

from app.database import get_db

from app.models import Event
from app.models import Registration

from app.dependencies import require_login

router = APIRouter()

from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(
    directory="app/templates"
)

@router.post("/register-event/{event_id}")
def register_event(
    event_id: int,
    request: Request,
    db: Session = Depends(get_db)
):

    user = require_login(
        request=request,
        db=db
    )

    existing = (
        db.query(Registration)
        .filter(
            Registration.user_id == user.id,
            Registration.event_id == event_id
        )
        .first()
    )

    if not existing:

        registration = Registration(
            user_id=user.id,
            event_id=event_id
        )

        db.add(registration)

        db.commit()

    return RedirectResponse(
        url="/my-events",
        status_code=303
    )

@router.get("/my-events")
def my_events(
    request: Request,
    db: Session = Depends(get_db)
):

    user = require_login(
        request=request,
        db=db
    )

    registrations = (
        db.query(Registration)
        .filter(
            Registration.user_id == user.id
        )
        .all()
    )

    events = []

    for registration in registrations:

        event = (
            db.query(Event)
            .filter(
                Event.id == registration.event_id
            )
            .first()
        )

        if event:
            events.append(event)

    return templates.TemplateResponse(
        request=request,
        name="my_events.html",
        context={
            "events": events,
            "user": user
        }
    )

from app.models import User 

@router.get("/registrations")
def view_all_registrations(
    request: Request,
    db: Session = Depends(get_db)
):
    #  Enforce user authentication state
    user = require_login(request=request, db=db)

    #  Hard access barrier: block participants from viewing this database matrix
    if user.role not in ["admin", "volunteer"]:
        return RedirectResponse(url="/dashboard", status_code=303)

    #  Optimized relational database cross-join query fetching User information alongside Event records
    records = (
        db.query(Registration, User, Event)
        .join(User, Registration.user_id == User.id)
        .join(Event, Registration.event_id == Event.id)
        .order_by(Registration.id.desc()) # Puts the latest actions at the top of your list grid
        .all()
    )

    
    parsed_registrations = []
    for reg, participant, event in records:
        parsed_registrations.append({
            "id": reg.id,
            "participant_name": participant.name,
            "participant_email": participant.email,
            "event_title": event.title,
            "event_category": event.category or "General"
        })

    return templates.TemplateResponse(
        request=request,
        name="registrations.html",
        context={
            "registrations": parsed_registrations,
            "user": user
        }
    )
