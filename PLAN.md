# PLAN.md (이번 사이클 RED 단계)

대상 로드맵: `docs/PLAN.md` 6단계 "생산 라인" 중 세 번째·네 번째 항목 — 생산 완료 시 주문 상태 전환 및
재고 반영 (PRD 5.5). 6단계 마지막 로직 항목이다.

## 이번에 구현할 동작 (1가지)

현재 생산 중인 주문이 있을 때 `ProductionLineController.complete_current_production`을 호출하면,
`current_production`이 계산한 실 생산량만큼 시료 재고를 늘리고, 그 주문의 수량만큼 재고를 차감한 뒤
(순재고 변화 = 실생산량 − 주문 수량, 5단계에서 합의한 "재고는 CONFIRMED 전환 시점에 차감" 원칙과
동일하게 적용), 주문 상태를 `PRODUCING`에서 `CONFIRMED`로 전환하고 완료된 `Order`를 반환한다.
생산 중인 주문이 없으면 `None`을 반환한다.

## 설계 결정

- `app/controllers/production_line_controller.py`의 `ProductionLineController`에
  `complete_current_production() -> Order | None` 메서드를 추가한다.
  - 내부적으로 `self.current_production()`을 호출해 현재 생산 중인 주문과 `actual_production`
    (실 생산량)을 얻는다. `None`이면 그대로 `None`을 반환한다 (생산 중인 주문이 없음).
  - `self.sample_repository.find_by_id(order.sample_id)`로 시료를 다시 조회한다 (재고 반영을 위해
    최신 상태를 가져온다).
  - `sample.stock += actual_production`로 생산된 만큼 재고를 늘린다.
  - `sample.stock -= order.quantity`로 확정되는 주문 수량만큼 재고를 차감한다 (5단계에서 합의한
    "CONFIRMED 전환 시점에 차감" 원칙을 그대로 적용 — 순재고 변화 = 실생산량 − 부족분을 채우고 남는
    여유분).
  - `self.sample_repository.update(sample)`로 재고 변경을 저장한다.
  - `order.status = "CONFIRMED"`로 바꾸고 `self.order_repository.update(order)`로 저장한다.
  - 변경된 `Order`를 반환한다.
  - 동시에 여러 시료의 생산이 완료되는 시나리오, 재고가 음수가 되는 예외적 상황에 대한 처리는 이번
    사이클 범위 밖 (단일 생산 라인 전제, PRD 2장).
- `OrderRepository`, `SampleRepository`, `Order`, `Sample` 자체는 변경하지 않는다 (이미 존재하는
  `update`/`find_by_id`를 재사용).
- 콘솔 입출력(View)은 이번 사이클 범위 밖. 이 사이클을 끝으로 6단계의 로직 부분(계산식, 대기열 조회,
  완료 처리)이 모두 구현된다 — "생산 현황 표기"는 `current_production`/`waiting_orders`가 반환하는
  데이터를 View가 그대로 사용하면 되므로 별도 로직이 필요 없다.

## 테스트

- 파일: `tests/test_production_line_controller.py`에 테스트를 추가한다 (기존 파일 확장).
- 테스트 이름:
  1. `test_complete_current_production_returns_none_when_no_producing_order`
  2. `test_complete_current_production_confirms_order_and_updates_stock`
- 검증 내용:
  - (1) `PRODUCING` 주문이 없는 상태에서 `production_controller.complete_current_production()`을
    호출한 결과가 `None`인지 확인한다.
  - (2) 재고 5, 수율 0.9, 평균생산시간 30인 시료(`S-001`)를 저장하고, `OrderController`로 주문 수량
    20인 주문을 접수·승인해 `PRODUCING` 상태로 만든다 (재고 5 < 수량 20 → 부족분 15, 실생산량
    `ceil(15/0.9)=17`).
  - `production_controller.complete_current_production()`을 호출한다.
  - 반환된 `Order`의 `status`가 `"CONFIRMED"`인지 확인한다.
  - `order_repository.find_by_id(주문 id)`로 재조회했을 때도 `status`가 `"CONFIRMED"`인지 확인한다.
  - `sample_repository.find_by_id("S-001")`로 재조회했을 때 `stock`이 `5 + 17 - 20 = 2`인지 확인한다.
- mock 없이 실제 `OrderController`, `ProductionLineController`, `OrderRepository`,
  `SampleRepository`, `Order`, `Sample`, 실제 파일 시스템(`tmp_path`)을 사용하여 검증한다.

## 예상되는 최소 구현 방향 (GREEN 단계 참고용)

`ProductionLineController.complete_current_production`은 `self.current_production()` 결과가
`None`이면 `None`을 반환하고, 아니면 `order`/`actual_production`을 꺼내 시료를 다시 조회한 뒤
`sample.stock += actual_production; sample.stock -= order.quantity`로 재고를 갱신·저장하고,
`order.status = "CONFIRMED"`로 바꿔 저장한 뒤 `order`를 반환한다. View 연동, 예외적 동시성 처리는
이번 사이클에서 추가하지 않는다 — 이것으로 6단계 로직이 완성된다.
