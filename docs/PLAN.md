# PLAN.md

개발 진행 순서다. 각 항목의 상세 스펙은 [docs/PRD.md](PRD.md) 참고.

각 단계의 각 항목은 `docs/PRD.md` 9장(TDD)·10장(Subagent 워크플로우)에 따라
`doc-consistency-verify → ai-action(RED) → [RED 리뷰: 사용자 검토] → ai-action(GREEN) →
{compliance-verify, test-verify 병렬} → [REVIEW: 사용자 검토] → 커밋` 사이클 단위로 진행한다.
이번 파일은 전체 로드맵이며, 각 사이클의 RED 단계에서 작성하는 세부 `PLAN.md`(프로젝트 루트, 동작 1개 단위)와는
별개다.

## 1단계 — 프로젝트 골격

- [x] `../PoC/ConsoleMVC`의 `mvc-skeleton` Skill로 `app/{models,views,controllers}`, `config.py`, `main.py`,
      `requirements.txt` 골격 생성 (PRD 8장)
- [x] `pyproject.toml` 작성, `data-persistence`를 `../PoC/DataPersistence` 로컬 editable 의존성으로 추가
- [x] `pip install -e ../PoC/DataPersistence` 실행 후 `import data_persistence` 확인
- [x] `pytest`, `pytest-cov` 등 테스트 의존성 추가

## 2단계 — 데이터 계층 (Model)

- [x] `app/models`에 시료(Sample) 모델 구현 — 필드: 시료 ID, 이름, 평균 생산시간, 수율, 현재 재고 (PRD 6장)
- [x] `app/models`에 주문(Order) 모델 구현 — 필드: 주문번호, 시료 ID, 고객명, 주문 수량, 상태 (PRD 6장)
- [x] `data_persistence.DataPersistence`로 `samples.json`, `orders.json` 각각 CRUD 연동 (PRD 7장)

## 3단계 — 시료 관리

- [x] 시료 등록 (시료 ID/이름/평균 생산시간/수율 입력) (PRD 5.2)
- [x] 시료 조회 (전체 목록 + 현재 재고 표시)
- [x] 시료 검색 (이름 등 속성 검색)

## 4단계 — 시료 주문

- [x] 시료 예약 입력(시료 ID/고객명/주문 수량) 처리, 상태 `RESERVED`로 생성 (PRD 5.3)

## 5단계 — 주문 승인/거절

- [x] `RESERVED` 주문 목록 표시 (PRD 5.4)
- [x] 주문 승인 — 재고 충분 시 `CONFIRMED`, 재고 부족 시 생산 라인 등록 + `PRODUCING` 전환
- [x] 주문 거절 — `REJECTED` 전환

## 6단계 — 생산 라인

- [x] 부족분(주문 수량 − 재고) / 실생산량(ceil(부족분/수율)) / 총 생산 시간(평균 생산시간 × 실생산량) 계산 (PRD 5.5)
- [x] 생산 큐 FIFO 처리 및 대기 목록 조회
- [x] 생산 완료 시 주문 상태 `PRODUCING` → `CONFIRMED` 전환, 재고 반영
- [x] 생산 현황(현재 생산 중인 시료 정보) 표시

## 7단계 — 출고 처리

- [x] `CONFIRMED` 주문 목록 표시 및 출고 실행, 상태 `RELEASE` 전환 (PRD 5.6)

## 8단계 — 모니터링

- [x] 상태별(`RESERVED`/`CONFIRMED`/`PRODUCING`/`RELEASE`) 주문 현황 집계 (`REJECTED` 제외) (PRD 5.7)
- [x] 시료별 재고 현황 및 여유/부족/고갈 상태 표시

## 9단계 — 메인 메뉴 연결

- [x] `main.py`에서 메인 메뉴(시료 관리/시료 주문/주문 승인·거절/모니터링/생산 라인 조회/출고 처리) 루프 연결 (PRD 5.1)
- [x] 메인 메뉴 요약 정보(등록 시료 수, 총 재고, 전체 주문 건수, 생산라인 대기 건수) 표시

## 10단계 — 마무리

- [ ] `CLAUDE.md`에 실제 빌드/실행/테스트 명령어와 구현된 코드 스타일·구조 반영
- [ ] 전체 기능에 대해 원본 요구사항 자료의 예시 UI 흐름과 실제 동작 비교 확인
