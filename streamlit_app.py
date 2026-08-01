import streamlit as st

from utils.db import get_connection

st.set_page_config(page_title="ScheduleManager", page_icon=":material/event_note:", layout="wide")

get_connection()  # ensure DB/schema exists before any page runs

page = st.navigation(
    [
        st.Page("app_pages/dashboard.py", title="대시보드", icon=":material/dashboard:", default=True),
        st.Page("app_pages/calendar.py", title="일정 관리", icon=":material/calendar_month:"),
        st.Page("app_pages/certificates.py", title="자격증 관리", icon=":material/workspace_premium:"),
        st.Page("app_pages/study.py", title="공부 시간 기록", icon=":material/menu_book:"),
        st.Page("app_pages/todo.py", title="할 일", icon=":material/checklist:"),
        st.Page("app_pages/statistics.py", title="통계", icon=":material/monitoring:"),
    ],
    position="top",
)

page.run()
