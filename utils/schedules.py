"""CRUD helpers for the schedules table."""

import datetime as dt

import pandas as pd

from utils.db import get_connection

CATEGORIES = ["회사", "공부", "운동", "병원", "약속", "시험", "기타"]


def list_between(start: dt.date, end: dt.date) -> pd.DataFrame:
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, date, start_time, end_time, title, category, memo, is_done "
        "FROM schedules WHERE date BETWEEN ? AND ? "
        "ORDER BY date, start_time",
        (start.isoformat(), end.isoformat()),
    ).fetchall()
    return pd.DataFrame(
        [dict(r) for r in rows],
        columns=["id", "date", "start_time", "end_time", "title", "category", "memo", "is_done"],
    )


def list_for_date(date: dt.date) -> pd.DataFrame:
    return list_between(date, date)


def add(date: dt.date, start_time: str, end_time: str, title: str, category: str, memo: str = "") -> None:
    conn = get_connection()
    conn.execute(
        "INSERT INTO schedules (date, start_time, end_time, title, category, memo) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (date.isoformat(), start_time, end_time, title, category, memo),
    )
    conn.commit()


def update(schedule_id: int, **fields) -> None:
    if not fields:
        return
    conn = get_connection()
    cols = ", ".join(f"{k} = ?" for k in fields)
    conn.execute(f"UPDATE schedules SET {cols} WHERE id = ?", (*fields.values(), schedule_id))
    conn.commit()


def set_done(schedule_id: int, is_done: bool) -> None:
    update(schedule_id, is_done=int(is_done))


def delete(schedule_id: int) -> None:
    conn = get_connection()
    conn.execute("DELETE FROM schedules WHERE id = ?", (schedule_id,))
    conn.commit()


def sync_range(start: dt.date, end: dt.date, edited_df: pd.DataFrame) -> None:
    """Reconcile a data_editor result for [start, end] back into the DB."""
    conn = get_connection()
    existing_ids = {
        r["id"]
        for r in conn.execute(
            "SELECT id FROM schedules WHERE date BETWEEN ? AND ?",
            (start.isoformat(), end.isoformat()),
        ).fetchall()
    }
    kept_ids = set()

    for _, row in edited_df.iterrows():
        if not str(row.get("title", "")).strip():
            continue
        row_id = row.get("id")
        values = (
            str(row["date"]),
            str(row["start_time"]),
            str(row.get("end_time") or ""),
            str(row["title"]),
            str(row.get("category") or "기타"),
            str(row.get("memo") or ""),
            int(bool(row.get("is_done"))),
        )
        if pd.notna(row_id) and int(row_id) in existing_ids:
            row_id = int(row_id)
            conn.execute(
                "UPDATE schedules SET date=?, start_time=?, end_time=?, title=?, "
                "category=?, memo=?, is_done=? WHERE id=?",
                (*values, row_id),
            )
            kept_ids.add(row_id)
        else:
            cur = conn.execute(
                "INSERT INTO schedules (date, start_time, end_time, title, category, memo, is_done) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                values,
            )
            kept_ids.add(cur.lastrowid)

    for stale_id in existing_ids - kept_ids:
        conn.execute("DELETE FROM schedules WHERE id = ?", (stale_id,))

    conn.commit()
