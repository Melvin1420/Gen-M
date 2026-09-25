from __future__ import annotations

import os

os.environ.setdefault("MYSQL_DATABASE", "gen_m_test")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import Session

import gen_m.models  # noqa: F401 - registers every model on Base.metadata
from gen_m.core.security import get_password_hash
from gen_m.database.base import Base
from gen_m.database.session import SessionLocal, engine, get_db
from gen_m.main import app
from gen_m.models.department import Department
from gen_m.models.user import User, UserRole


@pytest.fixture(scope="session", autouse=True)
def _test_schema():
    """Create every table once per test run, against gen_m_test only - never
    the real gen_m database. See the MYSQL_DATABASE override above."""
    assert engine.url.database == "gen_m_test", (
        f"Refusing to run tests against {engine.url.database!r}; "
        "expected the gen_m_test database."
    )
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db_session() -> Session:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(autouse=True)
def _clean_tables(db_session: Session):
    """Wipe every table after each test so tests never see leftover data
    from a previous one, regardless of test order."""
    yield
    db_session.execute(text("SET FOREIGN_KEY_CHECKS=0"))
    for table in reversed(Base.metadata.sorted_tables):
        db_session.execute(table.delete())
    db_session.execute(text("SET FOREIGN_KEY_CHECKS=1"))
    db_session.commit()


@pytest.fixture()
def client(db_session: Session):
    def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def department(db_session: Session) -> Department:
    dept = Department(name="Test Department")
    db_session.add(dept)
    db_session.commit()
    db_session.refresh(dept)
    return dept


@pytest.fixture()
def make_user(db_session: Session):
    """Factory fixture: make_user(email, role=..., department_id=...) -> (User, password)"""

    def _make_user(
        email: str,
        role: UserRole = UserRole.EMPLOYEE,
        department_id: int | None = None,
        password: str = "TestPass123!",
    ) -> tuple[User, str]:
        user = User(
            email=email,
            full_name=email.split("@")[0],
            hashed_password=get_password_hash(password),
            role=role,
            department_id=department_id,
            is_active=True,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user, password

    return _make_user
