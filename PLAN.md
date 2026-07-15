# PLAN.md (이번 사이클 RED 단계)

대상 로드맵: `docs/PLAN.md` 4단계 "시료 주문" — 시료 예약 입력(시료 ID/고객명/주문 수량) 처리, 상태
`RESERVED`로 생성 (PRD 5.3).

## 이번에 구현할 동작 (1가지)

`OrderController.place_order`에 시료 ID/고객명/주문 수량과 주문 접수 일자를 전달하면, 그 날짜 기준으로
`ORD-YYYYMMDD-NNNN` 형식의 새 주문번호를 채번해 상태 `RESERVED`인 `Order`를 생성·저장하고, 생성된
`Order`를 반환한다.

## 설계 결정

- 위치: `app/controllers/order_controller.py`, 클래스명 `OrderController`
- 생성자: `OrderController(order_repository)` — 기존 `OrderRepository` 인스턴스를 주입받는다
  (`SampleController`와 동일한 패턴, PRD 8장 MVC 계층 분리).
- `OrderRepository`(`app/models/order_repository.py`)에 `find_all() -> list[Order]` 메서드를 추가한다.
  - `SampleRepository.find_all()`과 동일한 패턴: `self._data_persistence.read_all()`로 전체 레코드를
    조회한 뒤 각 dict를 `Order(**record)`로 변환해 리스트로 반환한다.
  - 채번 시 "해당 날짜에 이미 접수된 주문 수"를 세기 위해 필요하다.
- 메서드: `place_order(sample_id, customer_name, quantity, order_date) -> Order`
  - `order_date`는 `datetime.date` 객체를 그대로 전달받는다 (현재 시각을 Controller 내부에서 직접
    구하지 않고 호출자가 주입 — 테스트 결정론성 확보 및 실제 시각 조회는 이후 View/main에서 담당,
    PRD 9장 "mock 없이 실제 로직 검증" 원칙에 맞춰 순수 로직으로 유지).
  - 채번 규칙: `order_date`를 `YYYYMMDD`로 포맷한 문자열을 접두어로 사용하고, `order_repository.
    find_all()` 결과 중 `id`가 `ORD-{YYYYMMDD}-`로 시작하는 주문 개수를 세어 그 다음 순번(1부터 시작)을
    4자리 0-패딩(`{:04d}`)으로 붙인다. 예) 해당 날짜 주문이 0건이면 `ORD-20260416-0001`.
  - `Order(id=생성된 주문번호, sample_id=sample_id, customer_name=customer_name, quantity=quantity,
    status="RESERVED")`를 생성한다 (PRD 5.3 — 예약 시점 상태는 `RESERVED`).
  - `order_repository.save(order)`로 저장한다.
  - 생성한 `Order` 객체를 반환한다.
- 재고 확인에 따른 `CONFIRMED`/`PRODUCING` 자동 전환, 승인/거절 로직은 이번 사이클 범위 밖 (5단계에서
  진행).
- 콘솔 입출력(View)은 이번 사이클 범위 밖.
- 동시성(같은 순간 여러 주문 접수 시 채번 충돌) 처리는 이번 사이클 범위 밖 — 콘솔 단일 사용자 흐름을
  전제로 순차 처리한다고 가정한다 (PRD 2장 "콘솔 기반, 담당자가 직접 메뉴 입력").

## 테스트

- 파일: `tests/test_order_controller.py` (신규)
- 테스트 이름: `test_place_order_generates_order_id_and_saves_reserved_order`
- 검증 내용:
  - `tmp_path` fixture로 임시 `orders.json` 경로를 만들고, 실제 `OrderRepository`·`OrderController`를
    생성한다 (mock 없음).
  - `date(2026, 4, 16)`을 `order_date`로 사용해 `controller.place_order("S-001", "홍길동", 20,
    date(2026, 4, 16))`를 호출한다.
  - 반환된 `Order`의 `id`가 `"ORD-20260416-0001"`이고, `sample_id`, `customer_name`, `quantity`가
    입력값과 동일하며 `status`가 `"RESERVED"`인지 확인한다.
  - 같은 날짜로 `controller.place_order("S-002", "김철수", 5, date(2026, 4, 16))`를 한 번 더 호출하면
    반환된 `Order.id`가 `"ORD-20260416-0002"`로 순번이 증가하는지 확인한다 (같은 날짜 내 채번 검증).
  - `order_repository.find_by_id("ORD-20260416-0001")`로 조회했을 때도 저장된 값이 동일한지 확인한다.
- mock 없이 실제 `OrderController`, `OrderRepository`, `Order`, 실제 파일 시스템(`tmp_path`)을 사용하여
  검증한다.

## 예상되는 최소 구현 방향 (GREEN 단계 참고용)

`app/models/order_repository.py`의 `OrderRepository`에 `find_all(self) -> list`를 추가해
`self._data_persistence.read_all()` 결과 각 dict를 `Order(**record)`로 변환한 리스트를 반환한다.
`app/controllers/order_controller.py`에 `OrderController` 클래스를 정의한다. 생성자에서
`order_repository`를 보관하고, `place_order`는 `order_date.strftime("%Y%m%d")`로 접두어를 만든 뒤
`order_repository.find_all()`에서 해당 접두어로 시작하는 `id` 개수를 세어 순번을 매기고, `Order`를
생성해 저장 후 반환한다. 승인/거절, 재고 확인, View 연동 등은 이번 사이클에서 추가하지 않는다.
