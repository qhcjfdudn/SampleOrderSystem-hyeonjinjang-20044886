# PLAN.md (이번 사이클 RED 단계)

대상 로드맵: `docs/PLAN.md` 5단계 "주문 승인/거절" 중 첫 번째 항목 — 주문 거절 (PRD 5.4).

## 이번에 구현할 동작 (1가지)

`RESERVED` 상태인 주문을 `OrderController.reject_order`에 전달해 거절하면, 해당 주문의 상태가
`REJECTED`로 전환되어 저장된다.

## 설계 결정

- (사용자와 합의된 5단계 전체 설계 방향, 이번 사이클 및 다음 사이클들에 적용)
  - 승인/거절 로직은 별도 클래스를 만들지 않고 기존 `OrderController`를 확장한다.
  - 재고 부족 시 "생산 라인 등록"은 별도 큐 자료구조 없이, `OrderRepository`에 저장된 `PRODUCING`
    상태 주문을 주문번호(`id`, `ORD-YYYYMMDD-NNNN` 형식이라 문자열 정렬이 곧 시간순) 순으로 조회하는
    것으로 대체한다 (6단계에서 실제 큐 소비/생산 계산 구현).
  - 재고는 주문이 `CONFIRMED`로 전환되는 시점에만 차감한다 (즉시 승인이든, 이후 생산 완료 후
    전환이든 동일). 이번 사이클(거절)은 재고를 다루지 않는다.
- `OrderController`(`app/controllers/order_controller.py`) 생성자를 `OrderController(order_repository,
  sample_repository)`로 변경한다 (다음 사이클의 승인 로직이 재고 확인을 위해 `sample_repository`가
  필요하므로 미리 주입 구조를 확장해둔다). 기존 `place_order`는 `sample_repository`를 사용하지 않지만
  생성자 시그니처 변경은 이번 사이클에서 함께 반영한다.
- 메서드: `reject_order(order_id) -> Order`
  - `self.order_repository.find_by_id(order_id)`로 주문을 조회한다.
  - 조회된 `Order`의 `status`를 `"REJECTED"`로 변경한다.
  - 변경된 주문을 `self.order_repository.save(order)`로 다시 저장한다 (`DataPersistence.create`가
    아니라 갱신이 필요하므로, `OrderRepository`에 `update(order) -> None` 메서드를 추가해
    `DataPersistence.update(order.id, changes)`를 호출한다 — 기존 레코드를 그대로 덮어쓰기 위해 5개
    필드 전체를 `changes`로 전달).
  - 변경된 `Order` 객체를 반환한다.
  - 존재하지 않는 order_id, 이미 다른 상태인 주문에 대한 예외 처리는 이번 사이클 범위 밖 (PRD에 명시
    없음, 최소 구현으로 시작).
- `app/models/order_repository.py`의 `OrderRepository`에 `update(order: Order) -> None` 메서드를
  추가한다.
  - `order`의 5개 필드를 dict로 만들어 `self._data_persistence.update(order.id, record)`를 호출한다
    (`DataPersistence.update(id, changes: dict)`는 이미 존재하는 API,
    `C:\reviewer\PoC\DataPersistence\data_persistence\processor.py` 확인).
- 재고 확인에 따른 승인(CONFIRMED/PRODUCING) 로직은 이번 사이클 범위 밖 (다음 사이클에서 진행).
- 콘솔 입출력(View)은 이번 사이클 범위 밖.

## 테스트

- 파일: `tests/test_order_controller.py`에 테스트를 추가한다 (기존 파일 확장, 생성자 시그니처 변경에
  맞춰 기존 테스트의 `OrderController(repository)` 호출도 `OrderController(repository,
  sample_repository)`로 함께 수정한다).
- 테스트 이름: `test_reject_order_transitions_status_to_rejected`
- 검증 내용:
  - `tmp_path` fixture로 임시 `orders.json`, `samples.json` 경로를 만들고, 실제 `OrderRepository`,
    `SampleRepository`, `OrderController`를 생성한다 (mock 없음).
  - `controller.place_order("S-001", "홍길동", 20, date(2026, 4, 16))`로 `RESERVED` 상태 주문을 하나
    생성한다.
  - `controller.reject_order(생성된 주문의 id)`를 호출한다.
  - 반환된 `Order`의 `status`가 `"REJECTED"`인지 확인한다.
  - `order_repository.find_by_id(주문 id)`로 다시 조회했을 때도 `status`가 `"REJECTED"`로 저장되어
    있는지 확인한다 (실제로 영속화되었는지 검증).
- mock 없이 실제 `OrderController`, `OrderRepository`, `SampleRepository`, `Order`, 실제 파일 시스템
  (`tmp_path`)을 사용하여 검증한다.

## 예상되는 최소 구현 방향 (GREEN 단계 참고용)

`app/models/order_repository.py`의 `OrderRepository`에 `update(self, order)`를 추가해 5개 필드를
dict로 만들어 `self._data_persistence.update(order.id, record)`를 호출한다.
`app/controllers/order_controller.py`의 `OrderController.__init__`에 `sample_repository` 인자를
추가하고 보관한다(이번 사이클에서는 사용하지 않음). `reject_order(self, order_id)`는
`find_by_id`로 주문을 조회하고 `status = "REJECTED"`로 바꾼 뒤 `update`로 저장하고 반환한다.
승인 로직, 재고 확인, View 연동은 이번 사이클에서 추가하지 않는다.
