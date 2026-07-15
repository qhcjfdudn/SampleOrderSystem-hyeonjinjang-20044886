# PLAN.md (이번 사이클 RED 단계)

대상 로드맵: `docs/PLAN.md` 5단계 "주문 승인/거절" 중 세 번째 항목 — 주문 승인, 재고가 부족한 경우
(PRD 5.4). 5단계 마지막 항목이다.

## 이번에 구현할 동작 (1가지)

`RESERVED` 상태인 주문에 대해 해당 시료의 재고가 주문 수량보다 적을 때 `OrderController.approve_order`를
호출하면, 주문 상태가 `PRODUCING`으로 전환되고(재고는 이번 시점에 차감하지 않는다) 저장된다.

## 설계 결정

- (5단계 전체 설계 방향 재확인)
  - "생산 라인 등록"은 별도 큐 자료구조 없이, 주문 상태를 `PRODUCING`으로 전환하는 것만으로 표현한다.
    실제 생산 큐 조회/FIFO 처리/생산 완료 후 `CONFIRMED` 전환 및 재고 반영은 6단계(생산 라인)에서
    `OrderRepository.find_all()`을 이용해 `status == "PRODUCING"`인 주문을 주문번호(id) 순으로
    조회하는 방식으로 구현한다.
  - 재고는 `CONFIRMED` 전환 시점에만 차감한다는 원칙에 따라, 이번 사이클(재고 부족 → `PRODUCING`)은
    재고를 전혀 변경하지 않는다. 재고 반영은 6단계에서 생산 완료 후 `PRODUCING` → `CONFIRMED` 전환
    시점에 이뤄진다 (부족분 생산으로 재고를 채운 뒤, 확정 시 주문 수량만큼 차감 — 6단계 사이클에서
    구체화).
- `app/controllers/order_controller.py`의 기존 `approve_order(order_id) -> Order` 메서드를 확장한다
  (이전 사이클에서 재고 충분 분기만 구현되어 있음, 이번 사이클에서 `else` 분기를 추가).
  - `sample.stock >= order.quantity`가 아닌 경우(재고 부족):
    - `order.status = "PRODUCING"`으로 변경하고 `self.order_repository.update(order)`로 저장한다.
    - 재고(`sample.stock`)는 변경하지 않는다 (`sample_repository.update`를 호출하지 않는다).
  - 두 분기(재고 충분/부족) 모두 마지막에 변경된 `Order`를 반환한다 (기존 구조 유지, 분기 후 공통
    return으로 정리 가능).
- 예외 처리(존재하지 않는 order_id/sample_id, 이미 다른 상태인 주문 재승인 등)는 이번 사이클 범위 밖
  — 5단계 전체에서 계속 유지해온 범위 제한.
- 콘솔 입출력(View)은 이번 사이클 범위 밖.

## 테스트

- 파일: `tests/test_order_controller.py`에 테스트를 추가한다 (기존 파일 확장).
- 테스트 이름: `test_approve_order_sets_producing_and_keeps_stock_when_stock_is_insufficient`
- 검증 내용:
  - `tmp_path` fixture로 임시 `orders.json`, `samples.json` 경로를 만들고, 실제 `OrderRepository`,
    `SampleRepository`, `OrderController`를 생성한다 (mock 없음).
  - `sample_repository.save(Sample(id="S-001", name="실리콘 웨이퍼-8인치", avg_production_time=30,
    yield_rate=0.9, stock=5))`로 재고 5인 시료를 저장한다.
  - `order_controller.place_order("S-001", "홍길동", 20, date(2026, 4, 16))`로 주문 수량 20인 주문을
    접수한다 (재고 5 < 주문 수량 20, 재고 부족 상황).
  - `order_controller.approve_order(주문 id)`를 호출한다.
  - 반환된 `Order`의 `status`가 `"PRODUCING"`인지 확인한다.
  - `order_repository.find_by_id(주문 id)`로 재조회했을 때도 `status`가 `"PRODUCING"`인지 확인한다.
  - `sample_repository.find_by_id("S-001")`로 재조회했을 때 `stock`이 여전히 `5`로 변경되지 않았는지
    확인한다 (재고는 이 시점에 차감되지 않아야 함).
- mock 없이 실제 `OrderController`, `OrderRepository`, `SampleRepository`, `Order`, `Sample`, 실제
  파일 시스템(`tmp_path`)을 사용하여 검증한다.

## 예상되는 최소 구현 방향 (GREEN 단계 참고용)

`OrderController.approve_order`의 기존 `if sample.stock >= order.quantity:` 블록에 `else` 분기를
추가해, 재고 부족 시 `order.status = "PRODUCING"`으로 바꾸고 `order_repository.update(order)`로
저장한 뒤(재고는 변경하지 않음) 함수 끝에서 `order`를 반환한다. 생산 큐 조회, 생산 계산, 예외 처리,
View 연동은 이번 사이클에서 추가하지 않는다 — 6단계(생산 라인)로 이어진다.
