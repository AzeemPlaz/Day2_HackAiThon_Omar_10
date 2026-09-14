"""SQLite persistence layer for EcoTrack."""
from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Optional

DB_PATH = Path(__file__).resolve().parent / "ecotrack.db"

SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    password_salt TEXT NOT NULL,
    security_q1 TEXT NOT NULL,
    security_a1_hash TEXT NOT NULL,
    security_a1_salt TEXT NOT NULL,
    security_q2 TEXT NOT NULL,
    security_a2_hash TEXT NOT NULL,
    security_a2_salt TEXT NOT NULL,
    theme TEXT NOT NULL DEFAULT 'light',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS waste_records (
    user_id INTEGER NOT NULL,
    item_id INTEGER NOT NULL,
    record_date TEXT NOT NULL,
    category TEXT NOT NULL CHECK(category IN ('Organic','Plastic','Paper','E-waste','Glass')),
    weight_kg REAL NOT NULL CHECK(weight_kg > 0 AND weight_kg <= 200),
    recycled INTEGER NOT NULL DEFAULT 0 CHECK(recycled IN (0,1)),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY(user_id, item_id),
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_waste_user_date ON waste_records(user_id, record_date);
CREATE INDEX IF NOT EXISTS idx_waste_user_category ON waste_records(user_id, category);

CREATE TABLE IF NOT EXISTS ideas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    idea_text TEXT NOT NULL,
    source TEXT NOT NULL DEFAULT 'user',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS reward_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    record_user_id INTEGER,
    record_item_id INTEGER,
    transaction_date TEXT NOT NULL,
    reason TEXT NOT NULL,
    kilograms REAL NOT NULL,
    points REAL NOT NULL,
    value_inr REAL NOT NULL,
    UNIQUE(record_user_id, record_item_id),
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY(record_user_id, record_item_id) REFERENCES waste_records(user_id, item_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_rewards_user_date ON reward_transactions(user_id, transaction_date);
"""


def connect(path: Path | str = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def connection(path: Path | str = DB_PATH) -> Iterator[sqlite3.Connection]:
    conn = connect(path)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def initialize_database(path: Path | str = DB_PATH) -> None:
    with connection(path) as conn:
        conn.executescript(SCHEMA)


def next_item_id(conn: sqlite3.Connection, user_id: int) -> int:
    row = conn.execute("SELECT COALESCE(MAX(item_id), 0) + 1 AS next_id FROM waste_records WHERE user_id = ?", (user_id,)).fetchone()
    return int(row["next_id"])


def get_user_by_username(username: str, path: Path | str = DB_PATH) -> Optional[sqlite3.Row]:
    with connection(path) as conn:
        return conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
