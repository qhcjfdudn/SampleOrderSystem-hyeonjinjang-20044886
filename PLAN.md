# PLAN.md (이번 사이클 RED 단계)

대상 로드맵: `docs/PLAN.md` 2단계 "데이터 계층 (Model)" 중 세 번째 항목 — 주문(Order) 데이터의
`data_persistence` 연동 (Sample 부분은 이전 사이클에서 완료, 이번 사이클은 Order 부분).

## 이번에 구현할 동작 (1가지)

`OrderRepository`로 `Order`를 저장(save)하면, 같은 id로 다시 조회했을 때(find_by_id) 저장한 주문과
동일한 필드 값을 가진 `Order`를 반환한다.

## 설계 결정

- 위치: `app/models/order_repository.py`
- 클래스명: `OrderRepository`
- 생성자: `OrderRepository(file_path)` — `data_persistence.DataPersistence(file_path)`를 내부에서
  생성해 `orders.json` 파일 경로를 그대로 전달받는다 (`SampleRepository`와 동일한 패턴, PRD 7장).
- 메서드:
  - `save(order: Order) -> None` — `Order` 객체를 dict로 변환해 `DataPersistence.create(record)`로
    저장한다.
  - `find_by_id(id) -> Order | None` — `DataPersistence.read(id)`로 dict를 조회한 뒤 존재하면 `Order`
    객체로 변환해 반환하고, 없으면 `None`을 반환한다.
- `Order` ↔ dict 변환: `Order`의 5개 필드(id, sample_id, customer_name, quantity, status)를 그대로
  dict의 키/값으로 매핑한다. `Order`에는 `to_dict`/`from_dict`를 추가하지 않고 `OrderRepository` 내부에서
  직접 dict를 구성/해석한다 (`SampleRepository`와 동일한 방식).
- update/delete, 목록 조회, 상태 전이 로직 등은 이번 사이클 범위 밖 (이후 5~7단계 Controller에서 담당).
- 파일 I/O는 `data_persistence.DataPersistence`에 위임하며, 직접 `open`/`json` 등을 사용하지 않는다.

## 테스트

- 파일: `tests/test_order_repository.py`
- 테스트 이름: `test_save_and_find_by_id_returns_order_with_same_field_values`
- 검증 내용:
  - `tmp_path` fixture로 임시 디렉터리에 `orders.json` 경로를 만들고, 그 경로로 `OrderRepository`를
    생성한다 (실제 파일 시스템 사용, mock 없음).
  - `Order(id="ORD-20260416-0043", sample_id="S-001", customer_name="홍길동", quantity=20,
    status="RESERVED")`를 생성해 `repository.save(order)`로 저장한다.
  - `repository.find_by_id("ORD-20260416-0043")`로 조회한 결과가 `None`이 아니며, `id`, `sample_id`,
    `customer_name`, `quantity`, `status` 속성이 저장한 주문과 각각 동일한 값인지 확인한다.
- mock 없이 실제 `OrderRepository`, `Order`, `DataPersistence`, 실제 파일 시스템(`tmp_path`)을 사용하여
  검증한다.

## 예상되는 최소 구현 방향 (GREEN 단계 참고용)

`app/models/order_repository.py`에 `OrderRepository` 클래스를 정의한다. 생성자에서
`DataPersistence(file_path)` 인스턴스를 보관하고, `save`는 `Order` 필드를 dict로 만들어 `create`를
호출하며, `find_by_id`는 `read(id)`로 얻은 dict를 `Order(**dict)`로 복원해 반환한다 (없으면 `None`).
그 외 update/delete, 목록 조회 등은 이번 사이클에서 추가하지 않는다.
