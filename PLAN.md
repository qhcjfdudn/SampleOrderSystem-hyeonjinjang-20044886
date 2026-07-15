# PLAN.md (이번 사이클 RED 단계)

대상 로드맵: `docs/PLAN.md` 6단계 "생산 라인" 중 두 번째 항목 — 생산 큐 FIFO 처리 및 대기 목록 조회
(PRD 5.5 "대기 주문 확인").

## 이번에 구현할 동작 (1가지)

`PRODUCING` 상태 주문이 여러 건 있을 때 `ProductionLineController.waiting_orders`를 호출하면, 현재
생산 중인 주문(`current_production`이 가리키는, 가장 먼저 등록된 것) 하나를 제외한 나머지 `PRODUCING`
주문을 주문번호(id) 순으로 정렬한 목록으로 반환한다.

## 설계 결정

- `app/controllers/production_line_controller.py`의 `ProductionLineController`에
  `waiting_orders() -> list[Order]` 메서드를 추가한다.
  - `self.order_repository.find_all()`에서 `status == "PRODUCING"`인 주문만 필터링한다.
  - `id` 기준 오름차순 정렬한다 (`current_production`과 동일한 정렬 기준 — 단일 라인 FIFO 원칙).
  - 정렬된 목록에서 첫 번째(현재 생산 중인 주문)를 제외한 나머지를 반환한다 (`sorted_list[1:]`).
  - `PRODUCING` 주문이 0건이거나 1건이면 빈 리스트를 반환한다 (제외할 "현재 생산 중" 자체가 없거나,
    대기 중인 주문이 없는 경우).
  - `current_production`과 정렬 로직이 중복되지만, 이번 사이클은 별도 헬퍼로 리팩터링하지 않고
    최소 구현으로 유지한다 (두 메서드 모두 간단한 필터+정렬이라 중복 비용이 낮음).
- `OrderRepository`, `Sample`, `Order`는 변경하지 않는다.
- 생산 완료 처리, 재고 반영, 콘솔 출력(View)은 이번 사이클 범위 밖.

## 테스트

- 파일: `tests/test_production_line_controller.py`에 테스트를 추가한다 (기존 파일 확장).
- 테스트 이름: `test_waiting_orders_returns_producing_orders_excluding_the_current_one`
- 검증 내용:
  - `tmp_path` fixture로 임시 `orders.json`, `samples.json` 경로를 만들고, 실제 `OrderRepository`,
    `SampleRepository`, `OrderController`, `ProductionLineController`를 생성한다 (mock 없음).
  - 재고가 부족한 시료(`S-001`, stock=5)를 저장한다.
  - 주문 3건을 같은 날짜로 순서대로 접수(`place_order`)하고 각각 `approve_order`로 승인해 모두
    `PRODUCING` 상태로 만든다 (재고 5 < 각 주문 수량이 되도록 수량을 충분히 크게 설정, 예: 20, 20, 20).
  - `production_controller.waiting_orders()`를 호출한 결과가 길이 2인 리스트이며, 그 안의 주문
    id가 두 번째·세 번째로 접수한 주문의 id와 순서대로(id 오름차순) 일치하는지 확인한다 (첫 번째
    주문은 `current_production`의 대상이라 제외되어야 함).
  - `PRODUCING` 주문이 하나도 없는 상태에서 `waiting_orders()`를 호출하면 빈 리스트가 반환되는지도
    별도로 확인한다 (같은 테스트 함수 안에서 새 컨트롤러로 검증하거나, 별도 테스트로 분리 — 아래
    "예상되는 최소 구현 방향" 참고).
- mock 없이 실제 `OrderController`, `ProductionLineController`, `OrderRepository`, `SampleRepository`,
  `Order`, `Sample`, 실제 파일 시스템(`tmp_path`)을 사용하여 검증한다.

## 예상되는 최소 구현 방향 (GREEN 단계 참고용)

`ProductionLineController.waiting_orders`는 `current_production`과 동일하게 `PRODUCING` 주문을
필터링·`id`로 정렬한 뒤, 슬라이싱(`[1:]`)으로 첫 번째를 제외한 리스트를 반환한다. `PRODUCING` 주문이
0건 또는 1건이면 슬라이싱 결과가 자연스럽게 빈 리스트가 된다 (별도 분기 불필요). 생산 완료 처리, 재고
반영, View 연동은 이번 사이클에서 추가하지 않는다.
