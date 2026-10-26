"""Initial executable web/API foundation for Telegram Self AI."""
from html import escape
from urllib.parse import urlparse

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import Settings

app = FastAPI(
    title="MohZarg Telegram Self AI",
    description="Free, self-hosted AI assistance and authorized Telegram automation toolkit.",
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


app.add_middleware(SecurityHeadersMiddleware)


def donation_url_is_safe(value: str) -> bool:
    if not value:
        return False
    parsed = urlparse(value)
    return parsed.scheme == "https" and bool(parsed.netloc)


@app.get("/api/health", tags=["system"])
def health():
    """Liveness check; deliberately does not expose configuration or secrets."""
    return {"status": "ok", "service": "telegram-self-ai", "version": app.version}


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
            "automation_worker": False,
            "scheduler_worker": False,
            "monitoring": True,
            "localization": ["en", "fa"],
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
<title>Telegram Self AI · MohZarg</title>
<style>
:root{color-scheme:dark;--bg:#080910;--panel:#121421;--line:#292c40;--text:#f4f5fb;--muted:#a4a8bf;--accent:#9d4dff}
*{box-sizing:border-box}body{margin:0;background:radial-gradient(ellipse at top,#19112b 0,var(--bg) 55%);color:var(--text);font:16px/1.6 system-ui,-apple-system,Segoe UI,sans-serif}
main{max-width:980px;margin:auto;padding:56px 22px}.eyebrow{color:#c7a1ff;letter-spacing:.14em;text-transform:uppercase;font-size:.78rem}
h1{font-size:clamp(2rem,6vw,4rem);line-height:1.05;letter-spacing:-.04em;margin:.5rem 0 1rem}p{color:var(--muted)}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px;margin:30px 0}
.card{background:rgba(18,20,33,.9);border:1px solid var(--line);border-radius:16px;padding:20px}.card h2{font-size:1rem;margin:0 0 8px}.pill{display:inline-block;border:1px solid #3d3156;color:#d6b9ff;border-radius:999px;padding:4px 10px;font-size:.8rem}
a{color:#d9c0ff}.donate{display:inline-block;margin-top:14px;padding:11px 16px;border-radius:12px;border:1px solid #6942a0;text-decoration:none}
footer{border-top:1px solid var(--line);margin-top:40px;padding-top:20px;color:var(--muted);font-size:.9rem}
</style></head>
<body><main>
<div class="eyebrow">MohZarg · Open Source</div>
<h1>Telegram Self AI</h1>
<p>A self-hosted foundation for AI assistance and authorized Telegram workflows.</p>
<span class="pill">Free &amp; Open Source</span> <span class="pill">Early Development</span>
<section class="grid" aria-label="Project status">
<article class="card"><h2>Core primitives</h2><span class="pill">Available</span><p>Rule evaluation, SQLite job storage, encrypted session-byte vault, redacted audit log, and an AI provider adapter.</p></article>
<article class="card"><h2>Telegram integrations</h2><span class="pill">Planned</span><p>Telegram Bot API, MTProto login, 2FA, session lifecycle, and rate-aware execution are not connected yet.</p></article>
<article class="card"><h2>Workers and dashboard</h2><span class="pill">In progress</span><p>Durable job storage exists; background workers, authentication, RBAC, and full Persian/English UI remain pending.</p></article>
</section>
<p>Current service status: <strong id="health">Checking…</strong></p>
__DONATE__
<footer>This project is free to use under the MIT License. Donations are optional and never unlock features. Use only accounts and data you are authorized to operate. · <a href="/api/docs">API docs</a> · <a href="https://github.com/MohZarg/MohZarg-Telegram-Self-AI">GitHub</a></footer>
</main>
<script>
fetch('/api/health').then(r=>r.ok?r.json():Promise.reject()).then(d=>document.getElementById('health').textContent=d.status==='ok'?'Online':'Unavailable').catch(()=>document.getElementById('health').textContent='Unavailable');
</script></body></html>"""
    return HTMLResponse(html.replace("__DONATE__", donate))


@app.get("/api", include_in_schema=False)
def api_root():
    return {"service": "telegram-self-ai", "docs": "/api/docs", "health": "/api/health"}
