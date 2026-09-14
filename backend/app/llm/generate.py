import asyncio
import httpx
import logging
from app.config import settings

logger = logging.getLogger("llm")

GROQ_TIMEOUT = 15.0
OLLAMA_TIMEOUT = 30.0


def _call_groq(prompt: str, json_mode: bool = False) -> str:
    headers = {"Authorization": f"Bearer {settings.groq_api_key}"}
    payload = {
        "model": settings.groq_model,
        "messages": [{"role": "user", "content": prompt}],
    }
    if json_mode:
        payload["response_format"] = {"type": "json_object"}

    resp = httpx.post(
        f"{settings.groq_base_url}/chat/completions",
        headers=headers,
        json=payload,
        timeout=GROQ_TIMEOUT,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def _call_ollama(prompt: str, json_mode: bool = False) -> str:
    payload = {
        "model": settings.ollama_model,
        "prompt": prompt,
        "stream": False,
    }
    if json_mode:
        payload["format"] = "json"

    resp = httpx.post(
        f"{settings.ollama_base_url}/api/generate",
        json=payload,
        timeout=OLLAMA_TIMEOUT,
    )
    resp.raise_for_status()
    return resp.json().get("response", "")


def _generate_sync(prompt: str, json_mode: bool = False) -> str:
    if settings.groq_api_key:
        try:
            result = _call_groq(prompt, json_mode=json_mode)
            logger.info("llm_provider=groq status=ok")
            return result
        except (httpx.RequestError, httpx.TimeoutException, httpx.HTTPStatusError,
                KeyError, IndexError) as e:
            logger.warning(f"llm_provider=groq status=failed error={e} — falling back to ollama")

    result = _call_ollama(prompt, json_mode=json_mode)
    logger.info("llm_provider=ollama status=ok (fallback)")
    return result


async def generate(prompt: str, json_mode: bool = False) -> str:
    return await asyncio.to_thread(_generate_sync, prompt, json_mode)
