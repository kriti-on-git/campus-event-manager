from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates

from app.database import get_db
from app.models import Announcement, User
from app.dependencies import require_admin, require_login

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")

@router.get("/announcements")
def announcements_page(request: Request, db: Session = Depends(get_db)):

    user = require_login(request, db)

    announcements = db.query(Announcement).all()

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

    admin = require_admin(request, db)

    ann = Announcement(
        title=title,
        content=content,
        created_by=admin.id
    )

    db.add(ann)
    db.commit()

    return RedirectResponse("/announcements", status_code=303)