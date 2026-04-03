# FactLog 검증 전략

## 1. NASA C-MAPSS 메인 검증 기준
- 메인 데이터셋: `NASA C-MAPSS FD001`
- 입력 단위: 엔진 유닛의 cycle별 시계열 row
- MVP 타깃 정의: `RUL <= 30 cycle` 이면 이상 상태(`1`), 아니면 정상(`0`)
- 이유:
  - 고장 직전 상태를 이진 분류로 바꾸면 MVP의 "이상 감지" 플로우와 바로 연결된다.
  - 발표 시 정확도, 정밀도, 재현율, F1, ROC-AUC를 직관적으로 설명할 수 있다.

## 2. 피처 선택
- 운영 조건: `op_setting_1~3`
- 센서: `sensor_2`, `sensor_3`, `sensor_4`, `sensor_7`, `sensor_8`, `sensor_11`, `sensor_12`, `sensor_13`, `sensor_15`, `sensor_17`, `sensor_20`, `sensor_21`
- 보조 피처: `time_in_cycles`

선정 근거:
- NASA C-MAPSS 실무/논문 예제에서 변동성이 낮은 센서는 자주 제외된다.
- MVP는 복잡한 feature engineering보다 재현 가능한 기준선이 중요하다.

## 3. 모델 기준선
- 모델: `LogisticRegression(class_weight="balanced")`
- 전처리: `SimpleImputer(median)` + `StandardScaler`

선정 이유:
- 2~3일 MVP에서 가장 중요한 것은 설명 가능하고 빠르게 재현 가능한 기준선이다.
- 복잡한 시계열 딥러닝은 구현 비용이 높고, 채용 과제에서는 오히려 검증 흐름이 흐려진다.

## 4. 산출 지표
- `accuracy`
- `precision`
- `recall`
- `f1`
- `roc_auc`
- `predicted_positive_ratio`

## 5. AI허브 데이터 역할
- 이번 MVP에서는 제품 메인 플로우에 완전 통합하지 않는다.
- 로컬 적재 이후 아래 두 가지 용도로만 사용한다.
  - NASA 기준선이 한국 제조 데이터에서도 크게 무너지지 않는지 보조 검증
  - 발표에서 "글로벌 벤치마크 + 국내 제조 데이터" 메시지 보강

## 6. 실행 방법
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
python scripts/run_validation.py --data-dir data/raw/nasa-cmapss --subset FD001
```

## 7. 예상 산출물
- 생성 파일: `artifacts/validation/nasa_fd001_summary.json`
- 후속 사용처:
  - 백엔드 `GET /api/validation/summary`
  - 대시보드 검증 카드
  - 발표 자료 검증 결과 슬라이드
