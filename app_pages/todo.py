import datetime as dt

import streamlit as st

from utils import todos

st.title("할 일")

selected_date = st.date_input("날짜", value=dt.date.today(), key="todo_date")

with st.form("add_todo", clear_on_submit=True):
    c1, c2, c3 = st.columns([0.55, 0.25, 0.2])
    with c1:
        content = st.text_input("할 일", key="todo_content")
    with c2:
        priority = st.selectbox("우선순위", todos.PRIORITIES, index=1, key="todo_priority")
    with c3:
        st.write("")
        submitted = st.form_submit_button("추가", type="primary")
    if submitted:
        if content.strip():
            todos.add(selected_date, content, priority)
            st.rerun()
        else:
            st.warning("할 일 내용을 입력하세요.")

day_todos = todos.list_for_date(selected_date)

if day_todos.empty:
    st.caption("등록된 할 일이 없습니다.")
else:
    rate = todos.completion_rate(selected_date)
    st.progress(int(rate * 100), text=f"완료율 {int(rate * 100)}%")

    for _, row in day_todos.iterrows():
        c1, c2, c3 = st.columns([0.7, 0.15, 0.15])
        with c1:
            label = f"{todos.PRIORITY_ICON.get(row['priority'], '')} {row['content']}"
            checked = st.checkbox(label, value=bool(row["is_done"]), key=f"todo_{row['id']}")
            if checked != bool(row["is_done"]):
                todos.set_done(int(row["id"]), checked)
                st.rerun()
        with c2:
            st.caption(row["priority"])
        with c3:
            if st.button(":material/delete:", key=f"del_todo_{row['id']}"):
                todos.delete(int(row["id"]))
                st.rerun()
