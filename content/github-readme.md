<p align="center">
  <h1 align="center">ContextBudget</h1>
  <p align="center">See where your context budget goes.</p>
</p>

<p align="center">
  <a href="https://www.npmjs.com/package/contextbudget"><img src="https://img.shields.io/npm/v/contextbudget?style=flat-square" alt="npm version"></a>
  <a href="https://pypi.org/project/contextbudget/"><img src="https://img.shields.io/pypi/v/contextbudget?style=flat-square" alt="PyPI version"></a>
  <a href="https://github.com/contextbudget/sdk/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue?style=flat-square" alt="License"></a>
  <a href="https://github.com/contextbudget/sdk/stargazers"><img src="https://img.shields.io/github/stars/contextbudget/sdk?style=flat-square" alt="GitHub stars"></a>
</p>

---

LLM context windows are a shared budget between your system prompt, conversation history, tool definitions, and tool results. ContextBudget shows you the breakdown.

```python
from contextbudget import track
client = track(anthropic.Anthropic())
# dashboard at localhost:3000
```

That's it. Your existing code stays the same. ContextBudget wraps your client and tracks token allocation in real time.

## What you'll see

```
Context Window: 200,000 tokens

System prompt     ████████░░░░░░░░░░░░  18,200  (9.1%)
Tool definitions  ██████████░░░░░░░░░░  22,400  (11.2%)
Conversation      ████████████████████  108,300  (54.2%)
Tool results      ██████░░░░░░░░░░░░░░  28,100  (14.1%)
Available         ████░░░░░░░░░░░░░░░░  23,000  (11.5%)
```

## Install

```bash
pip install contextbudget
# or
npm install contextbudget
```

## Quick start

### Python

```python
from contextbudget import track

# OpenAI
from openai import OpenAI
client = track(OpenAI())

# Anthropic
import anthropic
client = track(anthropic.Anthropic())

# Local models (Ollama, llama.cpp, vLLM)
client = track(
    OpenAI(base_url="http://localhost:11434/v1"),
    model_context_length=8192
)
```

### JavaScript / TypeScript

```typescript
import { track } from 'contextbudget';
import OpenAI from 'openai';
import Anthropic from '@anthropic-ai/sdk';

// OpenAI
const openai = track(new OpenAI());

// Anthropic
const anthropic = track(new Anthropic());
```

### Dashboard

```bash
npx contextbudget dashboard
# or
python -m contextbudget dashboard
```

Opens a local dashboard at `localhost:3000` with real-time token breakdown, historical usage, and configurable alerts.

## Features

- **Real-time breakdown** - system prompt, history, tools, results, all with token counts and percentages
- **Per-message tracking** - see the token cost of every message in the conversation
- **Configurable alerts** - get warned at 70%, 80%, 90% or whatever thresholds you set
- **Historical data** - SQLite storage, query your own usage patterns
- **Export** - JSON and CSV export for your own analysis
- **Zero overhead** - token counting is async, no latency added to API calls
- **Fully local** - no cloud, no telemetry, no network calls except to your LLM

## Supported providers

| Provider | SDK | Status |
|---|---|---|
| OpenAI | `openai` | Supported |
| Anthropic | `anthropic` | Supported |
| Google | `google-genai` | Supported |
| Ollama | OpenAI-compatible | Supported |
| llama.cpp | OpenAI-compatible | Supported |
| vLLM | OpenAI-compatible | Supported |
| LM Studio | OpenAI-compatible | Supported |
| LiteLLM | `litellm` | Supported |

## Configuration

```python
client = track(
    OpenAI(),
    dashboard_port=3000,         # default
    storage_path="~/.contextbudget/data.db",  # default
    alert_thresholds=[70, 85, 95],  # percentage warnings
    tokenizer="tiktoken",        # or "sentencepiece", "auto"
    model_context_length=None,   # auto-detected from model, or set manually
)
```

## How it works

ContextBudget wraps your LLM client's API methods (e.g., `chat.completions.create`, `messages.create`). Before each call, it counts tokens in each message category using the appropriate tokenizer. After the call, it records the response tokens. All data goes to a local SQLite database. The dashboard reads from that database.

No proxying. No middleware. No network calls. Just local token counting.

## Docs

Full documentation at [contextbudget.dev/docs](https://contextbudget.dev/docs).

## License

MIT
