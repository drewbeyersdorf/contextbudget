# Reddit Post: r/ChatGPTCoding

**Subreddit:** r/ChatGPTCoding
**Suggested Post Time:** Monday or Wednesday, 10-11am EST
**Flair:** Resource / Tool

---

**Title:** Built a free context budget tracker - see exactly how many tokens go to system prompt vs history vs tools

**Body:**

Quick share for anyone who's been frustrated by context window limits and not knowing what's using the space.

I built ContextBudget - a free, open-source tool that breaks down exactly where your tokens are going in every LLM call. It wraps your existing SDK client (OpenAI, Anthropic, whatever) and gives you a real-time dashboard showing:

- How many tokens your system prompt uses
- How much conversation history is accumulated
- What tool definitions cost you
- What tool call results are adding
- How much headroom you have left

**Why this matters more than you'd think:**

Most people assume their conversation history is what fills the context. Sometimes it is. But I've seen setups where the system prompt + tool definitions eat 40% of the window before the user says a single word. If you're using function calling with 20+ tools, each tool schema takes tokens. Those add up fast.

Here's a real example from my own setup:

```
Total context: 128,000 tokens
System prompt: 18,200 (14.2%)
Tool definitions: 22,400 (17.5%)  <-- this surprised me
Conversation: 71,800 (56.1%)
Tool results: 12,100 (9.5%)
Remaining: 3,500 (2.7%)
```

I was blaming my conversation length for hitting limits. Turns out tool definitions were the second biggest consumer. I trimmed 8 tools I wasn't actively using and got back 11% of my context window. That's like getting 14,000 tokens for free.

**How to use it:**

```python
# Python
from contextbudget import track
client = track(OpenAI())

# JavaScript
import { track } from 'contextbudget';
const client = track(new OpenAI());
```

That's the whole integration. Three lines. It proxies your API calls, counts tokens client-side (using tiktoken/the appropriate tokenizer for your model), and serves a local dashboard at localhost:3000.

**Features:**
- Real-time token breakdown by category
- Historical tracking across sessions
- Alerts when you hit configurable thresholds (e.g., warn at 80%)
- Export data as JSON for your own analysis
- Works with GPT-4o, Claude, Gemini, local models - anything with a chat completions-style API
- Zero performance overhead on the API calls themselves (counting happens async)

**What it doesn't do:**
- No cloud. Everything runs locally.
- No telemetry. I don't see your prompts or tokens.
- No paid tier (yet - honestly might never need one)

It's MIT licensed on GitHub. Happy to answer questions about the implementation or take feature requests.

What's been your experience with context limits? Curious if others have found the same tool-definition surprise I did.

**Link:** https://github.com/contextbudget/sdk

---

**Engagement strategy:** Lead with utility. This sub responds to practical tools. Offer to help people debug their specific context issues in the comments.
