# FactLog 검증 요약

## 핵심 플로우
- 센서값 입력 또는 CSV 업로드
- 이상 점수와 근거 설명 생성
- 유사 사례 3건 조회
- 조치 기록 저장
- 대시보드 최근 이력 반영

## NASA C-MAPSS 벤치마크
- 데이터셋: NASA C-MAPSS FD001
- 모델: LogisticRegression (logistic-regression-balanced-v1)
- 정확도: 0.9727
- 정밀도: 0.4763
- 재현율: 0.7861
- F1: 0.5932
- ROC-AUC: 0.9852

## AI허브 보조 검증 상태
- AIHub 제조 데이터: 미적재 / 아직 AI허브 데이터 적재 전

## 자동 검증 상태
- pytest: 33 passed
- vitest: 3 passed
- vite build: passed
