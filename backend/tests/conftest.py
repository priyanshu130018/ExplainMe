import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
import app.models  # noqa: F401
from app.db.session import get_db
from app.main import app

# In-memory SQLite engine for fast, isolated test execution
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for a test."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(autouse=True)
def override_get_db(db_session):
    """Override FastAPI get_db dependency to use the test database session."""
    def _override():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _override
    yield
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def mock_celery_delay():
    """Mock Celery task delay during unit tests so tests do not hang on Redis broker connection."""
    with patch("app.workers.video_tasks.process_video_analysis.delay") as mock_delay:
        mock_task = MagicMock()
        mock_task.id = "mock-celery-task-id-12345"
        mock_delay.return_value = mock_task
        yield mock_delay
