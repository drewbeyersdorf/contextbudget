# @contextbudget/sdk

Automatic AI context token tracking. One line to add to your code.

## Install

```bash
npm install @contextbudget/sdk
```

## Usage

```typescript
import { track } from '@contextbudget/sdk'
import Anthropic from '@anthropic-ai/sdk'

const client = track(new Anthropic())

// Use the client exactly as before -- tracking is automatic
const response = await client.messages.create({
  model: 'claude-sonnet-4-20250514',
  max_tokens: 1024,
  messages: [{ role: 'user', content: 'Hello' }]
})
// Prints: View your session: https://contextbudget.dev/d/a1b2c3d4e5f6
```

Works with Anthropic, OpenAI, and Google GenAI:

```typescript
// OpenAI
import OpenAI from 'openai'
const openai = track(new OpenAI())

// Google
import { GoogleGenerativeAI } from '@google/generative-ai'
const genai = new GoogleGenerativeAI('key')
const model = track(genai.getGenerativeModel({ model: 'gemini-pro' }))
```

## Configuration

```typescript
const client = track(new Anthropic(), {
  sessionId: 'my-session',              // Custom session ID (auto-generated if omitted)
  apiUrl: 'https://my-server/track',    // Self-hosted endpoint
  apiKey: 'cb_...',                      // Dashboard API key
})
```

## How it works

`track()` patches the token-returning method on your client (e.g. `messages.create` for Anthropic). After each call, it extracts token counts from the response and POSTs them to the ContextBudget API via `fetch()`. Your code gets the original response, unchanged. Tracking never throws -- if the POST fails, it fails silently.

The entire implementation is ~80 lines. Read it: [src/index.ts](src/index.ts)

## Zero dependencies

Uses the built-in `fetch` API (Node 18+). No extra packages needed.

## License

MIT
