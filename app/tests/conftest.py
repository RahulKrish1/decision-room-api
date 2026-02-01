import os
import pytest
from fastapi.testclient import TestClient

# IMPORTANT: set env vars BEFORE importing app
@pytest.fixture(scope="session", autouse=True)
def _set_test_env():
    os.environ.setdefault("ENV", "test")
    os.environ.setdefault("JWT_SECRET", "test-secret")
    os.environ.setdefault("JWT_EXPIRES_MINUTES", "60")
    # DATABASE_URL will be provided by CI env; for local tests you can export it.

@pytest.fixture()
def client():
    from app.main import app
    return TestClient(app)
