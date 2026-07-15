# PLAN.md (이번 사이클 RED 단계)

대상 로드맵: `docs/PLAN.md` 9단계 "메인 메뉴 연결" 중 여섯 번째 항목 — 모니터링 콘솔 메뉴 연결
(PRD 5.1 메인 메뉴 중 "모니터링", 5.7).

## 이번에 구현할 동작 (1가지)

모니터링 콘솔 메뉴에서 "1"(상태별 주문 현황)을 선택하면 `RESERVED`/`CONFIRMED`/`PRODUCING`/`RELEASE`
각 상태별 주문 건수가 출력되고, "2"(시료별 재고 현황)를 선택하면 각 시료의 재고/수요/상태(여유·부족·
고갈)가 출력되며, "3"(이전 메뉴로)을 선택하면 메뉴 루프가 종료된다.

## 설계 결정

- 위치: `app/views/monitoring_view.py`, 함수명 `run_monitoring_menu(monitoring_controller) -> None`
  - 콘솔 루프: 메뉴("1. 상태별 주문 현황", "2. 시료별 재고 현황", "3. 이전 메뉴로")를 출력하고
    `input("선택: ")`으로 선택지를 받는다.
  - `"1"`: `monitoring_controller.order_status_counts()`를 호출한다. 반환된 dict를 순회하며 각 상태를
    `f"{status}: {count}건"` 형식으로 한 줄씩 출력한다 (`REJECTED`는 dict에 키가 없으므로 자연히
    출력되지 않는다, PRD 5.7 "REJECTED는 집계에서 제외").
  - `"2"`: `monitoring_controller.sample_stock_status()`를 호출한다. 결과가 없으면 "등록된 시료가
    없습니다." 출력. 아니면 각 항목을 `f"{entry['sample'].id} | {entry['sample'].name} | 재고
    {entry['sample'].stock} | 수요 {entry['demand']} | {entry['status']}"` 형식으로 한 줄씩
    출력한다.
  - `"3"`: `return`으로 루프를 종료한다.
  - 그 외 입력: "잘못된 입력입니다." 출력 후 루프 계속.
  - `monitoring_controller`는 외부에서 주입받는다.
- 메인 메뉴 루프 연결은 이번 사이클 범위 밖 (마지막 사이클에서 진행) — 이 사이클을 끝으로 9단계의
  개별 메뉴 구현이 모두 끝나고, 다음 사이클에서 `main.py`가 이 메뉴들을 하나로 묶는다.

## 테스트

- 파일: `tests/test_monitoring_view.py` (신규)
- 테스트 이름: `test_run_monitoring_menu_shows_order_status_counts_and_sample_stock_status`
- 검증 내용:
  - `tmp_path` fixture로 임시 `orders.json`, `samples.json` 경로를 만들고, 실제 `OrderRepository`,
    `SampleRepository`, `OrderController`, `MonitoringController`를 생성한다 (mock 없음).
  - 재고 20인 시료(`S-001`)를 저장하고, `order_controller.place_order`로 수량 5인 주문 하나를
    접수해 `RESERVED` 상태로 남긴다 (재고 20 ≥ 수요 5이므로 시료 상태는 "여유"가 되어야 함).
  - `monkeypatch.setattr("builtins.input", ...)`로 다음 값을 순서대로 반환하도록 스텁한다: `"1"`
    (상태별 현황), `"2"`(재고 현황), `"3"`(종료).
  - `run_monitoring_menu(monitoring_controller)`를 호출한다.
  - `capsys.readouterr().out`으로 표준출력을 캡처해, `"RESERVED: 1건"`이 포함되고, `"CONFIRMED:
    0건"`이 포함되며, 시료 재고 현황 출력에 `"S-001"`과 `"여유"`가 모두 포함되는지 확인한다.
- mock 없이 실제 `OrderController`, `MonitoringController`, `OrderRepository`, `SampleRepository`,
  `Order`, `Sample`, 실제 파일 시스템(`tmp_path`)을 사용하고, 콘솔 입력만 `monkeypatch`로 스텁한다.

## 예상되는 최소 구현 방향 (GREEN 단계 참고용)

`app/views/monitoring_view.py`에 `run_monitoring_menu(monitoring_controller)` 함수를 정의한다.
`while True` 루프에서 메뉴를 출력하고 `"1"`이면 `order_status_counts()` 결과를 `"{status}:
{count}건"` 형식으로 순회 출력, `"2"`면 `sample_stock_status()` 결과를 시료별로 출력(빈 결과는 안내
메시지), `"3"`이면 `return`으로 종료한다. 메인 메뉴 연결은 이번 사이클에서 추가하지 않는다.
