# PLAN.md (이번 사이클 RED 단계)

대상 로드맵: `docs/PLAN.md` 9단계 "메인 메뉴 연결" 중 다섯 번째 항목 — 출고 처리 콘솔 메뉴 연결
(PRD 5.1 메인 메뉴 중 "출고 처리", 5.6).

## 이번에 구현할 동작 (1가지)

출고 처리 콘솔 메뉴에서 "1"(`CONFIRMED` 주문 목록 조회)을 선택하면 `CONFIRMED` 주문 목록이 출력되고,
"2"(출고 처리)를 선택해 주문번호를 입력하면 해당 주문이 `RELEASE`로 전환되어 결과가 출력되며,
"3"(이전 메뉴로)을 선택하면 메뉴 루프가 종료된다.

## 설계 결정

- 위치: `app/views/order_view.py` (기존 파일 확장 — 주문 관련 메뉴는 한 파일에 모은다는 기존 방침
  유지).
- 함수명: `run_release_menu(order_controller) -> None`
  - 콘솔 루프: 메뉴("1. CONFIRMED 주문 목록 조회", "2. 출고 처리", "3. 이전 메뉴로")를 출력하고
    `input("선택: ")`으로 선택지를 받는다.
  - `"1"`: `order_controller.list_confirmed_orders()`를 호출해 각 주문을
    `f"{o.id} | {o.sample_id} | {o.customer_name} | {o.quantity}"` 형식으로 출력한다 (승인/거절
    메뉴의 목록 출력과 동일한 포맷). 결과가 없으면 "출고 대기 중인 주문이 없습니다." 출력.
  - `"2"`: `input()`으로 주문번호를 받아 `order_controller.release_order(order_id)`를 호출하고,
    `f"출고 처리 완료: {order.id} ({order.status})"` 형식으로 출력한다 (`status`는 항상 `RELEASE`).
  - `"3"`: `return`으로 루프를 종료한다.
  - 그 외 입력: "잘못된 입력입니다." 출력 후 루프 계속.
  - `order_controller`는 외부에서 주입받는다 (기존 `run_order_menu`/`run_order_approval_menu`와 동일한
    방식).
- 메인 메뉴 루프 연결, 모니터링 메뉴는 이번 사이클 범위 밖 (다음 사이클들에서 진행).

## 테스트

- 파일: `tests/test_order_view.py`에 테스트를 추가한다 (기존 파일 확장).
- 테스트 이름: `test_run_release_menu_lists_confirmed_orders_and_releases_order`
- 검증 내용:
  - `tmp_path` fixture로 임시 `orders.json`, `samples.json` 경로를 만들고, 실제 `OrderRepository`,
    `SampleRepository`, `OrderController`를 생성한다 (mock 없음). 재고 충분한 시료(`S-001`,
    stock=50)를 저장한다.
  - `order_controller.place_order`와 `order_controller.approve_order`를 직접 호출해(View를 거치지
    않고) 주문을 하나 접수·승인해 `CONFIRMED` 상태로 미리 만들어 둔다.
  - `monkeypatch.setattr("builtins.input", ...)`로 다음 값을 순서대로 반환하도록 스텁한다: `"1"`
    (목록 조회), `"2"`(출고 처리 선택), 해당 주문의 id, `"3"`(종료).
  - `run_release_menu(order_controller)`를 호출한다.
  - `capsys.readouterr().out`으로 표준출력을 캡처해, 목록 조회 출력과 출고 처리 출력 모두에 해당
    주문의 id가 포함되고, 출고 처리 출력에 `"RELEASE"`가 포함되는지 확인한다.
- mock 없이 실제 `OrderController`, `OrderRepository`, `SampleRepository`, `Order`, `Sample`, 실제
  파일 시스템(`tmp_path`)을 사용하고, 콘솔 입력만 `monkeypatch`로 스텁한다.

## 예상되는 최소 구현 방향 (GREEN 단계 참고용)

`app/views/order_view.py`에 `run_release_menu(order_controller)` 함수를 추가한다. `while True`
루프에서 메뉴를 출력하고 `"1"`이면 `list_confirmed_orders()` 결과를 출력, `"2"`면 주문번호를 입력받아
`release_order`를 호출해 결과 출력, `"3"`이면 `return`으로 종료한다. 메인 메뉴 연결, 모니터링 메뉴는
이번 사이클에서 추가하지 않는다.
