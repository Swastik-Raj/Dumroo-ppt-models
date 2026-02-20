from __future__ import annotations

import os

from dotenv import load_dotenv


def _print_result(name: str, ok: bool, detail: str) -> None:
    status = "OK" if ok else "FAILED"
    print(f"{name}: {status} - {detail}")


def _has_whitespace(value: str) -> bool:
    return any(ch.isspace() for ch in value)


def _check_gemini() -> int:
    try:
        from google import genai
    except Exception as e:
        _print_result("Gemini", False,
                      f"google-genai not installed ({type(e).__name__})")
        return 1

    def _pick_supported_model(client: genai.Client, preferred: str | None) -> str | None:
        # 1) Try preferred (if provided)
        if preferred:
            return preferred

    # 2) Try to pick from ListModels
    try:
        models = list(client.models.list())
    except Exception:
        return None

    def supports_generate(m) -> bool:
        actions = getattr(m, "supported_actions", None) or []
        return any(a.lower() == "generatecontent" for a in actions)

    candidates = [m for m in models if supports_generate(m)]

    # Prefer "flash" text models for speed/cost; then any gemini.
    def score(m) -> tuple[int, int, str]:
        name = (getattr(m, "name", "") or "").lower()
        return (
            0 if "flash" in name else 1,
            0 if "gemini" in name else 1,
            name,
        )

    candidates.sort(key=score)
    if not candidates:
        return None

        return candidates[0].name

    key = os.getenv("GEMINI_API_KEY")
    if not key:
        _print_result("Gemini", False, "GEMINI_API_KEY not set")
        return 1

    if _has_whitespace(key):
        _print_result("Gemini", False,
                      "GEMINI_API_KEY contains whitespace (copy/paste issue)")
        return 1

    model = os.getenv("GEMINI_MODEL")
    if not model:
        try:
            from app.config import settings

            model = settings.gemini_model
        except Exception:
            model = "gemini-1.5-flash-latest"

    client = genai.Client(api_key=key)

    try:
        chosen = model
        try:
            client.models.generate_content(
                model=chosen,
                contents="ping",
                config={"temperature": 0, "max_output_tokens": 1},
            )
        except Exception as first_err:
            fallback = _pick_supported_model(client, preferred=None)
            if not fallback:
                raise first_err
            client.models.generate_content(
                model=fallback,
                contents="ping",
                config={"temperature": 0, "max_output_tokens": 1},
            )
            chosen = fallback

        _print_result("Gemini", True, f"authenticated (model={chosen})")
        return 0
    except Exception as e:
        _print_result("Gemini", False, f"{type(e).__name__}: {e}")
        return 1


def _check_openai() -> int:
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        _print_result("OpenAI", False, "OPENAI_API_KEY not set")
        return 1

    if _has_whitespace(key):
        _print_result("OpenAI", False,
                      "OPENAI_API_KEY contains whitespace (copy/paste issue)")
        return 1

    try:
        from openai import OpenAI
    except Exception as e:
        _print_result("OpenAI", False,
                      f"openai package not installed ({type(e).__name__})")
        return 1

    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    try:
        client = OpenAI(api_key=key)
        # Lightweight authenticated call; should fail fast if the key is invalid.
        client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "ping"}],
            max_tokens=1,
            temperature=0,
        )
        _print_result("OpenAI", True, f"authenticated (model={model})")
        return 0
    except Exception as e:
        _print_result("OpenAI", False, f"{type(e).__name__}: {e}")
        return 1


def main() -> None:
    load_dotenv()

    gemini_rc = _check_gemini()
    openai_rc = _check_openai()

    if gemini_rc != 0 and openai_rc != 0:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
