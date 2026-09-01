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

## DB 스키마

`utils/db.py`의 `SCHEMA`가 앱 실행 시 없으면 자동으로 만드는 4개 테이블이에요.
`cert_subjects`(자격증별 과목)와 `study_targets`(공부 목표)는 `certificates.id`를
외래키로 참조해서, 자격증을 지우면 관련 과목도 같이 지워지도록(`ON DELETE CASCADE`)
연결돼 있어요.

| 테이블 | 용도 |
|---|---|
| `schedules` | 날짜별 일정 (제목, 카테고리, 완료 여부) |
| `certificates` | 준비 중인 자격증 (이름, 시험일) |
| `cert_subjects` | 자격증에 딸린 과목별 완료 체크 |
| `study_targets` | 날짜별 공부 목표 (자격증/과목과 연결) |

## 트러블슈팅

아직 커밋이 초기 버전 하나뿐이라, 이 저장소에서 실제로 겪은 버그 수정 이력은 없어요.
(다른 저장소들은 배포 후 발견한 문제를 고친 기록이 있어서 그걸 troubleshooting 섹션에
정리했는데, 여기는 아직 그런 이력이 쌓이기 전이에요.)

---

🤖 이 저장소의 README는 Claude Code와 함께 작성했어요.
