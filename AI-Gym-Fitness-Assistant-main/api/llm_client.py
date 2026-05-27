"""
api/llm_client.py – Thin wrapper around LLM API calls.

Supports OpenAI-compatible endpoints and Google Gemini.
Returns None gracefully if no API key is configured.
"""
import os
from typing import Optional


def call_llm(prompt: str, system: str = "You are a helpful fitness assistant.") -> Optional[str]:
    """
    Send *prompt* to the configured LLM and return the response text.
    Returns None if no API key is available or if the call fails.
    """
    api_key = os.getenv("LLM_API_KEY", "")
    if not api_key:
        return None

    provider = os.getenv("LLM_PROVIDER", "openai").lower()

    if provider == "gemini":
        return _call_gemini(prompt, api_key)
    return _call_openai(prompt, system, api_key)


def _call_openai(prompt: str, system: str, api_key: str) -> Optional[str]:
    try:
        import httpx
        url = os.getenv("LLM_API_URL", "https://api.openai.com/v1/chat/completions")
        model = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            "max_tokens": 300,
            "temperature": 0.7,
        }
        resp = httpx.post(url, json=payload, headers=headers, timeout=15)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"].strip()
    except Exception:
        return None


def _call_gemini(prompt: str, api_key: str) -> Optional[str]:
    try:
        import httpx
        model = os.getenv("LLM_MODEL", "gemini-pro")
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{model}:generateContent?key={api_key}"
        )
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        resp = httpx.post(url, json=payload, timeout=15)
        resp.raise_for_status()
        return resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception:
        return None
