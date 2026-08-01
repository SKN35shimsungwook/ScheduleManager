"""CRUD helpers for the todos table."""

import datetime as dt

import pandas as pd

from utils.db import get_connection

PRIORITIES = ["중요", "보통", "낮음"]
PRIORITY_ICON = {"중요": "🔴", "보통": "🟡", "낮음": "🟢"}


def list_for_date(date: dt.date) -> pd.DataFrame:
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, date, content, priority, is_done FROM todos WHERE date = ? "
        "ORDER BY is_done, CASE priority WHEN '중요' THEN 0 WHEN '보통' THEN 1 ELSE 2 END, id",
        (date.isoformat(),),
    ).fetchall()
    return pd.DataFrame([dict(r) for r in rows], columns=["id", "date", "content", "priority", "is_done"])


def add(date: dt.date, content: str, priority: str = "보통") -> None:
    conn = get_connection()
    conn.execute(
        "INSERT INTO todos (date, content, priority) VALUES (?, ?, ?)",
        (date.isoformat(), content, priority),
    )
    conn.commit()


def set_done(todo_id: int, is_done: bool) -> None:
    conn = get_connection()
    conn.execute("UPDATE todos SET is_done = ? WHERE id = ?", (int(is_done), todo_id))
    conn.commit()


def update(todo_id: int, **fields) -> None:
    if not fields:
        return
    conn = get_connection()
    cols = ", ".join(f"{k} = ?" for k in fields)
    conn.execute(f"UPDATE todos SET {cols} WHERE id = ?", (*fields.values(), todo_id))
    conn.commit()


def delete(todo_id: int) -> None:
    conn = get_connection()
    conn.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
    conn.commit()


def completion_rate(date: dt.date) -> float:
    df = list_for_date(date)
    if df.empty:
        return 0.0
    return float(df["is_done"].mean())
