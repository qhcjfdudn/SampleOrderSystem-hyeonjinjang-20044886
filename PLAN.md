# PLAN.md (이번 사이클 RED 단계)

대상 로드맵: `docs/PLAN.md` 5단계 "주문 승인/거절" 중 두 번째 항목 — 주문 승인, 재고가 충분한 경우
(PRD 5.4).

## 이번에 구현할 동작 (1가지)

`RESERVED` 상태인 주문에 대해 해당 시료의 재고가 주문 수량 이상일 때 `OrderController.approve_order`를
호출하면, 주문 상태가 `CONFIRMED`로 전환되고 시료 재고가 주문 수량만큼 차감된다.

## 설계 결정

- (5단계 전체 설계 방향 재확인, 이전 사이클에서 사용자와 합의됨)
  - 재고는 주문이 `CONFIRMED`로 전환되는 시점에 차감한다. 이번 사이클은 재고가 충분해 즉시
    `CONFIRMED`로 전환되는 경로만 다룬다.
  - 재고 부족 경로(`PRODUCING` 전환)는 다음 사이클에서 별도로 구현한다 (이번 사이클 범위 밖).
- `app/models/sample_repository.py`의 `SampleRepository`에 `update(sample: Sample) -> None` 메서드를
  추가한다.
  - `OrderRepository.update`와 동일한 패턴: `sample`의 5개 필드를 dict로 만들어
    `self._data_persistence.update(sample.id, record)`를 호출한다.
- `app/controllers/order_controller.py`의 `OrderController`에 `approve_order(order_id) -> Order`
  메서드를 추가한다.
  - `self.order_repository.find_by_id(order_id)`로 주문을 조회한다.
  - `self.sample_repository.find_by_id(order.sample_id)`로 해당 시료를 조회한다.
  - `sample.stock >= order.quantity`인 경우(재고 충분, 이번 사이클 범위):
    - `sample.stock -= order.quantity`로 재고를 차감하고 `self.sample_repository.update(sample)`로
      저장한다.
    - `order.status = "CONFIRMED"`로 변경하고 `self.order_repository.update(order)`로 저장한다.
  - 재고 부족(`sample.stock < order.quantity`)인 경우의 분기는 이번 사이클에서 다루지 않는다 — 다음
    사이클에서 `PRODUCING` 전환 로직을 추가할 때 이 메서드에 분기를 확장한다 (지금은 재고가 항상
    충분한 상황만 테스트/구현한다).
  - 변경된 `Order`를 반환한다.
  - 존재하지 않는 order_id/sample_id, 이미 다른 상태인 주문에 대한 예외 처리는 이번 사이클 범위 밖.
- 콘솔 입출력(View)은 이번 사이클 범위 밖.

## 테스트

- 파일: `tests/test_order_controller.py`에 테스트를 추가한다 (기존 파일 확장).
- 테스트 이름: `test_approve_order_confirms_order_and_deducts_stock_when_stock_is_sufficient`
- 검증 내용:
  - `tmp_path` fixture로 임시 `orders.json`, `samples.json` 경로를 만들고, 실제 `OrderRepository`,
    `SampleRepository`, `OrderController`, `SampleController`를 생성한다 (mock 없음).
  - `SampleController`로 재고 확보를 위해 `Sample`을 직접 `sample_repository.save(Sample(id="S-001",
    name="실리콘 웨이퍼-8인치", avg_production_time=30, yield_rate=0.9, stock=50))`로 저장한다
    (재고 50, 등록 시 재고 0으로 시작하는 `SampleController.register` 대신 재고 보유 시나리오를 직접
    구성하기 위해 `Sample`을 직접 생성 — 재고 확보 경로는 이번 사이클 대상이 아님).
  - `order_controller.place_order("S-001", "홍길동", 20, date(2026, 4, 16))`로 주문을 접수한다
    (재고 50 ≥ 주문 수량 20).
  - `order_controller.approve_order(주문 id)`를 호출한다.
  - 반환된 `Order`의 `status`가 `"CONFIRMED"`인지 확인한다.
  - `order_repository.find_by_id(주문 id)`로 재조회했을 때도 `status`가 `"CONFIRMED"`인지 확인한다.
  - `sample_repository.find_by_id("S-001")`로 재조회했을 때 `stock`이 `30`(50 − 20)으로 차감되었는지
    확인한다.
- mock 없이 실제 `OrderController`, `OrderRepository`, `SampleRepository`, `Order`, `Sample`, 실제
  파일 시스템(`tmp_path`)을 사용하여 검증한다.

## 예상되는 최소 구현 방향 (GREEN 단계 참고용)

`SampleRepository`에 `update(self, sample)`을 추가해 5개 필드를 dict로 만들어
`self._data_persistence.update(sample.id, record)`를 호출한다. `OrderController.approve_order`는
주문과 시료를 각각 조회한 뒤, 재고가 충분하면 재고를 차감·저장하고 주문 상태를 `CONFIRMED`로
바꿔 저장한 뒤 반환한다. 재고 부족 분기, 예외 처리, View 연동은 이번 사이클에서 추가하지 않는다.
