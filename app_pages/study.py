import datetime as dt

import pandas as pd
import streamlit as st

from utils import certificates, study

st.title("공부 시간 기록")

selected_date = st.date_input("날짜", value=dt.date.today(), key="study_date")

cert_df = certificates.list_certificates()
cert_options = {"기타": None} | {row["name"]: int(row["id"]) for _, row in cert_df.iterrows()}

col1, col2 = st.columns(2)

# ---- 오늘 공부 목표 ----------------------------------------------------------
with col1:
    with st.container(border=True):
        st.subheader(":material/checklist: 공부 목표")
        targets = study.list_targets_for_date(selected_date)
        if targets.empty:
            st.caption("등록된 공부 목표가 없습니다.")
        else:
            for _, row in targets.iterrows():
                tc1, tc2 = st.columns([0.85, 0.15])
                with tc1:
                    label = f"{row['subject_name']} ({row['target_minutes']}분)"
                    if pd.notna(row["certificate_name"]):
                        label = f"[{row['certificate_name']}] {label}"
                    checked = st.checkbox(label, value=bool(row["is_done"]), key=f"target_{row['id']}")
                    if checked != bool(row["is_done"]):
                        study.set_target_done(int(row["id"]), checked)
                        st.rerun()
                with tc2:
                    if st.button(":material/delete:", key=f"del_target_{row['id']}"):
                        study.delete_target(int(row["id"]))
                        st.rerun()

        with st.form("add_target", clear_on_submit=True):
            st.markdown("**목표 추가**")
            a1, a2, a3 = st.columns([0.4, 0.3, 0.3])
            with a1:
                t_cert = st.selectbox("자격증", list(cert_options.keys()), key="target_cert")
            with a2:
                t_subject = st.text_input("과목", key="target_subject")
            with a3:
                t_minutes = st.number_input("목표(분)", min_value=0, step=10, value=60, key="target_minutes")
            if st.form_submit_button("추가", type="primary"):
                if t_subject.strip():
                    study.add_target(selected_date, t_subject, int(t_minutes), cert_options[t_cert])
                    st.rerun()
                else:
                    st.warning("과목을 입력하세요.")

# ---- 공부 시간 기록 -----------------------------------------------------------
with col2:
    with st.container(border=True):
        st.subheader(":material/timer: 공부 시간 기록")
        total_minutes = study.total_minutes_for_date(selected_date)
        st.metric("총 공부시간", f"{total_minutes // 60}시간 {total_minutes % 60}분")

        logs = study.list_logs_between(selected_date, selected_date)
        if logs.empty:
            st.caption("기록된 공부 시간이 없습니다.")
        else:
            for _, row in logs.iterrows():
                lc1, lc2 = st.columns([0.85, 0.15])
                with lc1:
                    label = f"{row['subject_name']} · {row['duration_minutes']}분"
                    if pd.notna(row["certificate_name"]):
                        label = f"[{row['certificate_name']}] {label}"
                    st.markdown(label)
                with lc2:
                    if st.button(":material/delete:", key=f"del_log_{row['id']}"):
                        study.delete_log(int(row["id"]))
                        st.rerun()

        with st.form("add_log", clear_on_submit=True):
            st.markdown("**기록 추가**")
            b1, b2, b3 = st.columns([0.4, 0.3, 0.3])
            with b1:
                l_cert = st.selectbox("자격증", list(cert_options.keys()), key="log_cert")
            with b2:
                l_subject = st.text_input("과목", key="log_subject")
            with b3:
                l_minutes = st.number_input("시간(분)", min_value=0, step=5, value=30, key="log_minutes")
            l_memo = st.text_input("메모", key="log_memo")
            if st.form_submit_button("추가", type="primary"):
                if l_subject.strip():
                    study.add_log(selected_date, l_subject, int(l_minutes), cert_options[l_cert], l_memo)
                    st.rerun()
                else:
                    st.warning("과목을 입력하세요.")

st.divider()
st.subheader(":material/bar_chart: 공부 시간 그래프")
period = st.segmented_control("기간", ["하루", "일주일", "한달"], default="일주일", key="study_period")

if period == "하루":
    day_logs = study.list_logs_between(selected_date, selected_date)
    if day_logs.empty:
        st.caption("표시할 데이터가 없습니다.")
    else:
        chart_df = day_logs.groupby("subject_name", as_index=False)["duration_minutes"].sum()
        st.bar_chart(chart_df, x="subject_name", y="duration_minutes", x_label="과목", y_label="분")
else:
    days = 7 if period == "일주일" else 30
    start = selected_date - dt.timedelta(days=days - 1)
    range_logs = study.list_logs_between(start, selected_date)
    all_dates = pd.DataFrame({"date": [(start + dt.timedelta(days=i)).isoformat() for i in range(days)]})
    if range_logs.empty:
        daily = all_dates.copy()
        daily["duration_minutes"] = 0
    else:
        agg = range_logs.groupby("date", as_index=False)["duration_minutes"].sum()
        daily = all_dates.merge(agg, on="date", how="left").fillna(0)
    st.bar_chart(daily, x="date", y="duration_minutes", x_label="날짜", y_label="분")
