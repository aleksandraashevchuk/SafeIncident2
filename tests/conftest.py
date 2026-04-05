from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from starlette.middleware.sessions import SessionMiddleware

from backend.database import Base
from backend.routes import incidents as incidents_routes


@pytest.fixture()
def session_factory():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    testing_session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    yield testing_session_factory

    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture()
def db_session(session_factory):
    session = session_factory()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(session_factory):
    test_app = FastAPI(title="SafeIncident Test")
    test_app.add_middleware(SessionMiddleware, secret_key="test-secret-key")
    test_app.mount("/static", StaticFiles(directory="static"), name="static")
    test_app.include_router(incidents_routes.router)

    def override_get_db():
        db = session_factory()
        try:
            yield db
        finally:
            db.close()

    test_app.dependency_overrides[incidents_routes.get_db] = override_get_db

    with TestClient(test_app) as test_client:
        yield test_client
