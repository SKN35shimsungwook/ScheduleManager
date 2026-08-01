import calendar as cal
import datetime as dt

import pandas as pd
import streamlit as st

from utils.db import get_connection
from utils import study

st.title("통계")

today = dt.date.today()
month_anchor = st.date_input("조회 월", value=today, key="stats_month").replace(day=1)
month_days = cal.monthrange(month_anchor.year, month_anchor.month)[1]
month_start = month_anchor
month_end = month_anchor.replace(day=month_days)

conn = get_connection()

schedule_rows = conn.execute(
    "SELECT is_done FROM schedules WHERE date BETWEEN ? AND ?",
    (month_start.isoformat(), month_end.isoformat()),
).fetchall()
todo_rows = conn.execute(
    "SELECT is_done FROM todos WHERE date BETWEEN ? AND ?",
    (month_start.isoformat(), month_end.isoformat()),
).fetchall()

sched_total = len(schedule_rows)
sched_done = sum(r["is_done"] for r in schedule_rows)
todo_total = len(todo_rows)
todo_done = sum(r["is_done"] for r in todo_rows)

combined_total = sched_total + todo_total
combined_done = sched_done + todo_done
achievement_rate = int(combined_done / combined_total * 100) if combined_total else 0

logs = study.list_logs_between(month_start, month_end)
total_study_minutes = int(logs["duration_minutes"].sum()) if not logs.empty else 0

streak = study.streak_days(min(today, month_end))

st.subheader(f"{month_anchor.year}년 {month_anchor.month}월")

with st.container(horizontal=True):
    st.metric(
        "공부시간",
        f"{total_study_minutes // 60}시간 {total_study_minutes % 60}분",
        border=True,
    )
    st.metric("완료한 일정", f"{sched_done}개 / {sched_total}개", border=True)
    st.metric("달성률", f"{achievement_rate}%", border=True)
    st.metric("연속 공부", f"{streak}일", border=True)

st.divider()

col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.markdown("**일별 공부 시간**")
        all_dates = pd.DataFrame({"date": [(month_start + dt.timedelta(days=i)).isoformat() for i in range(month_days)]})
        if logs.empty:
            daily = all_dates.copy()
            daily["duration_minutes"] = 0
        else:
            agg = logs.groupby("date", as_index=False)["duration_minutes"].sum()
            daily = all_dates.merge(agg, on="date", how="left").fillna(0)
        st.bar_chart(daily, x="date", y="duration_minutes", x_label="날짜", y_label="분")

with col2:
    with st.container(border=True):
        st.markdown("**과목별 공부 시간**")
        if logs.empty:
            st.caption("표시할 데이터가 없습니다.")
        else:
            subj_agg = logs.groupby("subject_name", as_index=False)["duration_minutes"].sum()
            st.bar_chart(subj_agg, x="subject_name", y="duration_minutes", x_label="과목", y_label="분")

with st.container(border=True):
    st.markdown("**할 일 완료 현황**")
    st.progress(
        int(todo_done / todo_total * 100) if todo_total else 0,
        text=f"할 일 {todo_done}개 / {todo_total}개 완료",
    )
