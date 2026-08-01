import datetime as dt

import streamlit as st

from utils import certificates, schedules, study, todos

today = dt.date.today()

st.title("대시보드")
st.caption(f":material/calendar_today: {today.strftime('%Y-%m-%d (%a)')}")

col1, col2 = st.columns(2)

# ---- 오늘 일정 -------------------------------------------------------------
with col1:
    with st.container(border=True):
        st.subheader(":material/event: 오늘 일정")
        day_schedules = schedules.list_for_date(today)
        if day_schedules.empty:
            st.caption("오늘 등록된 일정이 없습니다.")
        else:
            for _, row in day_schedules.iterrows():
                c1, c2 = st.columns([0.1, 0.9])
                with c1:
                    checked = st.checkbox(
                        "완료", value=bool(row["is_done"]), key=f"dash_sched_{row['id']}",
                        label_visibility="collapsed",
                    )
                    if checked != bool(row["is_done"]):
                        schedules.set_done(int(row["id"]), checked)
                        st.rerun()
                with c2:
                    time_label = row["start_time"] + (f" ~ {row['end_time']}" if row["end_time"] else "")
                    text = f"**{time_label}** · {row['title']} `{row['category']}`"
                    st.markdown(f"~~{text}~~" if row["is_done"] else text)

# ---- 오늘 공부 --------------------------------------------------------------
with col2:
    with st.container(border=True):
        st.subheader(":material/menu_book: 오늘 공부")
        targets = study.list_targets_for_date(today)
        if targets.empty:
            st.caption("오늘 등록된 공부 목표가 없습니다. '공부 시간 기록' 페이지에서 추가하세요.")
        else:
            for cert_name, group in targets.groupby(targets["certificate_name"].fillna("기타")):
                st.markdown(f"**{cert_name}**")
                for _, row in group.iterrows():
                    checked = st.checkbox(
                        f"{row['subject_name']} {row['target_minutes']}분",
                        value=bool(row["is_done"]),
                        key=f"dash_target_{row['id']}",
                    )
                    if checked != bool(row["is_done"]):
                        study.set_target_done(int(row["id"]), checked)
                        st.rerun()

col3, col4 = st.columns(2)

# ---- D-Day ------------------------------------------------------------------
with col3:
    with st.container(border=True):
        st.subheader(":material/flag: D-Day")
        certs = certificates.list_certificates()
        if certs.empty:
            st.caption("등록된 자격증이 없습니다. '자격증 관리' 페이지에서 추가하세요.")
        else:
            for _, row in certs.sort_values("exam_date").iterrows():
                d = certificates.d_day(row["exam_date"])
                label = f"D{'+' if d < 0 else '-'}{abs(d)}" if d != 0 else "D-Day"
                st.markdown(f"**{row['name']}** &nbsp;&nbsp; `{label}`  \n{row['exam_date']}")

# ---- 오늘 해야 할 일 ----------------------------------------------------------
with col4:
    with st.container(border=True):
        st.subheader(":material/checklist: 오늘 해야 할 일")
        day_todos = todos.list_for_date(today)
        if day_todos.empty:
            st.caption("오늘 등록된 할 일이 없습니다.")
        else:
            for _, row in day_todos.iterrows():
                checked = st.checkbox(
                    f"{todos.PRIORITY_ICON.get(row['priority'], '')} {row['content']}",
                    value=bool(row["is_done"]),
                    key=f"dash_todo_{row['id']}",
                )
                if checked != bool(row["is_done"]):
                    todos.set_done(int(row["id"]), checked)
                    st.rerun()
