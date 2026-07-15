# PLAN.md (이번 사이클 RED 단계)

대상 로드맵: `docs/PLAN.md` 9단계 "메인 메뉴 연결" 중 네 번째 항목 — 생산 라인 조회 콘솔 메뉴 연결
(PRD 5.1 메인 메뉴 중 "생산 라인 조회", 5.5).

## 이번에 구현할 동작 (1가지)

생산 라인 콘솔 메뉴에서 "1"(현재 생산 현황)을 선택하면 현재 생산 중인 주문의 부족분/실생산량/
총생산시간이 출력되고, "2"(생산 대기열 조회)를 선택하면 대기 중인 주문 목록이 출력되며, "3"(생산
완료 처리)을 선택하면 현재 생산 중인 주문이 완료 처리되어(CONFIRMED 전환) 결과가 출력되고, "4"(이전
메뉴로)를 선택하면 메뉴 루프가 종료된다.

## 설계 결정

- 위치: `app/views/production_view.py`, 함수명 `run_production_menu(production_line_controller) ->
  None`
  - 콘솔 루프: 메뉴("1. 현재 생산 현황", "2. 생산 대기열 조회", "3. 생산 완료 처리", "4. 이전
    메뉴로")를 출력하고 `input("선택: ")`으로 선택지를 받는다.
  - `"1"`: `production_line_controller.current_production()`을 호출한다. `None`이면 "현재 생산 중인
    시료가 없습니다." 출력. 아니면 `f"{result['order'].id} | 부족분 {result['shortfall']} |
    실생산량 {result['actual_production']} | 총생산시간 {result['total_production_time']}"` 형식으로
    출력한다.
  - `"2"`: `production_line_controller.waiting_orders()`를 호출한다. 결과가 없으면 "대기 중인 생산이
    없습니다." 출력. 아니면 각 주문을 `f"{o.id} | {o.sample_id} | {o.quantity}"` 형식으로 한 줄씩
    출력한다.
  - `"3"`: `production_line_controller.complete_current_production()`을 호출한다. `None`이면 "완료할
    생산이 없습니다." 출력. 아니면 `f"생산 완료 처리: {order.id} ({order.status})"` 형식으로 출력한다
    (`status`는 항상 `CONFIRMED`).
  - `"4"`: `return`으로 루프를 종료한다.
  - 그 외 입력: "잘못된 입력입니다." 출력 후 루프 계속.
  - `production_line_controller`는 외부에서 주입받는다.
- 메인 메뉴 루프 연결, 출고/모니터링 메뉴는 이번 사이클 범위 밖 (다음 사이클들에서 진행).

## 테스트

- 파일: `tests/test_production_view.py` (신규)
- 테스트 이름: `test_run_production_menu_shows_current_production_waiting_orders_and_completes`
- 검증 내용:
  - `tmp_path` fixture로 임시 `orders.json`, `samples.json` 경로를 만들고, 실제 `OrderRepository`,
    `SampleRepository`, `OrderController`, `ProductionLineController`를 생성한다 (mock 없음).
  - 재고 부족한 시료(`S-001`, stock=5, yield_rate=0.9, avg_production_time=30)를 저장한다.
  - `order_controller.place_order`로 수량 20인 주문 두 건을 접수하고 각각 `approve_order`로 승인해
    둘 다 `PRODUCING` 상태로 만든다 (재고 5 < 수량 20이므로 둘 다 생산 큐에 등록됨). 첫 번째 주문이
    id 순으로 "현재 생산 중", 두 번째가 "대기 중"이 된다.
  - `monkeypatch.setattr("builtins.input", ...)`로 다음 값을 순서대로 반환하도록 스텁한다: `"1"`
    (현재 생산 현황), `"2"`(대기열 조회), `"3"`(완료 처리), `"4"`(종료).
  - `run_production_menu(production_line_controller)`를 호출한다.
  - `capsys.readouterr().out`으로 표준출력을 캡처해 다음을 확인한다:
    - 현재 생산 현황 출력에 첫 번째 주문의 id와 부족분(`15`), 실생산량(`math.ceil(15/0.9)=17`)이
      포함된다.
    - 대기열 출력에 두 번째 주문의 id가 포함된다 (첫 번째 주문 id는 대기열에 없어야 하므로, 두
      주문의 id가 서로 다른 시점의 출력 블록에 나오는지까지는 문자열 포함 여부로만 검증하고 엄격한
      섹션 분리는 요구하지 않는다 — 콘솔 출력 특성상 순서로 구분).
    - 완료 처리 출력에 첫 번째 주문의 id와 `"CONFIRMED"`가 포함된다.
- mock 없이 실제 `OrderController`, `ProductionLineController`, `OrderRepository`,
  `SampleRepository`, `Order`, `Sample`, 실제 파일 시스템(`tmp_path`)을 사용하고, 콘솔 입력만
  `monkeypatch`로 스텁한다.

## 예상되는 최소 구현 방향 (GREEN 단계 참고용)

`app/views/production_view.py`에 `run_production_menu(production_line_controller)` 함수를 정의한다.
`while True` 루프에서 메뉴를 출력하고 `"1"`/`"2"`/`"3"`에 따라 각각 `current_production`/
`waiting_orders`/`complete_current_production`을 호출해 결과를 출력하며(빈 결과는 안내 메시지),
`"4"`면 `return`으로 종료한다. 메인 메뉴 연결, 다른 메뉴는 이번 사이클에서 추가하지 않는다.
