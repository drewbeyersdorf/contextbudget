# Hacker News: Show HN

**Post Type:** Show HN
**Suggested Post Time:** Tuesday-Thursday, 8-9am EST (HN prime time)

---

**Title:** Show HN: ContextBudget - See where your AI context tokens go

**URL:** https://contextbudget.dev

**Text:**

Hey HN. I built ContextBudget because I kept hitting context window limits in my AI coding tools without understanding why.

The problem: LLM context windows are a shared budget between your system prompt, conversation history, tool definitions, and tool results. But no tooling shows you the breakdown. You're spending tokens blind.

ContextBudget is a lightweight SDK (Python + JS/TS) that wraps your existing LLM client and tracks token allocation in real time. Three-line integration:

    from contextbudget import track
    client = track(anthropic.Anthropic())
    # dashboard at localhost:3000

What it shows you:
- Token count per category (system, history, tools, results)
- Percentage of context window used
- Per-message cost breakdown
- Historical usage across sessions
- Configurable alerts at thresholds

Works with OpenAI, Anthropic, Ollama, llama.cpp, vLLM, LM Studio, and anything that uses the chat completions format.

One finding that surprised me: tool definitions in a typical agentic setup can consume 15-20% of context before the conversation even starts. Trimming unused tools recovered thousands of tokens.

Everything runs locally. SQLite for storage, no cloud, no telemetry. MIT licensed.

Tech: Python SDK uses tiktoken + sentencepiece for accurate tokenization across providers. Zero overhead on API calls (counting is async). Dashboard is a lightweight Vite app.

Repo: https://github.com/contextbudget/sdk
Docs: https://contextbudget.dev/docs

Happy to answer questions about the implementation.

---

**Engagement strategy:** HN rewards technical depth and honesty. Answer questions quickly. Acknowledge limitations openly. Don't be defensive about "just use the API response token counts" - explain why client-side pre-call estimation is different and useful.
