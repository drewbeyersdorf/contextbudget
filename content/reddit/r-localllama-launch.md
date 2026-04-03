# Reddit Post: r/LocalLLaMA

**Subreddit:** r/LocalLLaMA
**Suggested Post Time:** Thursday, 11am-1pm EST (high engagement window)
**Flair:** Resources

---

**Title:** Open-source SDK for tracking context window usage across any LLM provider

**Body:**

Hey all. Been lurking here for a while and using a lot of the stuff you folks recommend. Built something I think the local model crowd will find useful - maybe more useful than the API-only people, actually, because context management matters even more when you're running smaller windows.

**ContextBudget** is an open-source SDK (Python and JS/TS) that tracks and visualizes where your context window tokens are going. It works with any LLM provider - OpenAI, Anthropic, Ollama, llama.cpp, vLLM, LM Studio, anything that speaks the chat completions format.

**Why local model users should care:**

When you're running a 7B or 13B model with a 4K-8K context window, every token matters. You don't have the luxury of a 128K or 200K window where inefficiency is just annoying. With smaller windows, a bloated system prompt or unnecessary tool definitions can cut your usable context in half.

ContextBudget shows you exactly what's happening:

```
Model: Qwen2.5-7B (8192 context)
System prompt: 1,840 tokens (22.5%)
Tool definitions: 920 tokens (11.2%)
Conversation: 4,200 tokens (51.3%)
Available: 1,232 tokens (15.0%)
```

That visibility lets you make real decisions. Maybe you compress your system prompt. Maybe you strip tool definitions you're not using in this session. Maybe you implement sliding window on conversation history. The point is, you can't optimize what you can't see.

**Technical details:**

- Pure Python, no heavy dependencies. The core is just a wrapper that intercepts messages before they hit your LLM endpoint and counts tokens.
- Tokenizer support: tiktoken for OpenAI-compatible, SentencePiece for Llama-family, configurable for custom tokenizers.
- Pluggable backend: works with raw HTTP, the OpenAI client library, LiteLLM, or direct llama.cpp bindings.
- Local dashboard served on localhost. No cloud, no telemetry, no network calls except to your own LLM.
- SQLite storage for historical tracking. Query your own token usage data however you want.

**Integration with Ollama:**

```python
from contextbudget import track
from openai import OpenAI

# Point at your Ollama instance
client = track(
    OpenAI(base_url="http://localhost:11434/v1"),
    model_context_length=8192,  # set your actual context size
    tokenizer="sentencepiece"    # or auto-detect from model
)
```

**Integration with llama.cpp server:**

```python
from contextbudget import track
from openai import OpenAI

client = track(
    OpenAI(base_url="http://localhost:8080/v1"),
    model_context_length=4096
)
```

**What's in the dashboard:**
- Real-time bar showing context usage by category
- Time-series chart of context fill rate across a conversation
- Per-message token cost breakdown
- Warnings when you're about to overflow (configurable threshold)
- Export to JSON/CSV

**What I want to build next (and would love input on):**
- Context compression suggestions (e.g., "this tool definition could be 40% smaller")
- KV cache utilization tracking for llama.cpp (if anyone knows a clean way to query this)
- Automatic sliding window management
- Integration with text-generation-webui and Open WebUI

The whole thing is MIT licensed. No paid anything. I use it myself every day with a mix of local and API models.

Repo: https://github.com/contextbudget/sdk
Docs: https://contextbudget.dev/docs

Interested to hear if this solves a problem you've been having, or if you've built your own version of this already.

---

**Engagement strategy:** This sub values technical depth. Be ready to discuss tokenizer implementation, performance benchmarks, and specific model compatibility. Offer to add support for models/providers people request.
