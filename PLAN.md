# PLAN.md (이번 사이클 RED 단계)

대상 로드맵: `docs/PLAN.md` 7단계 "출고 처리" 중 두 번째 항목 — 출고 실행, 상태 `RELEASE` 전환
(PRD 5.6). 7단계 마지막 항목이다.

## 이번에 구현할 동작 (1가지)

`CONFIRMED` 상태인 주문을 `OrderController.release_order`에 전달해 출고를 실행하면, 해당 주문의
상태가 `RELEASE`로 전환되어 저장된다.

## 설계 결정

- `app/controllers/order_controller.py`의 `OrderController`에 `release_order(order_id) -> Order`
  메서드를 추가한다.
  - `self.order_repository.find_by_id(order_id)`로 주문을 조회한다.
  - `order.status = "RELEASE"`로 변경한다.
  - `self.order_repository.update(order)`로 저장한다.
  - 변경된 `Order`를 반환한다.
  - `reject_order`와 완전히 동일한 형태(단순 상태 전이, 재고 변경 없음)이다 — 재고는 이미 승인
    (`CONFIRMED` 전환) 시점에 차감되어 있으므로 출고 시점에는 재고를 다시 변경하지 않는다 (PRD 5.6
    "재고가 충분해진 CONFIRMED 주문에 대하여 출고를 처리"는 재고 상태를 조건으로 언급할 뿐, 출고
    자체가 재고를 변경한다는 서술은 없다 — 5·6단계에서 합의한 "CONFIRMED 전환 시점에만 재고 차감"
    원칙과 일치).
  - 존재하지 않는 order_id, 이미 다른 상태인 주문에 대한 예외 처리는 이번 사이클 범위 밖 (5단계
    `reject_order`/`approve_order`와 동일하게 최소 구현 유지).
- `OrderRepository`, `SampleRepository`, `Order`, `Sample`은 변경하지 않는다.
- 콘솔 입출력(View)은 이번 사이클 범위 밖. 이 사이클을 끝으로 7단계(출고 처리)가 모두 구현된다.

## 테스트

- 파일: `tests/test_order_controller.py`에 테스트를 추가한다 (기존 파일 확장).
- 테스트 이름: `test_release_order_transitions_status_to_release_without_changing_stock`
- 검증 내용:
  - `tmp_path` fixture로 임시 `orders.json`, `samples.json` 경로를 만들고, 실제 `OrderRepository`,
    `SampleRepository`, `OrderController`를 생성한다 (mock 없음).
  - 재고 충분한 시료(`S-001`, stock=50)를 저장한다.
  - `controller.place_order("S-001", "홍길동", 20, date(2026, 4, 16))`로 주문을 접수하고
    `controller.approve_order(주문 id)`로 즉시 승인해 `CONFIRMED` 상태로 만든다 (재고는 50 - 20 = 30
    으로 차감됨).
  - `controller.release_order(주문 id)`를 호출한다.
  - 반환된 `Order`의 `status`가 `"RELEASE"`인지 확인한다.
  - `order_repository.find_by_id(주문 id)`로 재조회했을 때도 `status`가 `"RELEASE"`인지 확인한다.
  - `sample_repository.find_by_id("S-001")`로 재조회했을 때 `stock`이 여전히 `30`으로(출고로 인해
    추가로 변경되지 않고) 유지되는지 확인한다.
- mock 없이 실제 `OrderController`, `OrderRepository`, `SampleRepository`, `Order`, `Sample`, 실제
  파일 시스템(`tmp_path`)을 사용하여 검증한다.

## 예상되는 최소 구현 방향 (GREEN 단계 참고용)

`OrderController.release_order`는 `reject_order`와 동일한 구조로, `find_by_id`로 주문을 조회하고
`status = "RELEASE"`로 바꾼 뒤 `update`로 저장하고 반환한다. 재고 변경, 예외 처리, View 연동은 이번
사이클에서 추가하지 않는다 — 이것으로 7단계가 완성된다.
