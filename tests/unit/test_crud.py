from datetime import datetime, timedelta

from backend import crud, models, schemas


def test_create_incident_sets_default_status_new(db_session):
    incident_in = schemas.IncidentCreate(
        title="Падение сервиса",
        description="Сервис недоступен",
        location="Москва",
    )

    created = crud.create_incident(db_session, incident_in)

    assert created.id is not None
    assert created.status == models.IncidentStatus.NEW
    assert created.title == incident_in.title


def test_get_incident_returns_created_record(db_session):
    created = crud.create_incident(
        db_session,
        schemas.IncidentCreate(
            title="Ошибка авторизации",
            description="Пользователь не может войти",
            location="СПб",
        ),
    )

    found = crud.get_incident(db_session, created.id)

    assert found is not None
    assert found.id == created.id
    assert found.location == "СПб"


def test_get_incidents_returns_desc_order_by_created_at(db_session):
    first = crud.create_incident(
        db_session,
        schemas.IncidentCreate(title="Первый", description="desc1", location="A"),
    )
    second = crud.create_incident(
        db_session,
        schemas.IncidentCreate(title="Второй", description="desc2", location="B"),
    )

    first.created_at = datetime.utcnow() - timedelta(days=1)
    second.created_at = datetime.utcnow()
    db_session.commit()

    incidents = crud.get_incidents(db_session)

    assert [item.id for item in incidents] == [second.id, first.id]


def test_update_incident_status_changes_value(db_session):
    created = crud.create_incident(
        db_session,
        schemas.IncidentCreate(
            title="Инцидент сети",
            description="Проблема с сетью",
            location="Казань",
        ),
    )

    updated = crud.update_incident_status(db_session, created, models.IncidentStatus.RESOLVED)

    assert updated.status == models.IncidentStatus.RESOLVED
