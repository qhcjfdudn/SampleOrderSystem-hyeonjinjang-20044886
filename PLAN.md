# PLAN.md (이번 사이클 RED 단계)

대상 로드맵: `docs/PLAN.md` 5단계 "주문 승인/거절" 중 첫 번째 항목 — `RESERVED` 주문 목록 표시
(PRD 5.4). 승인/거절 로직(두 번째, 세 번째 항목)은 이전 사이클들에서 이미 구현 완료.

## 이번에 구현할 동작 (1가지)

여러 상태(`RESERVED`, `CONFIRMED` 등)의 주문이 섞여 있을 때 `OrderController.list_reserved_orders`를
호출하면, `RESERVED` 상태인 주문만 `Order` 목록으로 반환한다.

## 설계 결정

- `app/controllers/order_controller.py`의 `OrderController`에 `list_reserved_orders() -> list[Order]`
  메서드를 추가한다.
  - `self.order_repository.find_all()`로 전체 주문을 조회한 뒤, `status == "RESERVED"`인 주문만
    필터링해 리스트로 반환한다 (`SampleController.search_by_name`이 `find_all()` 결과를 Controller
    레벨에서 필터링하는 것과 동일한 패턴).
  - "표시(화면 출력)"는 View의 책임이며, 이번 사이클은 "표시할 대상 데이터를 조회하는" 로직만
    구현한다 — 이는 3단계 "시료 조회"(`list_samples`)를 콘솔 출력 없이 데이터 조회로 구현했던 것과
    동일한 원칙이다 (콘솔 입출력은 9단계 메인 메뉴 연결에서 View와 함께 다룬다).
  - `OrderRepository`나 `Order`는 변경하지 않는다.
- 정렬 규칙(주문번호 순 등)은 PRD에 명시가 없으므로 이번 사이클에서 강제하지 않는다.
- 콘솔 입출력(View)은 이번 사이클 범위 밖.

## 테스트

- 파일: `tests/test_order_controller.py`에 테스트를 추가한다 (기존 파일 확장).
- 테스트 이름: `test_list_reserved_orders_returns_only_reserved_orders`
- 검증 내용:
  - `tmp_path` fixture로 임시 `orders.json`, `samples.json` 경로를 만들고, 실제 `OrderRepository`,
    `SampleRepository`, `OrderController`를 생성한다 (mock 없음).
  - `sample_repository.save(Sample(id="S-001", ..., stock=50))`로 재고 충분한 시료를 저장한다.
  - `controller.place_order("S-001", "홍길동", 10, date(2026, 4, 16))`로 주문 A를 접수한다
    (`RESERVED` 상태로 남음).
  - `controller.place_order("S-001", "김철수", 5, date(2026, 4, 16))`로 주문 B를 접수한 뒤
    `controller.approve_order(주문 B의 id)`로 즉시 승인해 `CONFIRMED`로 전환한다 (재고 충분).
  - `controller.list_reserved_orders()`를 호출한 결과가 길이 1인 리스트이며, 그 안의 `Order.id`가
    주문 A의 id와 같고 `status`가 `"RESERVED"`인지 확인한다 (주문 B는 `CONFIRMED`라 제외되어야 함).
- mock 없이 실제 `OrderController`, `OrderRepository`, `SampleRepository`, `Order`, `Sample`, 실제
  파일 시스템(`tmp_path`)을 사용하여 검증한다.

## 예상되는 최소 구현 방향 (GREEN 단계 참고용)

`OrderController`에 `list_reserved_orders(self)`를 추가해 `self.order_repository.find_all()` 결과를
`order.status == "RESERVED"`로 필터링한 리스트를 반환한다. 정렬, 콘솔 출력 등은 이번 사이클에서
추가하지 않는다.
