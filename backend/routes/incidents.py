from fastapi import APIRouter, Depends, Form, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from backend import crud, models, schemas
from backend.database import get_db
from backend.security import hash_password, verify_password

router = APIRouter()
templates = Jinja2Templates(directory="templates")
STATUS_LABELS = {
    models.IncidentStatus.NEW: "НОВЫЙ",
    models.IncidentStatus.IN_PROGRESS: "В РАБОТЕ",
    models.IncidentStatus.RESOLVED: "РЕШЕН",
    models.IncidentStatus.CANCELLED: "ОТМЕНЕН",
}
STATUS_BADGE_CLASSES = {
    models.IncidentStatus.NEW: "text-bg-secondary",
    models.IncidentStatus.IN_PROGRESS: "text-bg-warning",
    models.IncidentStatus.RESOLVED: "text-bg-success",
    models.IncidentStatus.CANCELLED: "text-bg-danger",
}


def get_current_user(request: Request, db: Session):
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    return crud.get_user_by_id(db, user_id)


@router.get("/", response_class=HTMLResponse)
def index(
    request: Request,
    q: str = Query(default=""),
    status: str = Query(default=""),
    db: Session = Depends(get_db),
):
    incidents = crud.get_incidents(db)
    search_query = q.strip()
    selected_status = status.strip()

    if selected_status:
        try:
            status_enum = models.IncidentStatus(selected_status)
            incidents = [incident for incident in incidents if incident.status == status_enum]
        except ValueError:
            selected_status = ""

    if search_query:
        query_lower = search_query.lower()
        incidents = [
            incident
            for incident in incidents
            if query_lower in incident.title.lower() or query_lower in incident.location.lower()
        ]

    total_count = len(incidents)
    active_statuses = (models.IncidentStatus.NEW, models.IncidentStatus.IN_PROGRESS)
    active_count = sum(1 for incident in incidents if incident.status in active_statuses)
    status_counts = {status_option: 0 for status_option in models.IncidentStatus}
    for incident in incidents:
        status_counts[incident.status] += 1
    resolved_count = status_counts[models.IncidentStatus.RESOLVED]
    resolved_percent = int((resolved_count / total_count) * 100) if total_count else 0
    current_user = get_current_user(request, db)

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "incidents": incidents,
            "status_labels": STATUS_LABELS,
            "status_badge_classes": STATUS_BADGE_CLASSES,
            "total_count": total_count,
            "active_count": active_count,
            "search_query": search_query,
            "selected_status": selected_status,
            "status_options": list(models.IncidentStatus),
            "status_counts": status_counts,
            "resolved_percent": resolved_percent,
            "current_user": current_user,
        },
    )


@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request, db: Session = Depends(get_db)):
    current_user = get_current_user(request, db)
    if current_user:
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse(
        "register.html",
        {"request": request, "error": None, "current_user": None},
    )


@router.post("/register")
def register(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    clean_username = username.strip()
    if not clean_username or len(password) < 4:
        return templates.TemplateResponse(
            "register.html",
            {
                "request": request,
                "error": "Введите корректные данные (пароль не короче 4 символов).",
                "current_user": None,
            },
            status_code=400,
        )

    existing_user = crud.get_user_by_username(db, clean_username)
    if existing_user:
        return templates.TemplateResponse(
            "register.html",
            {
                "request": request,
                "error": "Пользователь с таким именем уже существует.",
                "current_user": None,
            },
            status_code=400,
        )

    user = crud.create_user(db, clean_username, hash_password(password))
    request.session["user_id"] = user.id
    return RedirectResponse(url="/", status_code=303)


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request, db: Session = Depends(get_db)):
    current_user = get_current_user(request, db)
    if current_user:
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse(
        "login.html",
        {"request": request, "error": None, "current_user": None},
    )


@router.post("/login")
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = crud.get_user_by_username(db, username.strip())
    if not user or not verify_password(password, user.password_hash):
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error": "Неверный логин или пароль.",
                "current_user": None,
            },
            status_code=401,
        )

    request.session["user_id"] = user.id
    return RedirectResponse(url="/", status_code=303)


@router.post("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=303)


@router.get("/incidents/create", response_class=HTMLResponse)
def create_incident_page(request: Request, db: Session = Depends(get_db)):
    current_user = get_current_user(request, db)
    if not current_user:
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse(
        "create_incident.html",
        {"request": request, "current_user": current_user},
    )


@router.post("/incidents/create")
def create_incident(
    request: Request,
    title: str = Form(...),
    description: str = Form(...),
    location: str = Form(...),
    db: Session = Depends(get_db),
):
    current_user = get_current_user(request, db)
    if not current_user:
        return RedirectResponse(url="/login", status_code=303)

    incident_in = schemas.IncidentCreate(title=title, description=description, location=location)
    incident = crud.create_incident(db, incident_in)
    return RedirectResponse(url=f"/incidents/{incident.id}", status_code=303)


@router.get("/incidents/{incident_id}", response_class=HTMLResponse)
def incident_detail(incident_id: int, request: Request, db: Session = Depends(get_db)):
    incident = crud.get_incident(db, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Инцидент не найден")

    current_user = get_current_user(request, db)
    return templates.TemplateResponse(
        "incident_detail.html",
        {
            "request": request,
            "incident": incident,
            "statuses": list(models.IncidentStatus),
            "status_labels": STATUS_LABELS,
            "status_badge_classes": STATUS_BADGE_CLASSES,
            "current_user": current_user,
        },
    )


@router.post("/incidents/{incident_id}/status")
def update_status(
    request: Request,
    incident_id: int,
    status: str = Form(...),
    db: Session = Depends(get_db),
):
    current_user = get_current_user(request, db)
    if not current_user:
        return RedirectResponse(url="/login", status_code=303)

    incident = crud.get_incident(db, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Инцидент не найден")

    try:
        new_status = models.IncidentStatus(status)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Некорректный статус инцидента") from exc

    crud.update_incident_status(db, incident, new_status)
    return RedirectResponse(url=f"/incidents/{incident_id}", status_code=303)
