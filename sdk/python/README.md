# contextbudget

Automatic AI context token tracking. One line to add to your code.

## Install

```bash
pip install contextbudget
```

## Usage

```python
from contextbudget import track
from anthropic import Anthropic

client = track(Anthropic())

# Use the client exactly as before -- tracking is automatic
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello"}]
)
# Prints: View your session: https://contextbudget.dev/d/a1b2c3d4e5f6
```

Works with Anthropic, OpenAI, and Google GenAI:

```python
# OpenAI
from openai import OpenAI
client = track(OpenAI())

# Google
import google.generativeai as genai
model = track(genai.GenerativeModel("gemini-pro"))
```

## Configuration

```python
client = track(
    Anthropic(),
    session_id="my-session",          # Custom session ID (auto-generated if omitted)
    api_url="https://my-server/track", # Self-hosted endpoint
    api_key="cb_...",                  # Dashboard API key
)
```

## How it works

`track()` patches the token-returning method on your client (e.g. `messages.create` for Anthropic). After each call, it extracts token counts from the response and POSTs them to the ContextBudget API in a background thread. Your code gets the original response, unchanged. Tracking never throws -- if the POST fails, it fails silently.

The entire implementation is ~80 lines. Read it: [wrapper.py](contextbudget/wrapper.py)

## License

MIT
