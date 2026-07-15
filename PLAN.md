# PLAN.md (이번 사이클 RED 단계)

대상 로드맵: `docs/PLAN.md` 8단계 "모니터링" 중 첫 번째 항목 — 상태별 주문 현황 집계 (PRD 5.7
"주문량 확인").

## 이번에 구현할 동작 (1가지)

여러 상태(`RESERVED`/`CONFIRMED`/`PRODUCING`/`RELEASE`/`REJECTED`)의 주문이 섞여 있을 때
`MonitoringController.order_status_counts`를 호출하면, `REJECTED`를 제외한 4개 상태 각각의 주문
건수를 dict로 반환한다.

## 설계 결정

- 위치: `app/controllers/monitoring_controller.py`, 클래스명 `MonitoringController`
- 생성자: `MonitoringController(order_repository, sample_repository)` — 두 저장소를 주입받는다
  (다음 사이클의 재고 상태 판정에 `sample_repository`가 필요하므로 미리 주입 구조를 만든다, 이번
  사이클에서는 사용하지 않음).
- 메서드: `order_status_counts() -> dict`
  - `self.order_repository.find_all()`로 전체 주문을 조회한다.
  - `{"RESERVED": 0, "CONFIRMED": 0, "PRODUCING": 0, "RELEASE": 0}`로 초기화한 dict에 각 주문의
    `status`별 개수를 누적한다.
  - `REJECTED` 상태 주문은 집계에서 완전히 제외한다 (PRD 4장 "REJECTED는 정상 흐름 밖의 상태로,
    모니터링 집계에서 제외", CLAUDE.md 동일 서술).
  - 반환값의 키는 4개(`RESERVED`, `CONFIRMED`, `PRODUCING`, `RELEASE`)로 고정하며, 해당 상태 주문이
    0건이어도 키 자체는 존재하고 값이 0이다 (View가 항상 4개 항목을 표시할 수 있도록).
- `OrderRepository`, `Order`는 변경하지 않는다.
- 재고 상태(여유/부족/고갈) 판정은 이번 사이클 범위 밖 (다음 사이클에서 진행, 사용자와 합의된 기준:
  시료별 `RESERVED`+`PRODUCING` 상태 주문 수량 합계를 "미완료 수요"로 보고 현재 재고와 비교).
- 콘솔 입출력(View)은 이번 사이클 범위 밖.

## 테스트

- 파일: `tests/test_monitoring_controller.py` (신규)
- 테스트 이름: `test_order_status_counts_excludes_rejected_and_counts_each_status`
- 검증 내용:
  - `tmp_path` fixture로 임시 `orders.json`, `samples.json` 경로를 만들고, 실제 `OrderRepository`,
    `SampleRepository`, `OrderController`, `MonitoringController`를 생성한다 (mock 없음).
  - 재고 충분한 시료(`S-001`, stock=100)를 저장한다.
  - 다음과 같이 주문 5건을 만든다 (모두 `order_controller.place_order`로 접수한 뒤 상태 전이):
    - 주문 A: 접수만 함 (`RESERVED` 유지)
    - 주문 B: `approve_order` → 재고 충분이라 `CONFIRMED`
    - 주문 C: `approve_order` 후 `release_order` → `RELEASE`
    - 주문 D: `reject_order` → `REJECTED` (집계에서 제외되어야 함)
    - 주문 E: 재고가 부족한 다른 시료(`S-002`, stock=1)에 큰 수량으로 주문 후 `approve_order` →
      `PRODUCING`
  - `monitoring_controller.order_status_counts()`를 호출한 결과가
    `{"RESERVED": 1, "CONFIRMED": 1, "PRODUCING": 1, "RELEASE": 1}`과 같은지 확인한다 (딕셔너리 비교,
    `REJECTED` 키는 존재하지 않아야 함).
- mock 없이 실제 `OrderController`, `MonitoringController`, `OrderRepository`, `SampleRepository`,
  `Order`, `Sample`, 실제 파일 시스템(`tmp_path`)을 사용하여 검증한다.

## 예상되는 최소 구현 방향 (GREEN 단계 참고용)

`app/controllers/monitoring_controller.py`에 `MonitoringController` 클래스를 정의한다. 생성자에서
`order_repository`, `sample_repository`를 보관하고, `order_status_counts`는 4개 상태로 초기화한
dict를 만든 뒤 `order_repository.find_all()`을 순회하며 `status`가 그 4개 중 하나일 때만 카운트를
누적해 반환한다 (`REJECTED`나 그 외 값은 무시). 재고 상태 판정, View 연동은 이번 사이클에서 추가하지
않는다.
