# 📅 ScheduleManager

공부 일정, 자격증, 할 일, 공부 시간을 한 곳에서 관리하는 개인용 Streamlit 대시보드 앱이에요.

## 기능 (페이지별)

| 페이지 | 내용 |
|---|---|
| **대시보드** | 전체 현황 한눈에 보기 |
| **일정 관리** | 캘린더 형태로 일정 등록/조회 |
| **자격증 관리** | 준비 중인 자격증과 시험 일정 관리 |
| **공부 시간 기록** | 공부한 시간을 기록·누적 |
| **할 일** | 투두리스트 |
| **통계** | 위 기록들을 바탕으로 한 통계/분석 |

## 기술 스택

| 기술 | 역할 |
|---|---|
| **Streamlit** (`st.navigation` / `st.Page`) | 페이지 여러 개를 상단 탭으로 전환하는 멀티페이지 앱 구조 |
| **SQLite** | 일정/자격증/공부기록/할 일을 저장하는 로컬 DB (`utils/db.py`가 연결 및 스키마 초기화 담당) |
| **pandas** | 통계 페이지에서 데이터 집계/가공 |

## 파일 구조

```
ScheduleManager/
├── streamlit_app.py         # 앱 진입점 — 페이지 목록(네비게이션) 정의
├── app_pages/
│   ├── dashboard.py           # 대시보드
│   ├── calendar.py             # 일정 관리
│   ├── certificates.py         # 자격증 관리
│   ├── study.py                # 공부 시간 기록
│   ├── todo.py                  # 할 일
│   └── statistics.py            # 통계
└── utils/
    ├── db.py                     # SQLite 연결 및 스키마 생성
    ├── schedules.py               # 일정 CRUD
    ├── certificates.py            # 자격증 CRUD
    ├── study.py                    # 공부 시간 기록 CRUD
    └── todos.py                     # 할 일 CRUD
```

## 실행하기

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

---

🤖 이 저장소의 README는 Claude Code와 함께 작성했어요.
