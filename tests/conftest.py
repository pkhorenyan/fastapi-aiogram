import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session
from sqlmodel.pool import StaticPool

from api.main import app
from api.db import get_session


@pytest.fixture(name="session")
def session_fixture():
    # Создаем in-memory SQLite базу для тестов
    engine = create_engine(
        "sqlite:///file:memdb1?mode=memory&cache=shared",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Создаем таблицы
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    # Переопределяем зависимость get_session
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override

    client = TestClient(app)
    yield client

    # Очищаем переопределения после теста
    app.dependency_overrides.clear()


@pytest.fixture
def sample_student_data():
    return {
        "first_name": "Иван",
        "last_name": "Иванов"
    }


@pytest.fixture
def sample_score_data():
    return {
        "subject": "Математика",
        "score": 85
    }


@pytest.fixture
def created_student(client, sample_student_data):
    """Создает студента и возвращает его данные"""
    response = client.post("/students/", json=sample_student_data)
    return response.json()