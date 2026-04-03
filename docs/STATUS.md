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
- `#1` 이슈용 PR 생성: `feat: NASA C-MAPSS 검증 파이프라인 추가 (#1)`

## 알려진 이슈
| 이슈 | 심각도 | 상태 |
|------|-------|------|
| AI허브 데이터는 아직 로컬 적재 전이라 보조 검증만 계획 상태 | 중간 | Open |
| 업로드된 이력을 조회/페이지네이션하는 읽기 API는 아직 없음 | 중간 | Planned |
| `OPENAI_API_KEY`용 `.env.example` 파일은 아직 없음 | 낮음 | Planned |
| OpenAI 설명 생성 실패 사유를 구조화 로그로 남기지 않는다 | 낮음 | Open |

## 기술 부채
| 항목 | 등록일 | 예상 작업량 |
|------|-------|-----------|
| lint/typecheck 도구 미설정 | 2026-04-03 | M |
| NASA 외 데이터셋 검증 자동화 미구현 | 2026-04-03 | M |
| validation 요약을 API로 노출하는 계층 미구현 | 2026-04-03 | M |
| 업로드 스키마와 분석 요청 스키마 통합 미완료 | 2026-04-03 | S |
| SQLite 마이그레이션이 수동 `ALTER TABLE` 수준이라 버전 관리 체계가 없음 | 2026-04-04 | S |

## 다음 계획
- [ ] `#3` 브랜치 커밋/PR 정리
- [ ] `#4` FactLog 웹 UI MVP 구현
- [ ] `#5` E2E 시나리오 및 검증 결과 정리
