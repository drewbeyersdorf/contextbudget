"""Thin proxy wrapper that intercepts AI client calls and reports token usage.

How it works:
1. track() wraps your client in a proxy
2. The proxy intercepts calls to chat/messages methods
3. After each call, it extracts token counts from the response
4. Token usage is POSTed to the ContextBudget API in the background
5. Your code gets the original response, unchanged

The proxy only touches methods that return token usage.
Everything else passes through untouched.
"""

import uuid
import threading
import requests


# Default API endpoint
DEFAULT_API_URL = "https://contextbudget.dev/api/track"

# Map of client types to their token-returning methods and extraction logic.
# Each entry: (attribute_chain, extractor_function)
# attribute_chain: dot-separated path to the method (e.g. "messages.create")
# extractor: function that pulls token counts from the response
PROVIDERS = {
    "Anthropic": {
        "path": "messages.create",
        "extract": lambda r: {
            "input_tokens": r.usage.input_tokens,
            "output_tokens": r.usage.output_tokens,
            "model": r.model,
        },
    },
    "OpenAI": {
        "path": "chat.completions.create",
        "extract": lambda r: {
            "input_tokens": r.usage.prompt_tokens,
            "output_tokens": r.usage.completion_tokens,
            "model": r.model,
        },
    },
    "GenerativeModel": {
        # Google's genai client -- generate_content returns usage_metadata
        "path": "generate_content",
        "extract": lambda r: {
            "input_tokens": r.usage_metadata.prompt_token_count,
            "output_tokens": r.usage_metadata.candidates_token_count,
            "model": "gemini",
        },
    },
}


def _detect_provider(client):
    """Figure out which AI provider this client belongs to."""
    class_name = type(client).__name__
    for provider_name, config in PROVIDERS.items():
        if provider_name in class_name:
            return provider_name, config
    # Check parent classes too (some clients subclass)
    for cls in type(client).__mro__:
        for provider_name, config in PROVIDERS.items():
            if provider_name in cls.__name__:
                return provider_name, config
    raise ValueError(
        f"Unsupported client: {type(client).__name__}. "
        f"Supported: Anthropic, OpenAI, Google GenerativeModel"
    )


def _resolve_attr(obj, dotted_path):
    """Walk a dot-separated attribute path. 'messages.create' -> obj.messages.create"""
    for part in dotted_path.split("."):
        obj = getattr(obj, part)
    return obj


def _report(api_url, payload):
    """Fire-and-forget POST to the tracking API. Failures are silent --
    tracking should never break your app."""
    try:
        requests.post(api_url, json=payload, timeout=2)
    except Exception:
        pass  # Never let tracking errors affect the user's code


def track(client, *, api_url=DEFAULT_API_URL, session_id=None, api_key=None):
    """Wrap an AI client to automatically track token usage.

    Args:
        client: An Anthropic, OpenAI, or Google GenerativeModel instance.
        api_url: Where to POST usage data. Default: contextbudget.dev/api/track
        session_id: Group calls under one session. Auto-generated if omitted.
        api_key: Optional API key for the ContextBudget dashboard.

    Returns:
        The same client, with token tracking bolted on. Use it exactly
        as you would the original -- the interface doesn't change.
    """
    provider_name, config = _detect_provider(client)
    session_id = session_id or uuid.uuid4().hex[:12]
    printed = [False]  # Mutable container so the closure can flip it

    # Split "messages.create" into ["messages", "create"]
    path_parts = config["path"].split(".")
    method_name = path_parts[-1]           # "create"
    parent_path = path_parts[:-1]          # ["messages"]

    # Get the parent object that owns the method
    parent = client
    for part in parent_path:
        parent = getattr(parent, part)

    # Grab the original method before we patch it
    original_method = getattr(parent, method_name)

    def tracked_method(*args, **kwargs):
        # Call the original -- this is the real API call
        response = original_method(*args, **kwargs)

        # Print the dashboard URL once, on first successful call
        if not printed[0]:
            print(f"View your session: https://contextbudget.dev/d/{session_id}")
            printed[0] = True

        # Extract token usage from the response
        try:
            usage = config["extract"](response)
        except (AttributeError, TypeError):
            return response  # Response didn't have usage info -- skip

        # Build the tracking payload
        payload = {
            "session_id": session_id,
            "provider": provider_name.lower(),
            **usage,
        }
        if api_key:
            payload["api_key"] = api_key

        # Ship it in a background thread -- don't block the user's code
        threading.Thread(target=_report, args=(api_url, payload), daemon=True).start()

        return response

    # Patch the method on the parent object
    setattr(parent, method_name, tracked_method)

    return client
