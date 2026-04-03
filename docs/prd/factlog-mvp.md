# [PRD] FactLog MVP

**Status:** Approved
**Date:** 2026-04-03
**Branch:** main

## 1. 개요 (Overview)
- **배경 및 목적:** 제조 현장의 설비 이상 판단은 숙련자 경험, 엑셀, 종이 일지, 메신저 대화에 분산되어 있어 근거 추적이 어렵고, 담당자 변경 시 노하우가 유실된다. FactLog는 센서 데이터 기반 이상 감지, 근거 설명, 유사 사례 검색, 조치 기록 축적을 하나의 흐름으로 묶어 "설명 가능한 판단"과 "재사용 가능한 현장 지식"을 만드는 것을 목표로 한다.
- **타겟 워크플로우:** 설비 관리 담당자가 센서 데이터를 입력하거나 업로드하면, 시스템이 이상 여부와 근거를 제시하고, 과거 유사 사례와 조치 결과를 보여주며, 사용자는 실제 조치를 기록한다. 그 기록은 다음 판단의 참고 근거로 축적된다.

## 2. 핵심 요구사항 (Core Requirements)
- [x] 사용자는 설비를 선택하고 센서 데이터를 수기 입력하거나 CSV로 업로드할 수 있어야 한다.
- [x] 시스템은 NASA C-MAPSS 기반 이상 감지 모델로 이상 점수와 이상 여부를 계산해야 한다.
- [x] 시스템은 OpenAI API를 사용해 이상 판단 근거를 현장 언어로 자연어 설명해야 한다.
- [x] 시스템은 저장된 과거 분석 이력 중 유사 사례 3건을 검색해 보여줘야 한다.
- [x] 사용자는 분석 결과에 대해 실제 조치 내용, 담당자, 결과 메모를 기록할 수 있어야 한다.
- [x] 대시보드는 설비별 최근 이상 이력, 조치 현황, 기본 정확도 요약을 표시해야 한다.
- [ ] AI허브 제조 데이터는 제품 메인 플로우가 아니라 보조 검증 데이터셋으로 사용해야 한다.
- [x] 첫 사용 시 빈 상태에서는 온보딩 안내와 샘플 분석 1건을 제공해야 한다.

## 2-1. 구현 현황 (Implementation Status)
- **완료:** `#1` NASA C-MAPSS 검증 파이프라인, `#2` 입력/CSV 업로드 API, `#3` 분석/근거/유사 사례 API, `#4` 웹 UI MVP, `#5` E2E 및 검증 요약 산출물
- **자동 검증:** `pytest 33 passed`, `vitest 3 passed`, `playwright 1 passed`, `vite build passed`
- **정량 검증:** NASA C-MAPSS FD001 기준 `accuracy 0.9727`, `precision 0.4763`, `recall 0.7861`, `f1 0.5932`, `roc_auc 0.9852`
- **미완료:** AI허브 데이터 실제 적재 및 비교 검증, `.env.example`, OpenAI 실패 로그 구조화, 프론트 번들 최적화

## 3. 데이터 및 상태 정의 (Data & State Models)
- **상태 전이도:**
  `Idle → Input Ready → Uploading / Analyzing → Analysis Success / Analysis Error → Action Saving → Saved / Save Error`

- **핵심 데이터 필드:**
  - `equipment`
    - `id`
    - `name`
    - `type`
    - `source_dataset` (`nasa_cmapss` / `aihub`)
  - `sensor_record`
    - `id`
    - `equipment_id`
    - `timestamp`
    - `temperature`
    - `vibration`
    - `rpm`
    - `torque`
    - `tool_wear`
    - `raw_payload`
  - `analysis_result`
    - `id`
    - `sensor_record_id`
    - `anomaly_score`
    - `is_anomaly`
    - `model_version`
    - `explanation_text`
    - `explanation_source`
    - `similar_cases_payload`
    - `created_at`
    - `deleted_at`
  - `action_log`
    - `id`
    - `analysis_result_id`
    - `action_taken`
    - `operator_name`
    - `result_note`
    - `created_at`
    - `deleted_at`
  - `validation_summary`
    - `id`
    - `dataset_name`
    - `metric_name`
    - `metric_value`
    - `evaluated_at`

- **API 엔드포인트 (예상):**
  - `GET /health` : 헬스 체크
  - `POST /api/sensor-records` : 수기 센서 입력 저장
  - `POST /api/uploads/csv` : CSV 업로드 및 검증
  - `POST /api/analysis` : 센서 데이터 분석 실행
  - `GET /api/analysis/{id}` : 분석 결과 상세 조회
  - `GET /api/analysis` : 분석 이력 목록 조회
  - `GET /api/similar-cases/{analysis_id}` : 유사 사례 3건 조회
  - `POST /api/actions` : 조치 기록 저장
  - `GET /api/dashboard/summary` : 대시보드 요약 조회
  - `GET /api/validation/summary` : NASA / AI허브 검증 결과 조회

## 4. 예외 처리 정책 (Exception Handling)

| 상황 | 대응 방안 | 우선순위 |
|------|---------|---------|
| 첫 진입 시 데이터 0건 | 빈 표 대신 온보딩 안내와 샘플 분석 1건 제공 | 높음 |
| CSV 형식 오류 | 클라이언트에서 확장자/크기 1차 검증, 서버에서 컬럼/타입/필수값 재검증 후 행 번호 포함 오류 반환 | 높음 |
| 필수 컬럼 누락 | 업로드 전체 거절, 누락 컬럼명 명시 | 높음 |
| 숫자 파싱 실패 | 문제 행과 컬럼명을 명시해 업로드 거절 | 높음 |
| 분석 API 실패 | 오류 메시지와 `다시 시도` 버튼 제공, 자동 재시도 없음 | 높음 |
| OpenAI 설명 생성 실패 | 이상 점수/규칙 기반 요약 문구로 폴백, 화면에는 "설명 생성 일부 실패" 표시 | 높음 |
| 버튼 중복 클릭 | 프론트엔드 버튼 비활성화 + 서버 측 중복 요청 방지 | 높음 |
| 유사 사례 없음 | "아직 축적된 유사 사례가 없습니다" 메시지와 첫 기록 유도 CTA 제공 | 중간 |
| 이력 데이터 증가 | 대시보드 최근 20건만 노출, 전체 목록은 `page + page_size` 페이지네이션 적용 | 중간 |
| 기록 삭제 요청 | Hard Delete 금지, `deleted_at` 기반 Soft Delete 적용 | 중간 |

## 4-1. 남은 공백 (Known Gaps vs Spec)
| 항목 | 현재 상태 | 후속 방향 |
|------|---------|---------|
| AI허브 보조 검증 | 검증 요약에 `미적재` 상태만 표시 | AI허브 샘플 적재 후 NASA와 비교 지표 추가 |
| `.env.example` | 없음 | OpenAI 키와 실행 옵션 예시 파일 추가 |
| OpenAI 실패 로그 | 화면 폴백은 있으나 구조화 로그 없음 | 운영용 로그 스키마 추가 |
| 프론트 번들 최적화 | `538.63 kB` 경고 | code splitting 또는 차트 분리 로딩 검토 |

## 5. 기술 스택 (Technology Stack)
- **선택한 접근법:** 접근법 A, 최소 생존 버전
- **핵심 기술:**
  - `React + TypeScript + Recharts`
    - 입력 폼, 테이블, 차트, 대시보드 구현에 적합
  - `FastAPI`
    - CSV 업로드, 모델 추론, 검증 API를 빠르게 구성 가능
  - `SQLite`
    - 단일 사용자 데모, 분석 이력, 조치 기록 저장에 충분
  - `scikit-learn`
    - 이상 감지 모델 학습 및 정량 평가에 적합
  - `OpenAI API`
    - 모델 판단 근거를 현장 언어로 자연어 설명
  - `NASA C-MAPSS`
    - 메인 분석/시연용 공신력 있는 벤치마크 데이터
  - `AI허브 제조 데이터`
    - 한국 제조 현장 적합성 보조 검증 데이터

## 6. 아웃 오브 스코프 (Out of Scope)

| 제외 기능 | 제외 이유 | 예상 도입 시기 |
|----------|----------|-------------|
| 실시간 센서 스트리밍 수집 | 2~3일 MVP 범위 초과 | v2 |
| 멀티 사용자 / 권한 관리 | 채용 과제 데모에 비핵심 | v2 |
| AI허브 데이터 완전 통합 UI | 전처리 및 스키마 통합 비용 과다 | v2 |
| 모델 자동 재학습 파이프라인 | MVP 검증 핵심과 무관 | v2 |
| Slack/문자 알림 | 데모 완결성과 직접 관련 없음 | v2 |
| 모바일 최적화 | 데스크톱 시연 우선 | v2 |
| 고급 검색 / 복합 필터 | 초기 데이터 규모에서 불필요 | v2 |
| 다국어 설명 지원 | 한국어 발표 과제 범위 밖 | v2 |

## 7. 다음 액션 플랜 (Next Actions)
- AI허브 제조 데이터 적재 후 보조 검증 지표 추가
- `.env.example` 및 로컬 실행 가이드 보강
- OpenAI 실패 로그 구조화 및 운영 추적성 보강
- 프론트 번들 최적화 여부 판단
- 발표 자료에 NASA 검증 수치와 E2E 완료 상태 반영

## ⚠️ 가정 (Assumptions)
- 현재 사용자는 `인증 없는 단일 사용자 데모 모드`로 사용한다.
- 현장 워크플로우는 `센서 확인 → 숙련자 경험 판단 → 공유 → 조치 → 기록`의 일반 제조 흐름을 따른다.
- MVP의 주 시연 데이터는 NASA C-MAPSS이며, AI허브는 제품 메인 플로우가 아니라 보조 검증 용도다.
