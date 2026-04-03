# LinkedIn Launch Post

**Author:** Drew Beyersdorf
**Post Type:** Text post with image (dashboard screenshot)
**Suggested Post Time:** Tuesday or Wednesday, 8-9am EST

---

Three different AI CLI teams shipped context management features in the same 48 hours.

Anthropic released Claude Code's context tracking. Google launched Gemini CLI with context awareness. OpenAI updated Codex with window management.

The gap none of them filled: letting YOU see where your tokens are going.

Your system prompt eats 15%. Tool definitions eat another 15%. Before you type a single word, a third of your context window is gone. And none of these tools show you that.

So I built ContextBudget.

It's a three-line SDK integration that wraps your existing AI client and gives you a real-time dashboard showing exactly where your context tokens are allocated. System prompt, conversation history, tool definitions, tool results - all broken down with percentages.

Think of it like a budget tracker for your AI context window.

What surprised me most: the tool definitions cost. If you have 30+ tools defined (which is normal in an agentic setup), they can consume 20% of your context just sitting there. I trimmed 10 unused tools and got back 14,000 tokens. That's real headroom.

Works with every major provider. Runs entirely locally. MIT licensed. Free.

This started as a tool I built for myself because I was tired of guessing. Turns out a lot of other developers were guessing too.

contextbudget.dev

#AI #DeveloperTools #LLM #OpenSource #ContextWindow

---

**Image:** Dashboard screenshot showing token breakdown with color-coded categories.
**Alt text:** ContextBudget dashboard showing context window usage: system prompt 14.2%, tool definitions 17.5%, conversation 56.1%, tool results 9.5%, remaining 2.7%
