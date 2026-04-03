# 프로젝트 현황

**최종 업데이트:** 2026-04-04
**현재 버전:** v0.1.0
**배포 URL:** 없음

## 최근 변경
- NASA C-MAPSS `FD001` 기준 검증 파이프라인 추가
- 검증 실행 CLI와 요약 JSON 산출물 구조 추가
- FastAPI 기반 센서 수기 입력 / CSV 업로드 API 추가
- SQLite 저장 모델 및 Soft Delete 정책 구현
- `POST /api/analysis`, `GET /api/analysis/{id}`, `GET /api/similar-cases/{id}` 추가
- OpenAI 설명 생성과 규칙 기반 폴백 구조 추가
- QA 반려 후 `explanation_source`, `similarity_score` 저장/조회 정합성 복구
- 분석 API 회귀 테스트와 404 경계 테스트를 포함한 pytest 30개 통과
- `web/` 기반 React + TypeScript + Recharts UI MVP 추가
- `POST /api/actions`, `GET /api/dashboard/summary`, `GET /api/validation/summary` 추가
- Vitest + Testing Library 기반 UI 상태 테스트 3개 추가
- QA 반려 후 `ResizeObserver` mock을 넣어 프론트 테스트 환경 복구
- Playwright 기반 브라우저 E2E 1개 추가
- `FACTLOG_DB_PATH` 기반 E2E 전용 SQLite 경로 분리
- 발표용 검증 요약 산출물 `artifacts/validation/factlog_validation_summary.{json,md}` 생성
- 현재 자동 검증: `pytest 33개`, `vitest 3개`, `playwright 1개`, `vite build` 통과

## 알려진 이슈
| 이슈 | 심각도 | 상태 |
|------|-------|------|
| AI허브 데이터는 아직 로컬 적재 전이라 보조 검증만 계획 상태 | 중간 | Open |
| `OPENAI_API_KEY`용 `.env.example` 파일은 아직 없음 | 낮음 | Planned |
| OpenAI 설명 생성 실패 사유를 구조화 로그로 남기지 않는다 | 낮음 | Open |
| 프론트 번들 크기가 `538.63 kB`로 경고 임계값을 넘는다 | 낮음 | Open |

## 기술 부채
| 항목 | 등록일 | 예상 작업량 |
|------|-------|-----------|
| NASA 외 데이터셋 검증 자동화 미구현 | 2026-04-03 | M |
| 업로드 스키마와 분석 요청 스키마 통합 미완료 | 2026-04-03 | S |
| SQLite 마이그레이션이 수동 `ALTER TABLE` 수준이라 버전 관리 체계가 없음 | 2026-04-04 | S |
| 프론트 번들 code splitting 미적용 | 2026-04-04 | S |

## 다음 계획
- [ ] AIHub 보조 검증 데이터 적재 및 비교 수치 추가
- [ ] `.env.example` 및 실행 옵션 예시 정리
