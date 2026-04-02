# Service Brief: ContextBudget

**Date:** 2026-04-02
**Status:** BRIEFED
**Score:** 20/25

## Problem
Developers using AI CLIs (Claude Code, Gemini CLI, Codex) hit context limits without warning and have zero visibility into what's consuming their token budget -- compression fires silently and drops important state.

## Evidence
- Gemini ships ContextCompressionService (commit `e0044f2`) -- dedicated first-class service for compression
- Codex ships `/context window breakdown` (PR #16620) -- devs demanded visibility
- Claude Code memory-alert plugin (PR #38728) -- community-built because the gap is real
- Three separate teams solving the same visibility gap in the same 48h window = strong convergence signal

## Solution
Lightweight SDK that wraps any LLM client and emits real-time context budget breakdowns -- tokens by category (system prompt, history, tool results, current turn) -- plus a hosted dashboard.

## Persona
Developers and teams building with AI CLIs and agent frameworks who run long sessions and hit context walls. Power users of Claude Code, Gemini CLI, Codex, Aider, Cursor.

## Service Design

**Type:** Micro-SaaS Tool (SDK + dashboard)

**Core endpoints:**
- `POST /api/track` -- receives token usage event (session_id, categories, counts, timestamp)
- `GET /api/session/:id` -- returns session budget breakdown
- `GET /api/dashboard` -- renders live dashboard view
- `POST /api/alert` -- webhook when budget hits configurable threshold (70%, 85%, 95%)

**Frontend:** Single-page dashboard showing:
- Real-time token usage bar (system / history / tools / current)
- Session history with usage trends
- Alert configuration
- Multi-session comparison view

**Backend:** FastAPI on charlie, SQLite for session data

**SDK:** NPM package `@contextbudget/sdk` + Python package `contextbudget`
- < 100 lines, zero dependencies
- Wraps OpenAI/Anthropic/Google clients transparently
- Auto-detects provider from client type
- Emits usage events to dashboard API

## Pricing

| Tier | Price | Includes |
|---|---|---|
| Free | $0 | 3 sessions tracked, 24h retention, basic dashboard |
| Pro | $9/mo | Unlimited sessions, 30d retention, alerts, team sharing |
| Team | $29/mo | Everything + 10 seats, export, API access, Slack alerts |

## 5-Factor Score

| Factor | Score (1-5) | Reasoning |
|---|---|---|
| Specificity | 5 | One problem (context visibility) for one persona (AI CLI power users) |
| Existing spend | 3 | No direct competitor yet, but devs are building plugins to solve this -- willingness to invest time = willingness to pay |
| Build speed | 4 | SDK is <100 lines, dashboard is one page, API is 4 endpoints. Fleet ships in one session. |
| Organic discovery | 4 | "context window" + "token budget" are high-search terms. Reddit/HN communities actively discussing this. |
| Margin | 4 | SQLite + GitHub Pages + charlie. Near-zero per-user cost. Only cost is token counting computation (trivial). |
| **Total** | **20/25** | |

## Launch Communities
1. r/ClaudeAI (270K+) -- "I built a tool that shows where your context tokens are going"
2. r/ChatGPTCoding (180K+) -- same angle
3. r/LocalLLaMA (450K+) -- context management is hot topic
4. Hacker News -- "Show HN: See where your AI context budget goes"
5. Claude Code GitHub Discussions
6. Gemini CLI GitHub Discussions

## SEO Targets
- "context window limit" -- high volume
- "claude code context management" -- growing
- "llm token usage tracking" -- emerging
- "ai agent context budget" -- new term, own it

## Domain Candidates
1. contextbudget.dev
2. contextbudget.com
3. tokenbudget.dev

## Build Notes
- SDK must be truly minimal -- devs won't adopt a heavy dependency
- Dashboard should work without an account (free tier = no signup, just a session URL)
- Priority: ship the SDK first. Dashboard is the retention play.
- Consider: Claude Code hook integration (PostToolUse hook that auto-tracks)

## Revenue Projection (90 days)
- Month 1: $200 (early adopters from HN/Reddit launch, 20 Pro signups)
- Month 2: $800 (SEO indexing, word of mouth in AI dev communities)
- Month 3: $2,000 (team tier adoption, blog content driving organic)
