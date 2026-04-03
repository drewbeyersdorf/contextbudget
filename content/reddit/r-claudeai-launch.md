# Reddit Post: r/ClaudeAI

**Subreddit:** r/ClaudeAI
**Suggested Post Time:** Tuesday or Wednesday, 9-10am EST (peak dev browsing)
**Flair:** Tools / Projects

---

**Title:** I kept hitting context limits without knowing why, so I built a tool that shows where your tokens are going

**Body:**

I've been using Claude Code as my daily driver for about six months now. Love it. But I kept running into this problem where I'd be deep in a session - maybe 40 minutes in - and suddenly Claude starts forgetting things I told it 10 minutes ago. Context window full.

The frustrating part wasn't hitting the limit. It was not knowing WHY I hit it.

Was it my system prompt eating 30% of the window? Was it the tool call history piling up? Was it because I loaded three large files earlier and forgot about them? I had no idea. I was flying blind.

So I built ContextBudget.

It's a lightweight SDK that hooks into your LLM calls and shows you exactly where your context tokens are going. Think of it like a budget tracker, but for your context window. You get a breakdown:

- System prompt: 12,400 tokens (18%)
- Conversation history: 31,200 tokens (46%)
- Tool definitions: 8,100 tokens (12%)
- Tool call results: 14,300 tokens (21%)
- Available: 2,000 tokens (3%)

That "oh shit" moment when you realize your CLAUDE.md and tool definitions alone are eating 30% of your context before you even say anything? Yeah. That was my experience.

For Claude Code specifically, this has been really useful for:

1. **Figuring out which files to stop loading.** I had a habit of reading entire files when I only needed a function. ContextBudget showed me those reads were eating 8-12% of my context each time.

2. **Understanding the tool definition cost.** If you have MCP servers connected, those tool definitions aren't free. Each one takes tokens. I had 40+ tools defined and they were consuming 15% of my context just sitting there.

3. **Timing my compacts better.** Instead of guessing when to compact, I can see the actual percentage and make the call with real data.

The integration is three lines:

```python
from contextbudget import track
client = track(anthropic.Anthropic())
# that's it - check dashboard at localhost:3000
```

Works with the Anthropic SDK, OpenAI SDK, and any provider that uses the standard chat completions format. There's a local dashboard that shows real-time usage, and you can set alerts for when you're approaching limits.

It's free and open source. MIT license.

I'm genuinely curious what other Claude Code users think. Is context visibility something you've been wanting? What would you want to see in the dashboard that I haven't thought of?

**Link:** https://contextbudget.dev

---

**Engagement strategy:** Reply to every comment in the first 2 hours. Ask follow-up questions. Don't be defensive about feature requests - write them down publicly.
