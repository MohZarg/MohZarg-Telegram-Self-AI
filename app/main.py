"""Initial executable web/API foundation for Telegram Self AI."""
from base64 import b64decode
from binascii import Error as Base64Error
from hmac import compare_digest
from html import escape
import os
import threading
import time
from urllib.parse import urlparse

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import Settings

app = FastAPI(
    title="GhYiAb Self · by MohZarg",
    description="GhYiAb Self is a free, open-source Telegram account automation foundation by MohZarg.",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url=None,
)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "no-referrer")
        response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        response.headers.setdefault(
            "Content-Security-Policy",
            "default-src 'self'; style-src 'self' 'unsafe-inline'; "
            "script-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'",
        )
        return response


# Conservative per-process throttle. For multi-worker deployments, enforce a shared
# limiter at a trusted reverse proxy or shared store; this in-memory guard is not global.
_AUTH_FAILURE_WINDOW_SECONDS = 60.0
_AUTH_FAILURE_LIMIT = 5
_AUTH_BLOCK_SECONDS = 60.0
_auth_failures: dict[str, tuple[float, int, float]] = {}
_auth_failures_lock = threading.Lock()


def _auth_is_blocked(client_key: str, now: float) -> bool:
    with _auth_failures_lock:
        # Bound memory growth by removing expired entries on every lookup.
        expired = [key for key, (_, _, blocked_until) in _auth_failures.items()
                   if blocked_until <= now]
        for key in expired:
            _auth_failures.pop(key, None)
        state = _auth_failures.get(client_key)
        return bool(state and state[2] > now)


def _record_auth_failure(client_key: str, now: float) -> float:
    with _auth_failures_lock:
        # Remove expired entries and cap state so arbitrary client addresses cannot
        # grow the dictionary without bound.
        for key, (_, _, blocked_until) in list(_auth_failures.items()):
            if blocked_until <= now:
                _auth_failures.pop(key, None)
        state = _auth_failures.get(client_key)
        if state is None or now - state[0] >= _AUTH_FAILURE_WINDOW_SECONDS:
            count = 1
            window_start = now
            blocked_until = 0.0
        else:
            window_start, count, blocked_until = state
            count += 1
        if count >= _AUTH_FAILURE_LIMIT:
            blocked_until = now + _AUTH_BLOCK_SECONDS
        if len(_auth_failures) >= 10000 and client_key not in _auth_failures:
            # Fail closed for this request when the limiter is saturated.
            return now + _AUTH_BLOCK_SECONDS
        _auth_failures[client_key] = (window_start, count, blocked_until)
        return blocked_until


class AdminAuthMiddleware(BaseHTTPMiddleware):
    """Single-admin HTTP Basic gate for every route except the minimal liveness probe."""

    async def dispatch(self, request, call_next):
        if request.url.path == "/api/health":
            return await call_next(request)

        settings = Settings.from_env()
        if settings.app_env.lower() != "production":
            return await call_next(request)

        expected_user = os.getenv("ADMIN_USERNAME", "")
        expected_password = os.getenv("ADMIN_PASSWORD", "")
        if not expected_user or not expected_password:
            from fastapi.responses import JSONResponse
            return JSONResponse(
                {"detail": "Administrative authentication is not configured"},
                status_code=503,
            )

        client_key = request.client.host if request.client else "unknown"
        now = time.monotonic()
        if _auth_is_blocked(client_key, now):
            from fastapi.responses import JSONResponse
            state = _auth_failures.get(client_key)
            retry_after = max(1, int(state[2] - now)) if state else int(_AUTH_BLOCK_SECONDS)
            return JSONResponse(
                {"detail": "Too many failed authentication attempts"},
                status_code=429,
                headers={"Retry-After": str(retry_after)},
            )

        authorization = request.headers.get("authorization", "")
        username = password = ""
        try:
            scheme, encoded = authorization.split(" ", 1)
            if scheme.lower() == "basic":
                decoded = b64decode(encoded, validate=True).decode("utf-8")
                username, password = decoded.split(":", 1)
        except (ValueError, UnicodeDecodeError, Base64Error):
            pass

        user_ok = compare_digest(username.encode(), expected_user.encode())
        password_ok = compare_digest(password.encode(), expected_password.encode())
        if not (user_ok and password_ok):
            blocked_until = _record_auth_failure(client_key, now)
            if blocked_until > now:
                from fastapi.responses import JSONResponse
                return JSONResponse(
                    {"detail": "Too many failed authentication attempts"},
                    status_code=429,
                    headers={"Retry-After": str(max(1, int(blocked_until - now)))},
                )
            from fastapi.responses import JSONResponse
            return JSONResponse(
                {"detail": "Authentication required"},
                status_code=401,
                headers={"WWW-Authenticate": 'Basic realm="GhYiAb Self Admin"'},
            )
        with _auth_failures_lock:
            _auth_failures.pop(client_key, None)
        return await call_next(request)


# Add auth first so security headers also cover auth error responses.
app.add_middleware(AdminAuthMiddleware)
app.add_middleware(SecurityHeadersMiddleware)


def donation_url_is_safe(value: str) -> bool:
    if not value:
        return False
    parsed = urlparse(value)
    return parsed.scheme == "https" and bool(parsed.netloc)


@app.get("/api/health", tags=["system"])
def health():
    """Liveness check; deliberately does not expose configuration or secrets."""
    return {"status": "ok", "service": "ghyiab-self", "version": app.version}


@app.get("/api/status", tags=["system"])
def status():
    """Expose non-sensitive runtime status without overstating integrations."""
    settings = Settings.from_env()
    return {
        "status": "operational",
        "environment": settings.app_env,
        "features": {
            "web_dashboard": True,
            "health_api": True,
            "automation_rule_engine": True,
            "scheduler_sqlite_store": True,
            "encrypted_session_vault": True,
            "audit_log": True,
            "ai_provider_interface": True,
            "ollama_adapter": True,
            "telegram_bot": False,
            "mtproto_account": False,
            "ai_assistant_workflow": False,
            "content_engine": False,
            "automation_worker": True,
            "scheduler_worker": True,
            "monitoring": True,
            "localization": ["en"],
        },
        "donate_configured": donation_url_is_safe(settings.donation_url),
    }


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def dashboard():
    """Serve a minimal responsive status dashboard with no external assets."""
    settings = Settings.from_env()
    donate = ""
    if donation_url_is_safe(settings.donation_url):
        safe_url = escape(settings.donation_url, quote=True)
        donate = (
            f'<a class="donate" href="{safe_url}" target="_blank" '
            'rel="noopener noreferrer">Support Development</a>'
        )
    html = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="dark">
<title>GhYiAb Self · by MohZarg</title>
<style>
:root{color-scheme:dark;--bg:#080910;--panel:#121421;--line:#292c40;--text:#f4f5fb;--muted:#a4a8bf;--accent:#9d4dff}
*{box-sizing:border-box}body{margin:0;background:radial-gradient(ellipse at top,#19112b 0,var(--bg) 55%);color:var(--text);font:16px/1.6 system-ui,-apple-system,Segoe UI,sans-serif}
main{max-width:980px;margin:auto;padding:56px 22px}.eyebrow{color:#c7a1ff;letter-spacing:.14em;text-transform:uppercase;font-size:.78rem}
h1{font-size:clamp(2rem,6vw,4rem);line-height:1.05;letter-spacing:-.04em;margin:.5rem 0 1rem}p{color:var(--muted)}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px;margin:30px 0}
.card{background:rgba(18,20,33,.9);border:1px solid var(--line);border-radius:16px;padding:20px}.card h2{font-size:1rem;margin:0 0 8px}.creator{border-color:#4b326b;background:linear-gradient(120deg,rgba(38,22,58,.82),rgba(18,20,33,.94));margin-top:18px}.creator .eyebrow{margin-bottom:8px}.creator-link{display:inline-block;margin-top:4px;padding:9px 13px;border:1px solid #6942a0;border-radius:10px;text-decoration:none}.pill{display:inline-block;border:1px solid #3d3156;color:#d6b9ff;border-radius:999px;padding:4px 10px;font-size:.8rem}
a{color:#d9c0ff}.donate{display:inline-block;margin-top:14px;padding:11px 16px;border-radius:12px;border:1px solid #6942a0;text-decoration:none}
footer{border-top:1px solid var(--line);margin-top:40px;padding-top:20px;color:var(--muted);font-size:.9rem}
</style></head>
<body><main>
<div class="eyebrow">GhYiAb Self · Open Source</div>
<h1>GhYiAb Self</h1>
<p>A free, open-source foundation for authorized Telegram account automation, built by MohZarg.</p>
<span class="pill">Free &amp; Open Source</span> <span class="pill">Early Development</span>
<section class="grid" aria-label="Project status">
<article class="card"><h2>Core primitives</h2><span class="pill">Available</span><p>Rule evaluation, SQLite job storage, encrypted session-byte vault, redacted audit log, and an AI provider adapter.</p></article>
<article class="card"><h2>Telegram integrations</h2><span class="pill">Planned</span><p>Telegram Bot API, MTProto login, 2FA, session lifecycle, and rate-aware execution are not connected yet.</p></article>
<article class="card"><h2>Workers and dashboard</h2><span class="pill">In progress</span><p>Durable job storage exists; background workers, authentication, RBAC, and full Persian/English UI remain pending.</p></article>
</section>
<section class="card creator" aria-label="Creator promotion">
<div class="eyebrow">Creator · MohZarg</div>
<h2>Built by MohZarg. Open to everyone.</h2>
<p>MohZarg develops AI-first tools and open-source software. This project stays free; this creator promotion does not unlock features or affect functionality.</p>
<a class="creator-link" href="https://MohZarg.ir" target="_blank" rel="noopener noreferrer">Explore MohZarg</a>
</section>
<p>Current service status: <strong id="health">Checking…</strong></p>
__DONATE__
<footer>GhYiAb Self is free under the MIT License. MohZarg is the creator; the promotional link is disclosed, optional, and never unlocks features. Donations are optional. Use only accounts and data you are authorized to operate. · <a href="/api/docs">API docs</a> · <a href="https://github.com/MohZarg/MohZarg-Telegram-Self-AI">GitHub</a></footer>
</main>
<script>
fetch('/api/health').then(r=>r.ok?r.json():Promise.reject()).then(d=>document.getElementById('health').textContent=d.status==='ok'?'Online':'Unavailable').catch(()=>document.getElementById('health').textContent='Unavailable');
</script></body></html>"""
    return HTMLResponse(html.replace("__DONATE__", donate))


@app.get("/api", include_in_schema=False)
def api_root():
    return {"service": "telegram-self-ai", "docs": "/api/docs", "health": "/api/health"}
