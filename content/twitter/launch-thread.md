# Twitter/X Launch Thread

**Suggested Post Time:** Tuesday-Thursday, 9-10am EST
**Thread length:** 5 tweets

---

**Tweet 1 (Problem):**

Three different AI CLI teams shipped context management features in the same week.

None of them answered the most basic question: where are my tokens actually going?

So I built a tool that does. Here's what I found. (thread)

---

**Tweet 2 (Insight):**

Your AI context window is a shared budget:
- System prompt
- Conversation history
- Tool definitions
- Tool call results

In a typical agentic setup, the system prompt + tool definitions eat 30% of your context before you type anything.

You're starting every conversation at 70%.

---

**Tweet 3 (Solution):**

ContextBudget is a 3-line SDK that wraps your existing LLM client and shows you the breakdown in real time.

```python
from contextbudget import track
client = track(OpenAI())
# dashboard at localhost:3000
```

Works with OpenAI, Anthropic, Ollama, local models. Free and open source.

---

**Tweet 4 (Demo):**

[Screenshot description: Dashboard showing real-time context window breakdown with color-coded bars]

The moment I saw this, I trimmed 10 unused tool definitions and got back 14,000 tokens.

That's the difference between your AI forgetting everything you said 5 minutes ago and having room to actually think.

---

**Tweet 5 (CTA):**

Free. MIT licensed. Runs locally. No telemetry.

contextbudget.dev
github.com/contextbudget/sdk

If you've ever wondered why your AI suddenly got amnesia mid-conversation, this will show you exactly why.

---

**Notes:**
- Pin Tweet 1 to profile during launch week
- Quote-tweet the thread with a one-liner the next day for reach
- Reply to the thread with specific examples/findings over the next few days
