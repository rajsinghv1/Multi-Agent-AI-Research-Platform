import sqlite3
import json
from pathlib import Path
from datetime import datetime, timezone
from contextlib import contextmanager


DB_PATH = Path("data/memory/research_memory.db")


@contextmanager
def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DB_PATH, timeout=30)
    connection.row_factory = sqlite3.Row

    try:
        connection.execute("PRAGMA foreign_keys = ON")
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def init_database():
    """Initialize persistent research memory tables."""

    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS research_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                research_plan TEXT,
                analysis TEXT,
                report TEXT NOT NULL,
                evidence_json TEXT NOT NULL DEFAULT '[]',
                citation_validation_json TEXT NOT NULL DEFAULT '{}',
                created_at TEXT NOT NULL
            )
        """)

        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_research_created
            ON research_history(created_at)
        """)

    print("[OK] Research memory database initialized")


def save_research(
    question,
    report,
    research_plan="",
    analysis="",
    evidence=None,
    citation_validation=None,
):
    """Save a completed research report."""

    if not question.strip():
        raise ValueError("Research question cannot be empty")

    if not report.strip():
        raise ValueError("Research report cannot be empty")

    init_database()

    created_at = datetime.now(timezone.utc).isoformat()

    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO research_history (
                question,
                research_plan,
                analysis,
                report,
                evidence_json,
                citation_validation_json,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                question,
                research_plan,
                analysis,
                report,
                json.dumps(evidence or [], default=str),
                json.dumps(citation_validation or {}, default=str),
                created_at,
            ),
        )

        research_id = cursor.lastrowid

    print(f"[OK] Research saved with ID: {research_id}")

    return research_id


def get_research(research_id):
    """Retrieve a saved research record by ID."""

    init_database()

    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT *
            FROM research_history
            WHERE id = ?
            """,
            (research_id,),
        ).fetchone()

    if row is None:
        return None

    result = dict(row)

    result["evidence"] = json.loads(
        result.pop("evidence_json")
    )

    result["citation_validation"] = json.loads(
        result.pop("citation_validation_json")
    )

    return result


def list_research(limit=10):
    """Return recent research history."""

    init_database()

    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT id, question, created_at
            FROM research_history
            ORDER BY id DESC
            LIMIT ?
            """,
            (max(1, int(limit)),),
        ).fetchall()

    return [dict(row) for row in rows]


def search_research(keyword, limit=10):
    """Search saved research by keyword."""

    init_database()

    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT id, question, report, created_at
            FROM research_history
            WHERE question LIKE ? OR report LIKE ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (
                f"%{keyword}%",
                f"%{keyword}%",
                max(1, int(limit)),
            ),
        ).fetchall()

    return [dict(row) for row in rows]


def delete_research(research_id):
    """Delete a saved research record."""

    init_database()

    with get_connection() as conn:
        cursor = conn.execute(
            """
            DELETE FROM research_history
            WHERE id = ?
            """,
            (research_id,),
        )

        deleted = cursor.rowcount

    return deleted > 0