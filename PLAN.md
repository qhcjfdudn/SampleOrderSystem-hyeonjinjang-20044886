# PLAN.md (이번 사이클 RED 단계)

대상 로드맵: `docs/PLAN.md` 8단계 "모니터링" 중 두 번째 항목 — 시료별 재고 현황 및 여유/부족/고갈
상태 표시 (PRD 5.7 "재고량 확인"). 8단계 마지막 항목이다.

## 이번에 구현할 동작 (1가지)

등록된 시료들에 대해 `MonitoringController.sample_stock_status`를 호출하면, 각 시료마다 미완료
주문(`RESERVED`+`PRODUCING`) 수량 합계를 "수요"로 계산해 현재 재고와 비교한 뒤, 재고 0이면 `"고갈"`,
재고가 수요보다 적으면 `"부족"`, 그 외에는 `"여유"`로 판정한 결과를 시료별로 반환한다.

## 설계 결정

- (사용자와 합의된 판정 기준)
  - 시료별 수요 = 그 시료를 대상으로 하는 주문 중 `status`가 `RESERVED` 또는 `PRODUCING`인 주문의
    `quantity` 합계. `CONFIRMED`/`RELEASE`는 이미 재고에서 차감이 끝났거나 출고 완료된 상태라 수요에
    포함하지 않고, `REJECTED`는 유효한 주문이 아니므로 포함하지 않는다.
  - 판정 순서: `sample.stock == 0`이면 무조건 `"고갈"` (수요와 무관하게 재고 자체가 0인 상태를
    최우선으로 판정). 그 다음 `sample.stock < demand`이면 `"부족"`. 그 외(재고가 0보다 크고 수요
    이상인 경우, 수요가 0인 경우 포함)에는 `"여유"`.
- `app/controllers/monitoring_controller.py`의 `MonitoringController`에
  `sample_stock_status() -> list[dict]` 메서드를 추가한다.
  - `self.order_repository.find_all()`로 전체 주문을 조회해, `status`가 `RESERVED` 또는 `PRODUCING`인
    주문만 `sample_id`별로 `quantity`를 합산한 dict(`demand_by_sample`)를 만든다.
  - `self.sample_repository.find_all()`로 전체 시료를 조회한다.
  - 각 시료에 대해 `demand = demand_by_sample.get(sample.id, 0)`를 구하고, 위 판정 순서대로
    `status` 문자열(`"고갈"`/`"부족"`/`"여유"`)을 계산한다.
  - 각 시료마다 `{"sample": sample, "demand": demand, "status": status}` 형태의 dict를 만들어
    리스트로 반환한다 (PRD 5.7 "표기 정보 수준은 구현 시 자율적으로 결정"에 준해, 6단계
    `current_production`과 동일하게 dict 리스트로 단순화).
  - 시료가 하나도 없으면 빈 리스트를 반환한다.
- `OrderRepository`, `SampleRepository`, `Order`, `Sample`은 변경하지 않는다.
- 콘솔 입출력(View)은 이번 사이클 범위 밖. 이 사이클을 끝으로 8단계(모니터링)가 모두 구현된다.

## 테스트

- 파일: `tests/test_monitoring_controller.py`에 테스트를 추가한다 (기존 파일 확장).
- 테스트 이름: `test_sample_stock_status_classifies_samples_as_abundant_short_or_depleted`
- 검증 내용:
  - `tmp_path` fixture로 임시 `orders.json`, `samples.json` 경로를 만들고, 실제 `OrderRepository`,
    `SampleRepository`, `OrderController`, `MonitoringController`를 생성한다 (mock 없음).
  - 시료 3건을 저장한다:
    - `S-001` (재고 20): `RESERVED` 주문 수량 5건만 있어 수요(5) ≤ 재고(20) → `"여유"` 기대.
    - `S-002` (재고 5): `PRODUCING` 주문 수량 20건이 있어 수요(20) > 재고(5) → `"부족"` 기대.
    - `S-003` (재고 0): 주문이 전혀 없어도 재고가 0이므로 → `"고갈"` 기대.
  - `S-001`에 대해 `order_controller.place_order`로 수량 5인 주문을 접수한다 (`RESERVED` 유지).
  - `S-002`에 대해 `order_controller.place_order`로 수량 20인 주문을 접수하고 `approve_order`로
    승인해 `PRODUCING`으로 만든다 (재고 5 < 수량 20).
  - `monitoring_controller.sample_stock_status()`를 호출한 결과를 시료 id로 인덱싱한 뒤, 각각의
    `status`가 기대한 값(`S-001` → `"여유"`, `S-002` → `"부족"`, `S-003` → `"고갈"`)과 일치하는지
    확인한다.
- mock 없이 실제 `OrderController`, `MonitoringController`, `OrderRepository`, `SampleRepository`,
  `Order`, `Sample`, 실제 파일 시스템(`tmp_path`)을 사용하여 검증한다.

## 예상되는 최소 구현 방향 (GREEN 단계 참고용)

`MonitoringController.sample_stock_status`는 `order_repository.find_all()`에서
`RESERVED`/`PRODUCING` 주문만 걸러 `sample_id`별 `quantity` 합계 dict를 만든 뒤,
`sample_repository.find_all()`의 각 시료에 대해 `stock == 0`이면 `"고갈"`, `stock < demand`이면
`"부족"`, 그 외는 `"여유"`로 판정해 `{"sample":, "demand":, "status":}` 리스트를 반환한다. View 연동은
이번 사이클에서 추가하지 않는다 — 이것으로 8단계가 완성된다.
