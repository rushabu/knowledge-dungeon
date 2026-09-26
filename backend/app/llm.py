"""Thin wrapper over any OpenAI-compatible chat API (Featherless by default)."""
import json
import os
import re

from openai import OpenAI

BASE_URL = os.getenv("LLM_BASE_URL", "https://api.featherless.ai/v1")
MODEL = os.getenv("LLM_MODEL", "Qwen/Qwen2.5-7B-Instruct")


class LLMUnavailable(RuntimeError):
    pass


def available() -> bool:
    return bool(os.getenv("LLM_API_KEY"))


def _client() -> OpenAI:
    if not available():
        raise LLMUnavailable("LLM_API_KEY is not set")
    return OpenAI(base_url=BASE_URL, api_key=os.environ["LLM_API_KEY"], timeout=90)


def chat(messages, temperature=0.4, max_tokens=2000) -> str:
    try:
        resp = _client().chat.completions.create(
            model=MODEL, messages=messages, temperature=temperature, max_tokens=max_tokens,
        )
    except LLMUnavailable:
        raise
    except Exception as e:  # network, auth, rate limit...
        raise LLMUnavailable(str(e)) from e
    return resp.choices[0].message.content or ""


def extract_json(text: str):
    """Pull the first JSON object/array out of a model reply (handles ```json fences)."""
    fenced = re.search(r"```(?:json)?\s*(.*?)```", text, re.S)
    if fenced:
        text = fenced.group(1)
    start = min((i for i in (text.find("{"), text.find("[")) if i != -1), default=-1)
    if start == -1:
        raise ValueError("no JSON in model reply")
    return json.JSONDecoder().raw_decode(text[start:])[0]


def chat_json(system: str, user: str, retries=2, **kw):
    messages = [{"role": "system", "content": system}, {"role": "user", "content": user}]
    last_err = None
    for _ in range(retries + 1):
        reply = chat(messages, **kw)
        try:
            return extract_json(reply)
        except ValueError as e:
            last_err = e
            messages += [
                {"role": "assistant", "content": reply},
                {"role": "user", "content": "That was not valid JSON. Reply with only the JSON."},
            ]
    raise LLMUnavailable(f"model did not return JSON: {last_err}")
