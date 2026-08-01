import datetime as dt

import streamlit as st

from utils import certificates

st.title("자격증 관리")

with st.expander(":material/add: 자격증 추가"):
    with st.form("add_cert", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("자격증 이름")
        with c2:
            exam_date = st.date_input("시험일", value=dt.date.today() + dt.timedelta(days=30))
        memo = st.text_input("메모", value="")
        if st.form_submit_button("추가", type="primary"):
            if name.strip():
                certificates.add_certificate(name, exam_date, memo)
                st.rerun()
            else:
                st.warning("자격증 이름을 입력하세요.")

certs = certificates.list_certificates()

if certs.empty:
    st.caption("등록된 자격증이 없습니다. 위에서 추가해보세요.")

for _, cert in certs.sort_values("exam_date").iterrows():
    cert_id = int(cert["id"])
    d = certificates.d_day(cert["exam_date"])
    d_label = f"D{'+' if d < 0 else '-'}{abs(d)}" if d != 0 else "D-Day"
    done, total = certificates.progress(cert_id)
    pct = int(done / total * 100) if total else 0

    with st.container(border=True):
        head1, head2 = st.columns([0.7, 0.3])
        with head1:
            st.subheader(cert["name"])
            st.caption(f"시험일 {cert['exam_date']}")
        with head2:
            st.metric("D-Day", d_label)

        st.progress(pct, text=f"진도 {pct}% ({done}/{total} 과목)")

        st.markdown("**남은 과목**")
        subjects = certificates.list_subjects(cert_id)
        if subjects.empty:
            st.caption("등록된 과목이 없습니다.")
        else:
            for _, subj in subjects.iterrows():
                sc1, sc2 = st.columns([0.85, 0.15])
                with sc1:
                    checked = st.checkbox(
                        subj["name"], value=bool(subj["is_done"]), key=f"subj_{subj['id']}"
                    )
                    if checked != bool(subj["is_done"]):
                        certificates.set_subject_done(int(subj["id"]), checked)
                        st.rerun()
                with sc2:
                    if st.button(":material/delete:", key=f"del_subj_{subj['id']}"):
                        certificates.delete_subject(int(subj["id"]))
                        st.rerun()

        new_col1, new_col2 = st.columns([0.8, 0.2])
        with new_col1:
            new_subject = st.text_input("과목 추가", key=f"new_subject_{cert_id}", label_visibility="collapsed", placeholder="과목명 입력 후 추가")
        with new_col2:
            if st.button("추가", key=f"add_subject_{cert_id}"):
                if new_subject.strip():
                    certificates.add_subject(cert_id, new_subject)
                    st.rerun()

        confirm_key = f"confirm_delete_{cert_id}"
        del_col1, del_col2 = st.columns([0.85, 0.15])
        with del_col2:
            if not st.session_state.get(confirm_key):
                if st.button(":material/delete: 자격증 삭제", key=f"del_cert_{cert_id}"):
                    st.session_state[confirm_key] = True
                    st.rerun()
            else:
                if st.button(":material/warning: 정말 삭제할까요?", key=f"del_cert_confirm_{cert_id}", type="primary"):
                    certificates.delete_certificate(cert_id)
                    st.session_state.pop(confirm_key, None)
                    st.rerun()
