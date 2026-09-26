"""Thin wrapper over any OpenAI-compatible chat API (Groq by default)."""
import json
import os
import re

from openai import BadRequestError, OpenAI

BASE_URL = os.getenv("LLM_BASE_URL", "https://api.groq.com/openai/v1")
MODEL = os.getenv("LLM_MODEL", "openai/gpt-oss-120b")
# reasoning models (e.g. gpt-oss) think before answering; keep that short so replies aren't empty
REASONING_EFFORT = os.getenv("LLM_REASONING_EFFORT", "low" if "gpt-oss" in MODEL else "")


class LLMUnavailable(RuntimeError):
    pass


class InvalidToolCall(LLMUnavailable):
    """The provider rejected malformed output (a tool call or JSON); safe to retry."""


def available() -> bool:
    return bool(os.getenv("LLM_API_KEY"))


def _client() -> OpenAI:
    if not available():
        raise LLMUnavailable("LLM_API_KEY is not set")
    return OpenAI(base_url=BASE_URL, api_key=os.environ["LLM_API_KEY"], timeout=45, max_retries=4)  # retries honour Groq's rate-limit waits


def _complete(effort=None, **kw):
    effort = effort or REASONING_EFFORT
    extra = {"reasoning_effort": effort} if REASONING_EFFORT and effort else {}
    try:
        return _client().chat.completions.create(model=MODEL, extra_body=extra, **kw).choices[0].message
    except LLMUnavailable:
        raise
    except BadRequestError as e:
        if "tool_use_failed" in str(e) or "json_validate_failed" in str(e):
            raise InvalidToolCall(str(e)) from e
        raise LLMUnavailable(str(e)) from e
    except Exception as e:  # network, auth, rate limit...
        raise LLMUnavailable(str(e)) from e


def chat(messages, temperature=0.4, max_tokens=4000, json_mode=False, effort=None) -> str:
    """`effort` raises reasoning for a reasoning model (ignored for models without it)."""
    kw = {"response_format": {"type": "json_object"}} if json_mode else {}
    msg = _complete(effort, messages=messages, temperature=temperature, max_tokens=max_tokens, **kw)
    return msg.content or ""


def chat_tools(messages, tools, temperature=0.3, max_tokens=1500):
    """One step of native function calling; returns the assistant message."""
    return _complete(None, messages=messages, tools=tools, tool_choice="auto",
                     temperature=temperature, max_tokens=max_tokens)


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
        try:
            reply = chat(messages, json_mode=True, **kw)
            return extract_json(reply)
        except InvalidToolCall as e:  # JSON mode rejected malformed output server-side
            last_err, reply = e, ""
        except ValueError as e:
            last_err = e
            messages += [
                {"role": "assistant", "content": reply},
                {"role": "user", "content": "That was not valid JSON. Reply with only the JSON."},
            ]
    raise LLMUnavailable(f"model did not return JSON: {last_err}")
