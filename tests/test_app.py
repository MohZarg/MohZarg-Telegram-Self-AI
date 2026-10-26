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
    assert data["features"]["scheduler_worker"] is True
    assert data["features"]["automation_worker"] is True
    assert data["features"]["localization"] == ["en"]
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


def test_production_routes_fail_closed_without_admin_credentials(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.delenv("ADMIN_USERNAME", raising=False)
    monkeypatch.delenv("ADMIN_PASSWORD", raising=False)
    assert client.get("/api/health").status_code == 200
    response = client.get("/api/status")
    assert response.status_code == 503
    assert "not configured" in response.json()["detail"]


def test_production_protects_dashboard_status_and_docs(monkeypatch):
    import base64

    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("ADMIN_USERNAME", "owner")
    monkeypatch.setenv("ADMIN_PASSWORD", "test-only-password")
    for path in ("/", "/api/status", "/api/docs", "/openapi.json"):
        response = client.get(path)
        assert response.status_code == 401
        assert response.headers["www-authenticate"].startswith("Basic")

    credential = base64.b64encode(b"owner:test-only-password").decode("ascii")
    headers = {"Authorization": f"Basic {credential}"}
    assert client.get("/", headers=headers).status_code == 200
    assert client.get("/api/status", headers=headers).status_code == 200
    assert client.get("/api/docs", headers=headers).status_code == 200


def test_production_rejects_wrong_admin_credentials(monkeypatch):
    import base64

    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("ADMIN_USERNAME", "owner")
    monkeypatch.setenv("ADMIN_PASSWORD", "correct-password")
    credential = base64.b64encode(b"owner:wrong-password").decode("ascii")
    response = client.get("/api/status", headers={"Authorization": f"Basic {credential}"})
    assert response.status_code == 401


def test_production_throttles_repeated_failed_authentication(monkeypatch):
    import base64
    import app.main as main_module

    main_module._auth_failures.clear()
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("ADMIN_USERNAME", "owner")
    monkeypatch.setenv("ADMIN_PASSWORD", "correct-password")
    wrong = base64.b64encode(b"owner:wrong-password").decode("ascii")
    headers = {"Authorization": f"Basic {wrong}"}

    responses = [client.get("/api/status", headers=headers) for _ in range(5)]
    assert [response.status_code for response in responses[:4]] == [401] * 4
    assert responses[4].status_code == 429
    assert int(responses[4].headers["retry-after"]) > 0
    # Correct credentials from the same client are also blocked during cooldown.
    correct = base64.b64encode(b"owner:correct-password").decode("ascii")
    blocked = client.get("/api/status", headers={"Authorization": f"Basic {correct}"})
    assert blocked.status_code == 429
    assert blocked.headers["retry-after"]
    main_module._auth_failures.clear()
