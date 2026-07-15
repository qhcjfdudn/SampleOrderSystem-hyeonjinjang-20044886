# PLAN.md (이번 사이클 RED 단계)

대상 로드맵: `docs/PLAN.md` 2단계 "데이터 계층 (Model)" 중 두 번째 항목 — 주문(Order) 모델.

## 이번에 구현할 동작 (1가지)

Order 객체를 주문번호/시료 ID/고객명/주문 수량/상태 값으로 생성하면 각 속성에 그 값이 그대로 저장된다.

## 설계 결정

- 위치: `app/models/order.py`
- 클래스명: `Order`
- 생성자 인자 및 속성명 (PRD 6장 "주문(Order)" 필드 매핑):
  - `id` — 주문번호 (예: "ORD-20260416-0043")
  - `sample_id` — 시료 ID (주문 대상 시료)
  - `customer_name` — 고객명
  - `quantity` — 주문 수량 (ea)
  - `status` — 주문 상태 (RESERVED / REJECTED / PRODUCING / CONFIRMED / RELEASE, PRD 4장)
- `id` 속성은 주문번호 값을 그대로 담는다 (Sample의 `id`와 동일한 패턴, doc-consistency-verify 검토 결과 반영 —
  `data_persistence`의 레코드 `id` 필드와 자연스럽게 대응시키기 위함).
- 주문번호 채번(ORD-YYYYMMDD-NNNN 형식 생성) 로직은 이번 사이클 범위가 아니다. Order는 순수 데이터 홀더로,
  주문번호는 생성자 인자로 그대로 받는다. 채번 책임은 이후 Controller(4단계, 시료 주문)에서 담당한다.
- data_persistence 연동은 이번 사이클 범위 밖 (다음 사이클에서 진행).

## 테스트

- 파일: `tests/test_order_model.py`
- 테스트 이름: `test_order_stores_all_field_values`
- 검증 내용: `Order(id="ORD-20260416-0043", sample_id="S-001", customer_name="홍길동", quantity=20,
  status="RESERVED")`로 생성한 인스턴스의 `id`, `sample_id`, `customer_name`, `quantity`, `status` 속성이 각각
  생성 시 전달한 값과 동일한지 확인한다.
- mock 없이 실제 `Order` 클래스를 import하여 검증한다.

## 예상되는 최소 구현 방향 (GREEN 단계 참고용)

`app/models/order.py`에 `Order` 클래스를 정의하고, 생성자에서 받은 값을 각각 동일한 이름의 속성에 저장한다.
그 외 메서드(채번, 상태 전이 검증 등)나 검증 로직은 이번 사이클에서 추가하지 않는다.
