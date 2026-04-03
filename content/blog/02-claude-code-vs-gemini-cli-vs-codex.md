# Claude Code vs Gemini CLI vs Codex: How They Handle Context

**Target keyword:** Claude Code vs Gemini CLI, Claude Code context, Codex context management
**Secondary keywords:** AI coding tools comparison, context window management, Claude Code token usage, Gemini CLI tokens
**Word count target:** 800-1000
**Meta description:** How do Claude Code, Gemini CLI, and OpenAI Codex handle context windows differently? A developer's comparison of context management across the three major AI coding CLIs.

---

Three major AI coding CLIs. Three different context window sizes. Three completely different approaches to managing what fits inside them.

If you're using Claude Code, Gemini CLI, or OpenAI Codex for daily development work, understanding how each one handles context directly affects how useful they are in long sessions.

Here's what I've found after running all three on real projects.

## The basics: window sizes

Let's start with raw capacity:

| Tool | Model | Context Window |
|---|---|---|
| Claude Code | Claude 4 Opus | 200,000 tokens |
| Gemini CLI | Gemini 2.5 Pro | 1,000,000 tokens |
| OpenAI Codex | GPT-4o / o3 | 128,000-200,000 tokens |

On paper, Gemini wins by a huge margin. In practice, it's more nuanced than that.

## Claude Code: compact and manage

Claude Code gives you the most explicit control over context management. The `/compact` command lets you manually compress your conversation when things get bloated. Your CLAUDE.md files (project instructions) load into the system prompt automatically, and you can see when context is getting heavy via the status display.

**What goes into Claude Code's context:**
- System prompt with behavioral instructions
- Your CLAUDE.md files (global, project-level, and directory-level)
- Tool definitions for all connected MCP servers
- Full conversation history
- Tool call results (file reads, bash output, grep results)

**How it handles overflow:** Claude Code will warn you when context is getting full and suggest compacting. When you compact, it summarizes the conversation and drops the verbose middle. You keep the system prompt and a condensed version of what happened.

**The hidden cost:** MCP tool definitions. If you have multiple MCP servers connected (GitHub, Slack, database, Playwright, etc.), each server's tools get defined in the context. I've measured setups where tool definitions alone consume 25,000-40,000 tokens. That's 12-20% of the window before a single message.

## Gemini CLI: brute force with a million tokens

Gemini CLI's approach is essentially: give you so much context that management is rarely necessary. A million tokens is roughly 750,000 words. Most coding sessions won't come close to filling that.

**Where it still matters:** Even with a million-token window, context isn't free. Longer contexts mean higher latency and higher cost. Sending a million tokens per request when you only need 50,000 is wasteful. And quality can degrade with extremely long contexts - the "lost in the middle" problem, where the model pays less attention to information in the middle of a very long context.

**The approach:** Gemini CLI generally doesn't force you to think about context management. It loads what it needs and relies on the massive window to absorb it. For most sessions, this works fine. For extremely long sessions or very large codebases, you'll still eventually hit the wall.

## OpenAI Codex: sandboxed and structured

Codex takes a different architectural approach. It runs in a sandboxed environment and tends toward shorter, more structured interactions. The context management is more opaque - you have less visibility into what's in the window and fewer manual controls.

**How it handles overflow:** Codex tends to manage context internally, truncating older messages and keeping recent exchanges. The sandboxed architecture means it's doing more context management behind the scenes.

**The tradeoff:** Less control, but also less to think about. If you want to just code and not worry about context budgets, Codex's approach is simpler. If you want to optimize, you have fewer levers to pull.

## What none of them show you

Here's the gap that surprised me: none of these tools give you a clear, real-time breakdown of where your tokens are going.

Claude Code shows you a rough context indicator. Gemini CLI shows you almost nothing about token usage. Codex abstracts it away entirely.

But if you're trying to optimize your workflow - figure out why Claude forgot your architecture, why Gemini's responses slowed down, why Codex dropped something important - you need to see the breakdown.

Questions none of them answer natively:
- How many tokens is my system prompt actually using?
- How much context are tool definitions consuming?
- Which file reads are still in context and which got truncated?
- What percentage of my context is conversation vs infrastructure?

## Measuring it yourself

This is why I built [ContextBudget](https://contextbudget.dev). It wraps the underlying SDK calls and gives you the breakdown:

```
Claude Code session (45 min):
System prompt: 22,100 tokens (11.1%)
Tool definitions: 38,400 tokens (19.2%)
Conversation: 108,000 tokens (54.0%)
Tool results: 28,500 tokens (14.3%)
Available: 3,000 tokens (1.5%)
```

That tool definition number (19.2%) was the first thing I optimized. Disconnecting MCP servers I wasn't using in that session recovered nearly 40,000 tokens of headroom.

## Which is best?

It depends on your workflow:

- **Long exploratory sessions:** Gemini CLI's million-token window means you rarely hit the wall.
- **Controlled, optimized sessions:** Claude Code's explicit compacting and CLAUDE.md system gives you the most control.
- **Quick task-based work:** Codex's managed approach means less friction for short interactions.

But regardless of which tool you use, visibility into your context budget makes all of them better. You can't optimize what you can't see.

---

*[ContextBudget](https://contextbudget.dev) works with all three CLIs. Free, open-source, three-line integration.*
