"""ContextBudget API -- tracks AI context token usage.

FastAPI app with SQLite storage, Stripe billing, and a live dashboard.
Designed to be fast, reliable, and simple to deploy.
"""

import os
from contextlib import asynccontextmanager

import stripe
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

import db
from models import (
    AlertConfig,
    AlertConfigResponse,
    CheckoutRequest,
    HealthResponse,
    SessionResponse,
    SessionSummary,
    TrackEvent,
    TrackResponse,
)

load_dotenv()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")

# Stripe price IDs -- set these in .env for your Stripe account
PRICE_IDS = {
    "pro": os.getenv("STRIPE_PRICE_PRO", "price_pro_placeholder"),
    "team": os.getenv("STRIPE_PRICE_TEAM", "price_team_placeholder"),
}

BASE_URL = os.getenv("BASE_URL", "http://localhost:8091")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize DB on startup."""
    db.init_db()
    yield


app = FastAPI(
    title="ContextBudget",
    description="Track AI context token usage across sessions",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS -- wide open for dev, tighten origins in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# 1. POST /api/track -- receive token usage event
# ---------------------------------------------------------------------------
@app.post("/api/track", response_model=TrackResponse)
async def track_usage(event: TrackEvent):
    """Record a token usage event and return current usage percentage.

    This is the hot path -- every tool call from every session hits this.
    We do a single INSERT and compute usage_pct inline. No extra queries.
    """
    usage_pct = db.insert_event(
        session_id=event.session_id,
        provider=event.provider,
        cat_system=event.categories.system,
        cat_history=event.categories.history,
        cat_tools=event.categories.tools,
        cat_current=event.categories.current,
        total=event.total,
        token_limit=event.limit,
        timestamp=event.timestamp,
    )

    # Check alert thresholds -- fire any that are newly crossed
    _check_alerts(event.session_id, usage_pct)

    return TrackResponse(
        status="ok",
        session_id=event.session_id,
        usage_pct=usage_pct,
    )


def _check_alerts(session_id: str, usage_pct: float) -> None:
    """Fire alerts for any newly-crossed thresholds.

    Why here instead of async: alert checking is a single SELECT + conditional
    INSERTs. Sub-millisecond. Not worth the complexity of a background task.
    """
    config = db.get_alert_config(session_id)
    if not config:
        return

    already_triggered = db.get_triggered_thresholds(session_id)
    for threshold in config["thresholds"]:
        if usage_pct >= threshold and threshold not in already_triggered:
            db.record_alert(session_id, threshold, usage_pct)
            # Future: POST to config["webhook_url"] if set


# ---------------------------------------------------------------------------
# 2. GET /api/session/{session_id} -- session budget breakdown
# ---------------------------------------------------------------------------
@app.get("/api/session/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str):
    """Return full event history and aggregate summary for a session."""
    events = db.get_session_events(session_id)
    if not events:
        raise HTTPException(status_code=404, detail="Session not found")

    summary_data = db.get_session_summary(session_id)
    return SessionResponse(
        session_id=session_id,
        events=events,
        summary=SessionSummary(**summary_data),
    )


# ---------------------------------------------------------------------------
# 3. GET /api/dashboard/{session_id} -- live HTML dashboard
# ---------------------------------------------------------------------------
@app.get("/api/dashboard/{session_id}", response_class=HTMLResponse)
async def dashboard(session_id: str):
    """Serve a self-contained HTML dashboard that polls for updates.

    Why polling over SSE: simpler to deploy (no sticky sessions needed),
    works behind any reverse proxy, and 2-second intervals are fine for
    a token budget display. SSE would save bandwidth but add complexity.
    """
    return HTMLResponse(content=_render_dashboard(session_id))


def _render_dashboard(session_id: str) -> str:
    """Generate a self-contained HTML page with embedded JS for polling."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>ContextBudget - {session_id}</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
    background: #0a0a0a; color: #e0e0e0;
    padding: 1.5rem; max-width: 900px; margin: 0 auto;
  }}
  h1 {{ font-size: 1.4rem; margin-bottom: 0.25rem; color: #fff; }}
  .session-id {{ font-size: 0.85rem; color: #888; margin-bottom: 1.5rem; font-family: monospace; }}
  .gauge-container {{
    background: #141414; border: 1px solid #222; border-radius: 12px;
    padding: 2rem; margin-bottom: 1.5rem; text-align: center;
  }}
  .gauge-bar {{
    width: 100%; height: 32px; background: #1a1a1a; border-radius: 16px;
    overflow: hidden; margin: 1rem 0;
  }}
  .gauge-fill {{
    height: 100%; border-radius: 16px;
    transition: width 0.6s ease, background 0.6s ease;
  }}
  .gauge-pct {{ font-size: 2.5rem; font-weight: 700; }}
  .gauge-label {{ font-size: 0.85rem; color: #888; margin-top: 0.25rem; }}
  .categories {{
    display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 1rem; margin-bottom: 1.5rem;
  }}
  .cat-card {{
    background: #141414; border: 1px solid #222; border-radius: 8px;
    padding: 1rem;
  }}
  .cat-name {{ font-size: 0.75rem; text-transform: uppercase; color: #888; letter-spacing: 0.05em; }}
  .cat-value {{ font-size: 1.5rem; font-weight: 600; margin-top: 0.25rem; }}
  .cat-bar {{ width: 100%; height: 4px; background: #1a1a1a; border-radius: 2px; margin-top: 0.5rem; }}
  .cat-bar-fill {{ height: 100%; border-radius: 2px; transition: width 0.6s ease; }}
  .events-table {{
    width: 100%; border-collapse: collapse; font-size: 0.85rem;
  }}
  .events-table th {{
    text-align: left; padding: 0.5rem; border-bottom: 1px solid #222;
    color: #888; font-weight: 500; font-size: 0.75rem; text-transform: uppercase;
  }}
  .events-table td {{ padding: 0.5rem; border-bottom: 1px solid #1a1a1a; }}
  .alerts {{ margin-bottom: 1.5rem; }}
  .alert-badge {{
    display: inline-block; padding: 0.25rem 0.75rem; border-radius: 4px;
    font-size: 0.8rem; font-weight: 500; margin-right: 0.5rem; margin-bottom: 0.25rem;
  }}
  .alert-active {{ background: #3d1c1c; color: #ff6b6b; }}
  .alert-pending {{ background: #1c1c1c; color: #555; }}
  .status {{ font-size: 0.75rem; color: #444; text-align: center; margin-top: 1rem; }}
  .section-title {{ font-size: 0.9rem; color: #aaa; margin-bottom: 0.75rem; font-weight: 600; }}
</style>
</head>
<body>
<h1>ContextBudget</h1>
<div class="session-id">{session_id}</div>

<div class="gauge-container">
  <div class="gauge-pct" id="pct">--</div>
  <div class="gauge-bar"><div class="gauge-fill" id="fill" style="width:0%"></div></div>
  <div class="gauge-label"><span id="total">0</span> / <span id="limit">0</span> tokens</div>
</div>

<div class="categories" id="cats">
  <div class="cat-card"><div class="cat-name">System</div><div class="cat-value" id="cat-system">0</div><div class="cat-bar"><div class="cat-bar-fill" id="bar-system" style="width:0%;background:#6366f1"></div></div></div>
  <div class="cat-card"><div class="cat-name">History</div><div class="cat-value" id="cat-history">0</div><div class="cat-bar"><div class="cat-bar-fill" id="bar-history" style="width:0%;background:#22d3ee"></div></div></div>
  <div class="cat-card"><div class="cat-name">Tools</div><div class="cat-value" id="cat-tools">0</div><div class="cat-bar"><div class="cat-bar-fill" id="bar-tools" style="width:0%;background:#a78bfa"></div></div></div>
  <div class="cat-card"><div class="cat-name">Current</div><div class="cat-value" id="cat-current">0</div><div class="cat-bar"><div class="cat-bar-fill" id="bar-current" style="width:0%;background:#34d399"></div></div></div>
</div>

<div class="alerts" id="alerts-section" style="display:none">
  <div class="section-title">Alerts</div>
  <div id="alerts"></div>
</div>

<div>
  <div class="section-title">Event History</div>
  <table class="events-table">
    <thead><tr><th>Time</th><th>Provider</th><th>Total</th><th>Usage</th></tr></thead>
    <tbody id="events"></tbody>
  </table>
</div>

<div class="status" id="status">Connecting...</div>

<script>
const SID = "{session_id}";
const API = window.location.origin;

function fmt(n) {{
  if (n >= 1e6) return (n/1e6).toFixed(1) + "M";
  if (n >= 1e3) return (n/1e3).toFixed(1) + "K";
  return n.toString();
}}

function gaugeColor(pct) {{
  if (pct >= 90) return "#ef4444";
  if (pct >= 70) return "#f59e0b";
  return "#22c55e";
}}

async function poll() {{
  try {{
    const r = await fetch(API + "/api/session/" + SID);
    if (!r.ok) {{
      document.getElementById("status").textContent = "No data yet. Waiting...";
      return;
    }}
    const d = await r.json();
    const s = d.summary;
    const pct = s.usage_pct;

    document.getElementById("pct").textContent = pct.toFixed(1) + "%";
    document.getElementById("pct").style.color = gaugeColor(pct);
    document.getElementById("fill").style.width = Math.min(pct, 100) + "%";
    document.getElementById("fill").style.background = gaugeColor(pct);

    const last = d.events[d.events.length - 1];
    document.getElementById("total").textContent = fmt(last ? last.total : 0);
    document.getElementById("limit").textContent = fmt(last ? last.limit : 0);

    const bc = s.by_category;
    const catTotal = bc.system + bc.history + bc.tools + bc.current || 1;
    ["system","history","tools","current"].forEach(c => {{
      document.getElementById("cat-" + c).textContent = fmt(bc[c]);
      document.getElementById("bar-" + c).style.width = ((bc[c]/catTotal)*100).toFixed(1) + "%";
    }});

    const tbody = document.getElementById("events");
    tbody.innerHTML = d.events.slice(-20).reverse().map(e => {{
      const u = e.limit > 0 ? ((e.total/e.limit)*100).toFixed(1) : "0.0";
      return `<tr><td>${{e.timestamp}}</td><td>${{e.provider}}</td><td>${{fmt(e.total)}}</td><td style="color:${{gaugeColor(parseFloat(u))}}">${{u}}%</td></tr>`;
    }}).join("");

    if (s.alerts_triggered > 0) {{
      document.getElementById("alerts-section").style.display = "block";
      document.getElementById("alerts").innerHTML =
        `<span class="alert-badge alert-active">${{s.alerts_triggered}} alert(s) triggered</span>`;
    }}

    document.getElementById("status").textContent = "Live -- polling every 2s";
  }} catch(e) {{
    document.getElementById("status").textContent = "Error: " + e.message;
  }}
}}

poll();
setInterval(poll, 2000);
</script>
</body>
</html>"""


# ---------------------------------------------------------------------------
# 4. POST /api/alert/configure -- set alert thresholds
# ---------------------------------------------------------------------------
@app.post("/api/alert/configure", response_model=AlertConfigResponse)
async def configure_alerts(config: AlertConfig):
    """Set or update alert thresholds for a session.

    Thresholds are percentage values. When usage crosses a threshold
    for the first time, we record it (and eventually fire a webhook).
    """
    db.upsert_alert_config(config.session_id, config.thresholds, config.webhook_url)
    return AlertConfigResponse(
        status="ok",
        session_id=config.session_id,
        thresholds=config.thresholds,
    )


# ---------------------------------------------------------------------------
# 5. GET /api/health -- health check
# ---------------------------------------------------------------------------
@app.get("/api/health", response_model=HealthResponse)
async def health():
    return HealthResponse()


# ---------------------------------------------------------------------------
# 6. POST /create-checkout-session -- Stripe checkout
# ---------------------------------------------------------------------------
@app.post("/create-checkout-session")
async def create_checkout_session(req: CheckoutRequest):
    """Create a Stripe Checkout session for pro or team tier.

    Tradeoff: server-side checkout (vs client-side) means the price ID
    never touches the client, so users can't tamper with it. Slightly
    more server work, but worth it for billing integrity.
    """
    if req.tier not in PRICE_IDS:
        raise HTTPException(status_code=400, detail=f"Invalid tier: {req.tier}")

    if not stripe.api_key:
        raise HTTPException(status_code=503, detail="Stripe not configured")

    try:
        session = stripe.checkout.Session.create(
            mode="subscription",
            line_items=[{"price": PRICE_IDS[req.tier], "quantity": 1}],
            success_url=f"{BASE_URL}/api/health?checkout=success",
            cancel_url=f"{BASE_URL}/api/health?checkout=cancel",
        )
        return {"url": session.url}
    except stripe.StripeError as e:
        raise HTTPException(status_code=502, detail=str(e))


# ---------------------------------------------------------------------------
# 7. POST /webhook -- Stripe webhook handler
# ---------------------------------------------------------------------------
@app.post("/webhook")
async def stripe_webhook(request: Request):
    """Handle Stripe webhook events (checkout completion, subscription changes).

    Why verify signature: without it, anyone can POST fake events and
    grant themselves a subscription. The webhook secret ensures only
    Stripe can trigger this endpoint.
    """
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")

    if not STRIPE_WEBHOOK_SECRET:
        raise HTTPException(status_code=503, detail="Webhook secret not configured")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Handle the events we care about
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        # Future: activate subscription for session["customer_email"]
        # For now, just acknowledge receipt
        return {"status": "ok", "event": "checkout.session.completed"}

    if event["type"] == "customer.subscription.deleted":
        # Future: deactivate subscription
        return {"status": "ok", "event": "customer.subscription.deleted"}

    return {"status": "ok", "event": event["type"]}
