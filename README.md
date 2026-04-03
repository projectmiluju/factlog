# FactLog

근거 기반 설비 이상 감지 + 의사결정 트래커

## 시작하기 (Getting Started)

### 사전 요구사항
- `Python 3.8+`
- `pip`

### 설치
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
cd web && npm install
```

### 환경변수 설정
- 현재 필수 환경변수는 없습니다.
- `OPENAI_API_KEY`
  설정하면 분석 API가 OpenAI를 사용해 근거 설명을 생성합니다.
  값이 없거나 호출에 실패하면 규칙 기반 한국어 설명으로 자동 폴백합니다.

### 실행
```bash
python scripts/run_validation.py --data-dir data/raw/nasa-cmapss --subset FD001
uvicorn factlog_ml.api:app --reload
cd web && npm run dev
```

## 프로젝트 구조
```text
factlog/
├── docs/
│   ├── prd/
│   ├── decisions/
│   ├── devlog/
│   └── STATUS.md
├── scripts/
├── src/factlog_ml/
│   ├── api.py
│   ├── analysis.py
│   ├── analysis_schemas.py
│   ├── action_schemas.py
│   ├── api_schemas.py
│   ├── dashboard_schemas.py
│   ├── db.py
│   └── uploads.py
├── tests/
├── web/
└── artifacts/validation/
```

## 기술 스택
- `React + TypeScript + Recharts`
  화면 입력, 차트, 대시보드를 위한 프론트엔드 스택
- `FastAPI`
  입력/분석/대시보드 API를 위한 백엔드 스택
- `SQLite`
  MVP 단일 사용자 저장소
- `scikit-learn`
  NASA C-MAPSS 기준선 이상 감지 모델
- `OpenAI API`
  분석 근거 자연어 설명 생성

관련 결정:
- [ADR-001](docs/decisions/ADR-001-nasa-cmapss-binary-baseline.md)

## 스크립트
- `python scripts/run_validation.py --data-dir data/raw/nasa-cmapss --subset FD001`
  NASA C-MAPSS 검증 요약 생성
- `uvicorn factlog_ml.api:app --reload`
  센서 입력, CSV 업로드, 분석 결과, 조치 저장, 대시보드 API 실행
- `pytest -q`
  검증 파이프라인과 백엔드 API 테스트 실행
- `cd web && npm run dev`
  FactLog 웹 UI 개발 서버 실행
- `cd web && npm run test`
  웹 UI 상호작용 테스트 실행
- `cd web && npm run build`
  웹 UI 프로덕션 빌드 검증
