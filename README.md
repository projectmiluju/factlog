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
```

### 환경변수 설정
- 현재 `#1` 범위에서는 필수 환경변수가 없습니다.
- 이후 OpenAI 연동 단계에서 `.env.example`이 추가될 예정입니다.

### 실행
```bash
python scripts/run_validation.py --data-dir data/raw/nasa-cmapss --subset FD001
uvicorn factlog_ml.api:app --reload
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
│   ├── api_schemas.py
│   ├── db.py
│   └── uploads.py
├── tests/
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
  센서 수기 입력 및 CSV 업로드 API 실행
- `pytest -q`
  검증 파이프라인 및 입력 API 테스트 실행
