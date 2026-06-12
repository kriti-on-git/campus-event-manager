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