from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates

from app.database import get_db
from app.models import Announcement
from app.dependencies import require_admin, require_login

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/announcements")
def announcements_page(request: Request, db: Session = Depends(get_db)):
    # Authenticate user session explicitly
    user = require_login(request, db)

    # Sort announcements descending so latest notifications load first
    announcements = db.query(Announcement).order_by(Announcement.id.desc()).all()

    return templates.TemplateResponse(
        request=request,
        name="announcements.html",
        context={
            "user": user,
            "announcements": announcements
        }
    )

@router.post("/announcements/create")
def create_announcement(
    request: Request,
    title: str = Form(...),
    content: str = Form(...),
    db: Session = Depends(get_db)
):
    # Hard authorization block protecting creation pipe
    admin = require_admin(request, db)

    ann = Announcement(
        title=title,
        content=content,
        created_by=admin.id
    )

    db.add(ann)
    db.commit()

    return RedirectResponse("/announcements", status_code=303)
