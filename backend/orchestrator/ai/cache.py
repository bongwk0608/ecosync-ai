from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone

from django.conf import settings

from ..services.storage import repository
from .gemini import explain_match


PROMPT_VERSION = "ecosync-match-rationale-v1"


def get_or_create_explanation(startup, mentor, deterministic_result, force_refresh=False):
    cache_id = cache_key(startup["id"], mentor["id"])
    fingerprint = input_fingerprint(startup, mentor, deterministic_result)

    if not settings.REMEMBER_LLM_RESPONSES:
        return {
            "ai": explain_match(startup, mentor, deterministic_result),
            "ai_cache_status": "disabled",
            "ai_cache_key": cache_id,
        }

    cached = repository.get_llm_explanation(cache_id)
    if (
        cached
        and not force_refresh
        and cached.get("model") == settings.GEMINI_MODEL
        and cached.get("prompt_version") == PROMPT_VERSION
        and cached.get("input_fingerprint") == fingerprint
    ):
        repository.create_or_update_llm_explanation(
            cache_id,
            {
                **cached,
                "last_used_at": _now(),
                "usage_count": int(cached.get("usage_count") or 0) + 1,
            },
        )
        return {
            "ai": cached["ai"],
            "ai_cache_status": "hit",
            "ai_cache_key": cache_id,
        }

    ai = explain_match(startup, mentor, deterministic_result)
    now = _now()
    repository.create_or_update_llm_explanation(
        cache_id,
        {
            "id": cache_id,
            "startup_id": startup["id"],
            "mentor_id": mentor["id"],
            "model": settings.GEMINI_MODEL,
            "prompt_version": PROMPT_VERSION,
            "input_fingerprint": fingerprint,
            "ai": ai,
            "created_at": cached.get("created_at") if cached else now,
            "updated_at": now,
            "last_used_at": now,
            "usage_count": 1,
        },
    )
    return {
        "ai": ai,
        "ai_cache_status": "refresh" if force_refresh else "miss",
        "ai_cache_key": cache_id,
    }


def cache_key(startup_id, mentor_id):
    return f"llm-{startup_id}-{mentor_id}"


def input_fingerprint(startup, mentor, deterministic_result):
    payload = {
        "startup": startup,
        "mentor": mentor,
        "deterministic_result": deterministic_result,
        "model": settings.GEMINI_MODEL,
        "prompt_version": PROMPT_VERSION,
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _now():
    return datetime.now(timezone.utc).isoformat()
