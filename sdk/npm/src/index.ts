/**
 * ContextBudget SDK -- automatic AI context token tracking.
 *
 * Usage:
 *   import { track } from '@contextbudget/sdk'
 *   import Anthropic from '@anthropic-ai/sdk'
 *
 *   const client = track(new Anthropic())
 *   // Every API call now auto-reports token usage to your dashboard
 */

// --- Types ---

interface TrackOptions {
  /** Where to POST usage data. Default: contextbudget.dev/api/track */
  apiUrl?: string
  /** Group calls under one session. Auto-generated if omitted. */
  sessionId?: string
  /** Optional API key for the ContextBudget dashboard. */
  apiKey?: string
}

interface UsagePayload {
  session_id: string
  provider: string
  input_tokens: number
  output_tokens: number
  model: string
  api_key?: string
}

// --- Provider detection ---
// Each provider config tells us: which method path returns tokens, and how to extract them.

interface ProviderConfig {
  path: string
  extract: (response: any) => { input_tokens: number; output_tokens: number; model: string }
}

const PROVIDERS: Record<string, ProviderConfig> = {
  // Anthropic: client.messages.create() -> response.usage.{input_tokens, output_tokens}
  Anthropic: {
    path: 'messages.create',
    extract: (r) => ({
      input_tokens: r.usage.input_tokens,
      output_tokens: r.usage.output_tokens,
      model: r.model,
    }),
  },
  // OpenAI: client.chat.completions.create() -> response.usage.{prompt_tokens, completion_tokens}
  OpenAI: {
    path: 'chat.completions.create',
    extract: (r) => ({
      input_tokens: r.usage.prompt_tokens,
      output_tokens: r.usage.completion_tokens,
      model: r.model,
    }),
  },
  // Google GenAI: model.generateContent() -> response.usageMetadata.{promptTokenCount, candidatesTokenCount}
  GenerativeModel: {
    path: 'generateContent',
    extract: (r) => ({
      input_tokens: r.usageMetadata.promptTokenCount,
      output_tokens: r.usageMetadata.candidatesTokenCount,
      model: 'gemini',
    }),
  },
}

// --- Helpers ---

/** Generate a short random session ID. */
function randomSessionId(): string {
  const chars = 'abcdef0123456789'
  let id = ''
  for (let i = 0; i < 12; i++) {
    id += chars[Math.floor(Math.random() * chars.length)]
  }
  return id
}

/** Walk a dot-separated path on an object: "messages.create" -> obj.messages.create */
function resolve(obj: any, path: string): any {
  for (const part of path.split('.')) {
    obj = obj[part]
  }
  return obj
}

/** Fire-and-forget POST. Tracking should never break your app. */
function report(apiUrl: string, payload: UsagePayload): void {
  fetch(apiUrl, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
    signal: AbortSignal.timeout(2000),
  }).catch(() => {}) // Silent failure -- never affect the user's code
}

/** Detect which AI provider a client belongs to. */
function detectProvider(client: any): [string, ProviderConfig] {
  const className = client.constructor?.name ?? ''
  for (const [name, config] of Object.entries(PROVIDERS)) {
    if (className.includes(name)) return [name, config]
  }
  throw new Error(
    `Unsupported client: ${className}. Supported: Anthropic, OpenAI, Google GenerativeModel`
  )
}

// --- Main export ---

const DEFAULT_API_URL = 'https://contextbudget.dev/api/track'

/**
 * Wrap an AI client to automatically track token usage.
 *
 * Returns the same client with the token-returning method patched.
 * Use it exactly as you would the original -- the interface doesn't change.
 */
export function track<T>(client: T, options: TrackOptions = {}): T {
  const { apiUrl = DEFAULT_API_URL, apiKey } = options
  const sessionId = options.sessionId ?? randomSessionId()

  const [providerName, config] = detectProvider(client)

  // Split "messages.create" into parent path ["messages"] and method "create"
  const pathParts = config.path.split('.')
  const methodName = pathParts.pop()!
  const parent: any = pathParts.length > 0 ? resolve(client, pathParts.join('.')) : client

  // Grab the original method before patching
  const originalMethod = parent[methodName].bind(parent)
  let printed = false

  // Patch with a wrapper that tracks usage after each call
  parent[methodName] = async function (...args: any[]) {
    const response = await originalMethod(...args)

    // Print the dashboard URL once, on first successful call
    if (!printed) {
      console.log(`View your session: https://contextbudget.dev/d/${sessionId}`)
      printed = true
    }

    // Extract token usage from the response
    try {
      const usage = config.extract(response)
      const payload: UsagePayload = {
        session_id: sessionId,
        provider: providerName.toLowerCase(),
        ...usage,
      }
      if (apiKey) payload.api_key = apiKey

      // Fire and forget -- don't await, don't block
      report(apiUrl, payload)
    } catch {
      // Response didn't have usage info -- skip silently
    }

    return response
  }

  return client
}
