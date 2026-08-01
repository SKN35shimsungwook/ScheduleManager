"""SQLite connection and schema initialization."""

import sqlite3
from pathlib import Path

import streamlit as st

DB_PATH = Path(__file__).resolve().parent.parent / "database" / "schedule.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS schedules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    start_time TEXT NOT NULL,
    end_time TEXT,
    title TEXT NOT NULL,
    category TEXT NOT NULL DEFAULT '기타',
    memo TEXT DEFAULT '',
    is_done INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS certificates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    exam_date TEXT NOT NULL,
    memo TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS cert_subjects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    certificate_id INTEGER NOT NULL REFERENCES certificates(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    is_done INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS study_targets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    certificate_id INTEGER REFERENCES certificates(id) ON DELETE SET NULL,
    subject_name TEXT NOT NULL,
    target_minutes INTEGER NOT NULL DEFAULT 0,
    is_done INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS study_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    subject_name TEXT NOT NULL,
    certificate_id INTEGER REFERENCES certificates(id) ON DELETE SET NULL,
    duration_minutes INTEGER NOT NULL DEFAULT 0,
    memo TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS todos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    content TEXT NOT NULL,
    priority TEXT NOT NULL DEFAULT '보통',
    is_done INTEGER NOT NULL DEFAULT 0
);
"""


@st.cache_resource
def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA)
    conn.commit()
    return conn
