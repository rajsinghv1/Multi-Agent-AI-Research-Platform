import hashlib
import json
import sqlite3
import time
from pathlib import Path


DB_PATH = Path("data/research_cache.db")
CACHE_TTL = 24 * 60 * 60


def connect():
    DB_PATH.parent.mkdir(
        parents=True, exist_ok=True
    )

    connection = sqlite3.connect(DB_PATH)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS research_cache (
            cache_key TEXT PRIMARY KEY,
            result_json TEXT NOT NULL,
            created_at REAL NOT NULL
        )
    """)

    return connection


def make_key(query):
    normalized = " ".join(query.lower().split())

    return hashlib.sha256(
        normalized.encode("utf-8")
    ).hexdigest()


def get_cached(query):
    key = make_key(query)

    with connect() as db:
        row = db.execute(
            """
            SELECT result_json, created_at
            FROM research_cache
            WHERE cache_key = ?
            """,
            (key,)
        ).fetchone()

    if row is None:
        return None

    if time.time() - row[1] > CACHE_TTL:
        return None

    return json.loads(row[0])


def save_cache(query, result):
    key = make_key(query)

    with connect() as db:
        db.execute(
            """
            INSERT OR REPLACE INTO research_cache
            (cache_key, result_json, created_at)
            VALUES (?, ?, ?)
            """,
            (
                key,
                json.dumps(result, default=str),
                time.time()
            )
        )
        db.commit()