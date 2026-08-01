import calendar as cal
import datetime as dt

import pandas as pd
import streamlit as st

from utils import schedules

st.title("일정 관리")

WEEKDAY_KO = ["월", "화", "수", "목", "금", "토", "일"]

if "cal_anchor" not in st.session_state:
    st.session_state.cal_anchor = dt.date.today()

tab_week, tab_month = st.tabs([":material/view_week: 주간 캘린더", ":material/calendar_view_month: 월간 캘린더"])

# ============================================================================
# 주간 캘린더
# ============================================================================
with tab_week:
    nav1, nav2, nav3 = st.columns([0.15, 0.7, 0.15])
    with nav1:
        if st.button(":material/chevron_left: 이전 주", key="week_prev"):
            st.session_state.cal_anchor -= dt.timedelta(days=7)
    with nav3:
        if st.button("다음 주 :material/chevron_right:", key="week_next"):
            st.session_state.cal_anchor += dt.timedelta(days=7)

    anchor = st.session_state.cal_anchor
    week_start = anchor - dt.timedelta(days=anchor.weekday())
    week_end = week_start + dt.timedelta(days=6)
    with nav2:
        st.markdown(f"**{week_start} ~ {week_end}**", text_alignment="center")

    week_df = schedules.list_between(week_start, week_end)
    today = dt.date.today()

    day_cols = st.columns(7)
    for i, col in enumerate(day_cols):
        day = week_start + dt.timedelta(days=i)
        with col:
            with st.container(border=True, height=260):
                header = f"**{WEEKDAY_KO[i]}** {day.day}"
                if day == today:
                    st.markdown(f":primary-background[{header}]")
                else:
                    st.markdown(header)
                day_rows = week_df[week_df["date"] == day.isoformat()]
                if day_rows.empty:
                    st.caption("-")
                else:
                    for _, row in day_rows.iterrows():
                        st.markdown(f"`{row['start_time']}` {row['title']}")

    st.divider()
    with st.expander(":material/add: 일정 추가", expanded=False):
        with st.form("add_schedule_week", clear_on_submit=True):
            f1, f2, f3 = st.columns(3)
            with f1:
                new_date = st.date_input("날짜", value=week_start, key="week_new_date")
            with f2:
                new_start = st.time_input("시작 시간", value=dt.time(9, 0), key="week_new_start")
            with f3:
                new_end = st.time_input("종료 시간", value=dt.time(10, 0), key="week_new_end")
            f4, f5 = st.columns([0.6, 0.4])
            with f4:
                new_title = st.text_input("제목", key="week_new_title")
            with f5:
                new_category = st.selectbox("분류", schedules.CATEGORIES, key="week_new_category")
            new_memo = st.text_input("메모", key="week_new_memo")
            if st.form_submit_button("추가", type="primary"):
                if new_title.strip():
                    schedules.add(new_date, new_start.strftime("%H:%M"), new_end.strftime("%H:%M"), new_title, new_category, new_memo)
                    st.rerun()
                else:
                    st.warning("제목을 입력하세요.")

    st.subheader("이번 주 일정 수정 / 삭제")
    st.caption("셀을 더블클릭해 수정하고, 행 왼쪽 체크 후 삭제 아이콘으로 삭제할 수 있습니다.")
    edited = st.data_editor(
        week_df,
        key="week_editor",
        num_rows="dynamic",
        column_config={
            "id": None,
            "date": st.column_config.DateColumn("날짜"),
            "start_time": st.column_config.TextColumn("시작"),
            "end_time": st.column_config.TextColumn("종료"),
            "title": st.column_config.TextColumn("제목"),
            "category": st.column_config.SelectboxColumn("분류", options=schedules.CATEGORIES),
            "memo": st.column_config.TextColumn("메모"),
            "is_done": st.column_config.CheckboxColumn("완료"),
        },
        hide_index=True,
    )
    if st.button("변경사항 저장", key="week_save"):
        save_df = edited.copy()
        save_df["date"] = save_df["date"].apply(lambda d: d if isinstance(d, str) else pd.Timestamp(d).date().isoformat())
        schedules.sync_range(week_start, week_end, save_df)
        st.success("저장되었습니다.")
        st.rerun()

# ============================================================================
# 월간 캘린더
# ============================================================================
with tab_month:
    m1, m2, m3 = st.columns([0.15, 0.7, 0.15])
    with m1:
        if st.button(":material/chevron_left: 이전 달", key="month_prev"):
            first = st.session_state.cal_anchor.replace(day=1)
            st.session_state.cal_anchor = (first - dt.timedelta(days=1)).replace(day=1)
    with m3:
        if st.button("다음 달 :material/chevron_right:", key="month_next"):
            first = st.session_state.cal_anchor.replace(day=1)
            next_month = first.replace(day=28) + dt.timedelta(days=4)
            st.session_state.cal_anchor = next_month.replace(day=1)

    m_anchor = st.session_state.cal_anchor
    with m2:
        st.markdown(f"**{m_anchor.year}년 {m_anchor.month}월**", text_alignment="center")

    month_weeks = cal.Calendar(firstweekday=0).monthdatescalendar(m_anchor.year, m_anchor.month)
    month_start = month_weeks[0][0]
    month_end = month_weeks[-1][-1]
    month_df = schedules.list_between(month_start, month_end)

    header_cols = st.columns(7)
    for i, hc in enumerate(header_cols):
        hc.markdown(f"**{WEEKDAY_KO[i]}**")

    for week in month_weeks:
        row_cols = st.columns(7)
        for i, day in enumerate(week):
            with row_cols[i]:
                in_month = day.month == m_anchor.month
                with st.container(border=True, height=120):
                    day_label = str(day.day)
                    if day == dt.date.today():
                        st.markdown(f":primary-background[**{day_label}**]")
                    elif not in_month:
                        st.caption(day_label)
                    else:
                        st.markdown(f"**{day_label}**")
                    if in_month:
                        day_rows = month_df[month_df["date"] == day.isoformat()]
                        for _, row in day_rows.head(3).iterrows():
                            st.caption(f"{row['title']}")
                        if len(day_rows) > 3:
                            st.caption(f"+{len(day_rows) - 3}개 더")

    st.divider()
    st.subheader("이번 달 일정 목록")
    st.dataframe(
        month_df,
        column_config={
            "id": None,
            "date": st.column_config.DateColumn("날짜"),
            "start_time": st.column_config.TextColumn("시작"),
            "end_time": st.column_config.TextColumn("종료"),
            "title": st.column_config.TextColumn("제목"),
            "category": st.column_config.TextColumn("분류"),
            "memo": st.column_config.TextColumn("메모"),
            "is_done": st.column_config.CheckboxColumn("완료"),
        },
        hide_index=True,
    )
