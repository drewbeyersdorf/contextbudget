"""SQLite database setup and queries for ContextBudget.

Why raw SQLite instead of an ORM: token tracking is a hot path --
every API call from every session hits this. sqlite3 with WAL mode
gives us concurrent reads with minimal write contention, and raw SQL
avoids the overhead of object mapping on a schema this simple.
"""

import json
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "sessions.db"

# Connection per-thread -- SQLite handles concurrency via WAL mode,
# but connections themselves are not thread-safe.
_connections: dict[int, sqlite3.Connection] = {}


def get_conn() -> sqlite3.Connection:
    """Get or create a thread-local SQLite connection with WAL mode enabled."""
    import threading

    tid = threading.get_ident()
    if tid not in _connections:
        conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        _connections[tid] = conn
    return _connections[tid]


def init_db() -> None:
    """Create tables if they don't exist. Called once at startup."""
    conn = get_conn()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            provider TEXT NOT NULL,
            cat_system INTEGER DEFAULT 0,
            cat_history INTEGER DEFAULT 0,
            cat_tools INTEGER DEFAULT 0,
            cat_current INTEGER DEFAULT 0,
            total INTEGER NOT NULL,
            token_limit INTEGER NOT NULL,
            timestamp TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE INDEX IF NOT EXISTS idx_events_session
            ON events(session_id);

        CREATE TABLE IF NOT EXISTS alert_configs (
            session_id TEXT PRIMARY KEY,
            thresholds TEXT NOT NULL DEFAULT '[70, 85, 95]',
            webhook_url TEXT,
            updated_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS alerts_triggered (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            threshold INTEGER NOT NULL,
            usage_pct REAL NOT NULL,
            triggered_at TEXT DEFAULT (datetime('now'))
        );

        CREATE INDEX IF NOT EXISTS idx_alerts_session
            ON alerts_triggered(session_id);
    """)


def insert_event(
    session_id: str,
    provider: str,
    cat_system: int,
    cat_history: int,
    cat_tools: int,
    cat_current: int,
    total: int,
    token_limit: int,
    timestamp: str,
) -> float:
    """Insert a tracking event. Returns usage percentage."""
    conn = get_conn()
    conn.execute(
        """INSERT INTO events
           (session_id, provider, cat_system, cat_history, cat_tools,
            cat_current, total, token_limit, timestamp)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            session_id,
            provider,
            cat_system,
            cat_history,
            cat_tools,
            cat_current,
            total,
            token_limit,
            timestamp,
        ),
    )
    conn.commit()
    return round((total / token_limit) * 100, 2) if token_limit > 0 else 0.0


def get_session_events(session_id: str) -> list[dict]:
    """Get all events for a session, ordered by time."""
    conn = get_conn()
    rows = conn.execute(
        """SELECT session_id, provider, cat_system, cat_history,
                  cat_tools, cat_current, total, token_limit, timestamp
           FROM events
           WHERE session_id = ?
           ORDER BY id ASC""",
        (session_id,),
    ).fetchall()
    return [
        {
            "session_id": r["session_id"],
            "provider": r["provider"],
            "categories": {
                "system": r["cat_system"],
                "history": r["cat_history"],
                "tools": r["cat_tools"],
                "current": r["cat_current"],
            },
            "total": r["total"],
            "limit": r["token_limit"],
            "timestamp": r["timestamp"],
        }
        for r in rows
    ]


def get_session_summary(session_id: str) -> dict:
    """Compute aggregate summary for a session."""
    conn = get_conn()

    row = conn.execute(
        """SELECT
               COALESCE(SUM(total), 0) AS total_tokens,
               COALESCE(SUM(cat_system), 0) AS sum_system,
               COALESCE(SUM(cat_history), 0) AS sum_history,
               COALESCE(SUM(cat_tools), 0) AS sum_tools,
               COALESCE(SUM(cat_current), 0) AS sum_current,
               COALESCE(MAX(token_limit), 0) AS max_limit
           FROM events
           WHERE session_id = ?""",
        (session_id,),
    ).fetchone()

    # Latest event gives current usage percentage.
    # Order by id (not created_at) because created_at has 1-second
    # resolution and events can arrive within the same second.
    latest = conn.execute(
        """SELECT total, token_limit
           FROM events
           WHERE session_id = ?
           ORDER BY id DESC
           LIMIT 1""",
        (session_id,),
    ).fetchone()

    usage_pct = 0.0
    if latest and latest["token_limit"] > 0:
        usage_pct = round((latest["total"] / latest["token_limit"]) * 100, 2)

    alert_count = conn.execute(
        "SELECT COUNT(*) AS cnt FROM alerts_triggered WHERE session_id = ?",
        (session_id,),
    ).fetchone()["cnt"]

    return {
        "total_tokens": row["total_tokens"],
        "by_category": {
            "system": row["sum_system"],
            "history": row["sum_history"],
            "tools": row["sum_tools"],
            "current": row["sum_current"],
        },
        "usage_pct": usage_pct,
        "alerts_triggered": alert_count,
    }


def upsert_alert_config(
    session_id: str, thresholds: list[int], webhook_url: str | None
) -> None:
    """Create or update alert configuration for a session."""
    conn = get_conn()
    conn.execute(
        """INSERT INTO alert_configs (session_id, thresholds, webhook_url, updated_at)
           VALUES (?, ?, ?, datetime('now'))
           ON CONFLICT(session_id) DO UPDATE SET
               thresholds = excluded.thresholds,
               webhook_url = excluded.webhook_url,
               updated_at = excluded.updated_at""",
        (session_id, json.dumps(thresholds), webhook_url),
    )
    conn.commit()


def get_alert_config(session_id: str) -> dict | None:
    """Get alert config for a session."""
    conn = get_conn()
    row = conn.execute(
        "SELECT thresholds, webhook_url FROM alert_configs WHERE session_id = ?",
        (session_id,),
    ).fetchone()
    if not row:
        return None
    return {
        "thresholds": json.loads(row["thresholds"]),
        "webhook_url": row["webhook_url"],
    }


def record_alert(session_id: str, threshold: int, usage_pct: float) -> None:
    """Record that an alert threshold was triggered."""
    conn = get_conn()
    conn.execute(
        """INSERT INTO alerts_triggered (session_id, threshold, usage_pct)
           VALUES (?, ?, ?)""",
        (session_id, threshold, usage_pct),
    )
    conn.commit()


def get_triggered_thresholds(session_id: str) -> set[int]:
    """Get set of thresholds already triggered for this session."""
    conn = get_conn()
    rows = conn.execute(
        "SELECT DISTINCT threshold FROM alerts_triggered WHERE session_id = ?",
        (session_id,),
    ).fetchall()
    return {r["threshold"] for r in rows}
