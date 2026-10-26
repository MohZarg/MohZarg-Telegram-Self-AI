"""Minimal AI provider abstraction with graceful local-provider failures."""
from dataclasses import dataclass
from typing import Protocol
import json
from urllib.error import URLError, HTTPError
from urllib.request import Request, urlopen

class AIProvider(Protocol):
    name: str
    def generate(self, prompt: str) -> str: ...

@dataclass(frozen=True, slots=True)
class ProviderResult:
    ok: bool
    text: str = ""
    provider: str = "none"
    error: str = ""

class DisabledProvider:
    name = "disabled"
    def generate(self, prompt: str) -> str:
        raise RuntimeError("No AI provider is configured")

class OllamaProvider:
    """Ollama adapter; intended for a trusted local endpoint, not public exposure."""
    name = "ollama"
    def __init__(self, base_url: str = "http://127.0.0.1:11434", model: str = "qwen2.5:3b", timeout: float = 30):
        if not base_url.startswith(("http://", "https://")):
            raise ValueError("base_url must be HTTP(S)")
        if not model or len(model) > 120:
            raise ValueError("Invalid model name")
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = max(1.0, min(float(timeout), 120.0))

    def generate(self, prompt: str) -> str:
        if not prompt.strip() or len(prompt) > 20000:
            raise ValueError("Prompt must contain 1–20000 characters")
        payload = json.dumps({"model": self.model, "prompt": prompt, "stream": False}).encode()
        request = Request(self.base_url + "/api/generate", data=payload,
                          headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urlopen(request, timeout=self.timeout) as response:
                data = json.loads(response.read(2_000_000).decode("utf-8"))
        except (URLError, HTTPError, TimeoutError, OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise RuntimeError(f"AI provider unavailable ({type(exc).__name__})") from exc
        text = data.get("response") if isinstance(data, dict) else None
        if not isinstance(text, str):
            raise RuntimeError("AI provider returned an invalid response")
        return text

def generate_safely(provider: AIProvider, prompt: str) -> ProviderResult:
    try:
        return ProviderResult(ok=True, text=provider.generate(prompt), provider=provider.name)
    except Exception as exc:
        return ProviderResult(ok=False, provider=getattr(provider, "name", "unknown"),
                              error=f"Provider unavailable ({type(exc).__name__})")
