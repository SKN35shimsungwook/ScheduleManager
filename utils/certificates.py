"""CRUD helpers for certificates and their subjects."""

import datetime as dt

import pandas as pd

from utils.db import get_connection


def list_certificates() -> pd.DataFrame:
    conn = get_connection()
    rows = conn.execute("SELECT id, name, exam_date, memo FROM certificates ORDER BY exam_date").fetchall()
    return pd.DataFrame([dict(r) for r in rows], columns=["id", "name", "exam_date", "memo"])


def get_certificate(certificate_id: int) -> dict | None:
    conn = get_connection()
    row = conn.execute("SELECT id, name, exam_date, memo FROM certificates WHERE id = ?", (certificate_id,)).fetchone()
    return dict(row) if row else None


def add_certificate(name: str, exam_date: dt.date, memo: str = "") -> int:
    conn = get_connection()
    cur = conn.execute(
        "INSERT INTO certificates (name, exam_date, memo) VALUES (?, ?, ?)",
        (name, exam_date.isoformat(), memo),
    )
    conn.commit()
    return cur.lastrowid


def update_certificate(certificate_id: int, **fields) -> None:
    if not fields:
        return
    conn = get_connection()
    cols = ", ".join(f"{k} = ?" for k in fields)
    conn.execute(f"UPDATE certificates SET {cols} WHERE id = ?", (*fields.values(), certificate_id))
    conn.commit()


def delete_certificate(certificate_id: int) -> None:
    conn = get_connection()
    conn.execute("DELETE FROM cert_subjects WHERE certificate_id = ?", (certificate_id,))
    conn.execute("DELETE FROM certificates WHERE id = ?", (certificate_id,))
    conn.commit()


def list_subjects(certificate_id: int) -> pd.DataFrame:
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, certificate_id, name, is_done FROM cert_subjects WHERE certificate_id = ? ORDER BY id",
        (certificate_id,),
    ).fetchall()
    return pd.DataFrame([dict(r) for r in rows], columns=["id", "certificate_id", "name", "is_done"])


def add_subject(certificate_id: int, name: str) -> None:
    conn = get_connection()
    conn.execute(
        "INSERT INTO cert_subjects (certificate_id, name) VALUES (?, ?)",
        (certificate_id, name),
    )
    conn.commit()


def set_subject_done(subject_id: int, is_done: bool) -> None:
    conn = get_connection()
    conn.execute("UPDATE cert_subjects SET is_done = ? WHERE id = ?", (int(is_done), subject_id))
    conn.commit()


def delete_subject(subject_id: int) -> None:
    conn = get_connection()
    conn.execute("DELETE FROM cert_subjects WHERE id = ?", (subject_id,))
    conn.commit()


def progress(certificate_id: int) -> tuple[int, int]:
    """Return (done_count, total_count) for a certificate's subjects."""
    df = list_subjects(certificate_id)
    if df.empty:
        return 0, 0
    return int(df["is_done"].sum()), len(df)


def d_day(exam_date: str) -> int:
    target = dt.date.fromisoformat(exam_date)
    return (target - dt.date.today()).days
