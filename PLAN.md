# PLAN.md (이번 사이클 RED 단계)

대상 로드맵: `docs/PLAN.md` 6단계 "생산 라인" 중 첫 번째 항목 — 부족분/실 생산량/총 생산 시간 계산 및
현재 생산 중인 주문 정보 표시 (PRD 5.5).

## 이번에 구현할 동작 (1가지)

`PRODUCING` 상태 주문이 있을 때 `ProductionLineController.current_production`을 호출하면, 단일 생산
라인 규칙(한 번에 하나씩 생산)에 따라 주문번호(id) 순으로 가장 먼저 등록된 `PRODUCING` 주문 하나에
대해 부족분/실 생산량/총 생산 시간을 현재 재고 기준으로 계산해 반환한다. `PRODUCING` 주문이 없으면
`None`을 반환한다.

## 설계 결정

- (6단계 전체 설계 방향, 사용자와 합의됨)
  - 생산 라인 로직은 별도 클래스 `app/controllers/production_line_controller.py`의
    `ProductionLineController`에 둔다 (`OrderController`를 더 확장하지 않고 책임 분리).
  - 생산 큐는 별도 자료구조 없이 `OrderRepository`에 저장된 `PRODUCING` 주문을 주문번호(id, 시간순
    정렬과 동치) 순으로 조회하는 것으로 대체한다. 정렬된 목록의 첫 번째가 "현재 생산 중", 나머지가
    "대기 큐"이다 (단일 라인, FIFO — PRD 2장/5.5).
  - 생산 완료는 시간 경과를 시뮬레이션하지 않고, 생산 담당자가 명시적으로 완료 처리 액션을 호출하는
    방식으로 구현한다 (다음 사이클에서 `complete_current_production` 등으로 구현, 이번 사이클 범위
    밖).
  - 부족분/실 생산량은 승인(PRODUCING 전환) 시점이 아니라, 조회/완료 시점의 **현재** 재고를 기준으로
    매번 새로 계산한다 (승인 이후 다른 주문 처리로 재고가 바뀔 수 있으므로).
- 위치: `app/controllers/production_line_controller.py`, 클래스명 `ProductionLineController`
- 생성자: `ProductionLineController(order_repository, sample_repository)` — 두 저장소를 주입받는다
  (`OrderController`와 동일한 패턴).
- 메서드: `current_production() -> dict | None`
  - `self.order_repository.find_all()`에서 `status == "PRODUCING"`인 주문만 필터링한다.
  - 필터링된 주문이 없으면 `None`을 반환한다.
  - 있으면 `id` 기준 오름차순 정렬(`sorted(..., key=lambda o: o.id)`) 후 첫 번째 주문을 대상으로
    삼는다 (`ORD-YYYYMMDD-NNNN` 형식이라 문자열 정렬이 곧 시간순).
  - `self.sample_repository.find_by_id(order.sample_id)`로 시료를 조회한다.
  - 계산 (PRD 5.5 공식 그대로):
    - 부족분 = `order.quantity - sample.stock`
    - 실 생산량 = `math.ceil(부족분 / sample.yield_rate)`
    - 총 생산 시간 = `sample.avg_production_time * 실생산량`
  - 반환값은 dict로 구성한다: `{"order": order, "shortfall": 부족분, "actual_production": 실생산량,
    "total_production_time": 총생산시간}` (PRD 5.5 "표기 정보 수준은 구현 시 자율적으로 결정"에 따라
    자료구조를 dict로 단순화, View가 이후 필요한 필드를 꺼내 쓴다).
- 대기 큐 조회, 생산 완료 처리, 재고 반영, 콘솔 출력(View)은 이번 사이클 범위 밖 (다음 사이클들에서
  진행).

## 테스트

- 파일: `tests/test_production_line_controller.py` (신규)
- 테스트 이름:
  1. `test_current_production_returns_none_when_no_producing_order`
  2. `test_current_production_calculates_shortfall_and_actual_production_for_earliest_producing_order`
- 검증 내용:
  - (1) `tmp_path` fixture로 임시 `orders.json`, `samples.json` 경로를 만들고, 실제 `OrderRepository`,
    `SampleRepository`, `ProductionLineController`를 생성한다 (mock 없음, 아무 주문도 없는 상태).
    `controller.current_production()`을 호출한 결과가 `None`인지 확인한다.
  - (2) 재고 5, 수율 0.9, 평균 생산시간 30인 시료(`S-001`)를 저장한다. `OrderController`로 주문
    수량 20인 주문을 접수(`place_order`)하고 `approve_order`로 재고 부족 경로를 태워 `PRODUCING`
    상태로 만든다 (재고 5 < 수량 20). `production_controller.current_production()`을 호출한다.
    - 반환된 dict의 `order.id`가 해당 주문의 id와 같은지 확인한다.
    - `shortfall`이 `20 - 5 = 15`인지 확인한다.
    - `actual_production`이 `math.ceil(15 / 0.9) = 17`인지 확인한다.
    - `total_production_time`이 `30 * 17 = 510`인지 확인한다.
  - 두 시나리오 모두 mock 없이 실제 `OrderController`(주문 접수/승인용), `ProductionLineController`,
    `OrderRepository`, `SampleRepository`, `Order`, `Sample`, 실제 파일 시스템(`tmp_path`)을 사용하여
    검증한다.

## 예상되는 최소 구현 방향 (GREEN 단계 참고용)

`app/controllers/production_line_controller.py`에 `ProductionLineController` 클래스를 정의한다.
생성자에서 `order_repository`, `sample_repository`를 보관하고, `current_production`은
`order_repository.find_all()`을 `status == "PRODUCING"`으로 필터링·`id`로 정렬해 첫 번째 주문을
고른 뒤(없으면 `None`), 해당 시료를 조회해 `math.ceil`로 부족분/실생산량/총생산시간을 계산한 dict를
반환한다. 대기 큐 조회, 완료 처리, View 연동은 이번 사이클에서 추가하지 않는다.
