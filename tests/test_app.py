import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import app

client = TestClient(app)


def test_health_endpoint_does_not_expose_secrets():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert "api_hash" not in response.text.lower()
    assert "token" not in response.text.lower()


def test_health_response_has_security_headers():
    response = client.get("/api/health")
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert "default-src 'self'" in response.headers["content-security-policy"]


def test_status_marks_unimplemented_features(monkeypatch):
    monkeypatch.delenv("DONATION_URL", raising=False)
    response = client.get("/api/status")
    assert response.status_code == 200
    data = response.json()
    assert data["features"]["web_dashboard"] is True
    assert data["features"]["telegram_bot"] is False
    assert data["features"]["mtproto_account"] is False
    assert data["donate_configured"] is False


def test_dashboard_renders_and_checks_health():
    response = client.get("/")
    assert response.status_code == 200
    assert "GhYiAb Self" in response.text
    assert "Free &amp; Open Source" in response.text
    assert "Creator · MohZarg" in response.text
    assert "https://MohZarg.ir" in response.text
    assert "does not unlock features" in response.text
    assert "/api/health" in response.text


def test_creator_promotion_is_disclosed_and_does_not_gate_features():
    response = client.get("/")
    assert response.status_code == 200
    assert "Creator · MohZarg" in response.text
    assert "optional" in response.text
    assert "does not unlock features" in response.text


def test_donation_only_accepts_https(monkeypatch):
    monkeypatch.setenv("DONATION_URL", "http://example.com/donate")
    response = client.get("/")
    assert "Support Development" not in response.text


def test_settings_reject_invalid_port(monkeypatch):
    monkeypatch.setenv("APP_PORT", "not-a-port")
    with pytest.raises(ValueError, match="APP_PORT must be an integer"):
        Settings.from_env()


def test_settings_reject_out_of_range_port(monkeypatch):
    monkeypatch.setenv("APP_PORT", "70000")
    with pytest.raises(ValueError, match="between 1 and 65535"):
        Settings.from_env()
