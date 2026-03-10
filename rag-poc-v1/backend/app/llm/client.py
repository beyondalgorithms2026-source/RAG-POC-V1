import httpx
from app.core.config import settings
from app.core.logging import logger

_llm_ready = False

def is_llm_ready() -> bool:
    return _llm_ready

def _get_api_key():
    # support either name
    return getattr(settings, "OLLAMA_API_KEY", None) or getattr(settings, "LLM_API_KEY", None)

def _auth_headers() -> dict:
    key = _get_api_key()
    if not key:
        return {"Content-Type": "application/json"}
    return {"Content-Type": "application/json", "Authorization": f"Bearer {key}"}

def verify_llm_ready():
    """Preflight check on startup to ensure the LLM endpoint is reachable and the model exists."""
    global _llm_ready
    try:
        base = settings.LLM_BASE_URL.rstrip("/")

        # Local Ollama (OpenAI-compatible)
        if settings.LLM_PROVIDER == "ollama":
            url = f"{base}/v1/models"
            with httpx.Client(timeout=10.0) as client:
                response = client.get(url)
                if response.status_code != 200:
                    logger.error(f"Failed to fetch models from {base}. HTTP {response.status_code}")
                    _llm_ready = False
                    return False

                data = response.json()
                models = data.get("models", [])
                model_ids = [m.get("id") or m.get("name") for m in models]
                if not any(settings.LLM_MODEL in (m or "") for m in model_ids):
                    logger.error(f"Model '{settings.LLM_MODEL}' not found in Ollama at {base}")
                    _llm_ready = False
                    return False

                logger.info(f"LLM Preflight matched (local): {settings.LLM_MODEL} is ready.")
                _llm_ready = True
                return True

        # Ollama Cloud (ollama.com/api)
        if settings.LLM_PROVIDER == "ollama_cloud":
            url = f"{base}/tags"
            with httpx.Client(timeout=10.0) as client:
                response = client.get(url, headers=_auth_headers())
                if response.status_code != 200:
                    logger.error(f"Failed to fetch cloud tags from {base}. HTTP {response.status_code}")
                    _llm_ready = False
                    return False

                data = response.json()
                models = data.get("models", [])
                model_names = [m.get("name") for m in models if isinstance(m, dict)]
                if model_names and not any(settings.LLM_MODEL in (n or "") for n in model_names):
                    logger.warning(f"Cloud tags reachable but model '{settings.LLM_MODEL}' not listed. Continuing as ready.")

                logger.info(f"LLM Preflight OK (cloud): endpoint reachable.")
                _llm_ready = True
                return True

        # Unknown provider
        logger.error(f"Unknown LLM_PROVIDER='{settings.LLM_PROVIDER}'.")
        _llm_ready = False
        return False
    except Exception as e:
        logger.error(f"LLM Preflight failed: {e}")
        _llm_ready = False
        return False

def generate_answer(system_prompt: str, user_prompt: str) -> dict:
    base = settings.LLM_BASE_URL.rstrip("/")
    headers = _auth_headers()

    # 5 minute backup timeout (300s) as requested
    timeout_s = float(getattr(settings, "LLM_TIMEOUT_S", 300) or 300)
    timeout_s = max(timeout_s, 300.0)

    # Local Ollama (OpenAI-compatible)
    if settings.LLM_PROVIDER == "ollama":
        url = f"{base}/v1/chat/completions"
        payload = {
            "model": settings.LLM_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.0,
            "response_format": {"type": "json_object"}
        }

        try:
            with httpx.Client(timeout=timeout_s) as client:
                logger.info(f"Sending LOCAL LLM request to {url} with model {settings.LLM_MODEL}")
                response = client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                return {"success": True, "content": content}
        except httpx.TimeoutException:
            logger.error(f"LOCAL LLM generation timed out after {timeout_s}s.")
            return {"success": False, "error": f"LLM provider timeout ({timeout_s}s)."}
        except Exception as e:
            logger.error(f"LOCAL LLM generation failed: {e}")
            return {"success": False, "error": str(e)}

    # Ollama Cloud (ollama.com/api)
    if settings.LLM_PROVIDER == "ollama_cloud":
        url = f"{base}/chat"
        payload = {
            "model": settings.LLM_MODEL,
            "stream": False,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "options": {"temperature": 0.0},
        }

        try:
            with httpx.Client(timeout=timeout_s) as client:
                logger.info(f"Sending CLOUD LLM request to {url} with model {settings.LLM_MODEL}")
                response = client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()
                content = (data.get("message") or {}).get("content", "")
                return {"success": True, "content": content}
        except httpx.TimeoutException:
            logger.error(f"CLOUD LLM generation timed out after {timeout_s}s.")
            return {"success": False, "error": f"LLM provider timeout ({timeout_s}s)."}
        except Exception as e:
            logger.error(f"CLOUD LLM generation failed: {e}")
            return {"success": False, "error": str(e)}

    return {"success": False, "error": f"Unknown LLM_PROVIDER='{settings.LLM_PROVIDER}'"}