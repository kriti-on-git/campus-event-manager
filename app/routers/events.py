from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Event
from app.dependencies import require_login, require_admin

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# ==========================================================================
# 1. LIVE CATALOG LISTING (ACCESSIBLE TO ALL SIGNED-IN ROLES)
# ==========================================================================
@router.get("/events")
def list_events(
    request: Request,
    db: Session = Depends(get_db),
):
    # Fixed dependency block to enforce proper session validation
    user = require_login(request, db)
    
    # Fetch all events (ordered by date/id descending for modern look)
    events = db.query(Event).order_by(Event.id.desc()).all()

    return templates.TemplateResponse(
        request=request,
        name="events.html",
        context={
            "events": events,
            "user": user,
        },
    )


# ==========================================================================
# 2. CREATE EVENT VIEW INTERFACE (ADMINS ONLY)
# ==========================================================================
@router.get("/events/create")
def create_event_page(
    request: Request,
    db: Session = Depends(get_db),
):
    admin = require_admin(request, db)

    return templates.TemplateResponse(
        request=request,
        name="create_event.html", # FIXED: Mapped file back to non-plural template name
        context={"user": admin}
    )


# ==========================================================================
# 3. CONSTRUCT EVENT RECORD FORM PIPELINE (ADMINS ONLY)
# ==========================================================================
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
    admin = require_admin(request, db)

    event = Event(
        title=title,
        description=description,
        venue=venue,
        date=date,
        time=time,
        capacity=capacity,
        category=category,
        created_by=admin.id,
    )

    db.add(event)
    db.commit()
    db.refresh(event)

    return RedirectResponse("/events", status_code=303)


# ==========================================================================
# 4. DESTRUCTIVE DELETION TERMINATION ENDPOINT (ADMINS ONLY)
# ==========================================================================
@router.get("/events/delete/{event_id}")
def delete_event(
    event_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    admin = require_admin(request, db)

    event = db.query(Event).filter(Event.id == event_id).first()

    if event:
        db.delete(event)
        db.commit()

    return RedirectResponse("/events", status_code=303)
