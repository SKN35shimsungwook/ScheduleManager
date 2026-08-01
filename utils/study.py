"""CRUD helpers for study targets (daily checklist) and study logs (time records)."""

import datetime as dt

import pandas as pd

from utils.db import get_connection


# ---- Study targets (today's study checklist) -----------------------------

def list_targets_for_date(date: dt.date) -> pd.DataFrame:
    conn = get_connection()
    rows = conn.execute(
        "SELECT t.id, t.date, t.certificate_id, c.name AS certificate_name, "
        "t.subject_name, t.target_minutes, t.is_done "
        "FROM study_targets t LEFT JOIN certificates c ON c.id = t.certificate_id "
        "WHERE t.date = ? ORDER BY t.id",
        (date.isoformat(),),
    ).fetchall()
    return pd.DataFrame(
        [dict(r) for r in rows],
        columns=["id", "date", "certificate_id", "certificate_name", "subject_name", "target_minutes", "is_done"],
    )


def add_target(date: dt.date, subject_name: str, target_minutes: int, certificate_id: int | None = None) -> None:
    conn = get_connection()
    conn.execute(
        "INSERT INTO study_targets (date, certificate_id, subject_name, target_minutes) VALUES (?, ?, ?, ?)",
        (date.isoformat(), certificate_id, subject_name, target_minutes),
    )
    conn.commit()


def set_target_done(target_id: int, is_done: bool) -> None:
    conn = get_connection()
    conn.execute("UPDATE study_targets SET is_done = ? WHERE id = ?", (int(is_done), target_id))
    conn.commit()


def delete_target(target_id: int) -> None:
    conn = get_connection()
    conn.execute("DELETE FROM study_targets WHERE id = ?", (target_id,))
    conn.commit()


# ---- Study logs (actual recorded study time) ------------------------------

def list_logs_between(start: dt.date, end: dt.date) -> pd.DataFrame:
    conn = get_connection()
    rows = conn.execute(
        "SELECT l.id, l.date, l.subject_name, l.certificate_id, c.name AS certificate_name, "
        "l.duration_minutes, l.memo "
        "FROM study_logs l LEFT JOIN certificates c ON c.id = l.certificate_id "
        "WHERE l.date BETWEEN ? AND ? ORDER BY l.date, l.id",
        (start.isoformat(), end.isoformat()),
    ).fetchall()
    return pd.DataFrame(
        [dict(r) for r in rows],
        columns=["id", "date", "subject_name", "certificate_id", "certificate_name", "duration_minutes", "memo"],
    )


def add_log(date: dt.date, subject_name: str, duration_minutes: int, certificate_id: int | None = None, memo: str = "") -> None:
    conn = get_connection()
    conn.execute(
        "INSERT INTO study_logs (date, subject_name, certificate_id, duration_minutes, memo) "
        "VALUES (?, ?, ?, ?, ?)",
        (date.isoformat(), subject_name, certificate_id, duration_minutes, memo),
    )
    conn.commit()


def delete_log(log_id: int) -> None:
    conn = get_connection()
    conn.execute("DELETE FROM study_logs WHERE id = ?", (log_id,))
    conn.commit()


def total_minutes_for_date(date: dt.date) -> int:
    conn = get_connection()
    row = conn.execute(
        "SELECT COALESCE(SUM(duration_minutes), 0) AS total FROM study_logs WHERE date = ?",
        (date.isoformat(),),
    ).fetchone()
    return int(row["total"])


def streak_days(as_of: dt.date | None = None) -> int:
    """Count consecutive days (ending at as_of) with at least one study log."""
    as_of = as_of or dt.date.today()
    conn = get_connection()
    dates = {
        r["date"]
        for r in conn.execute(
            "SELECT DISTINCT date FROM study_logs WHERE date <= ?", (as_of.isoformat(),)
        ).fetchall()
    }
    streak = 0
    cursor = as_of
    while cursor.isoformat() in dates:
        streak += 1
        cursor -= dt.timedelta(days=1)
    return streak
