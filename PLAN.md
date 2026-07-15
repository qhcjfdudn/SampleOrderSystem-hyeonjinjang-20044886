# PLAN.md (이번 사이클 RED 단계)

대상 로드맵: `docs/PLAN.md` 9단계 "메인 메뉴 연결" 중 세 번째 항목 — 주문 승인/거절 콘솔 메뉴 연결
(PRD 5.1 메인 메뉴 중 "주문 승인/거절", 5.4).

## 이번에 구현할 동작 (1가지)

주문 승인/거절 콘솔 메뉴에서 "1"(접수된 주문 목록 조회)을 선택하면 `RESERVED` 주문 목록이 출력되고,
"2"(주문 승인)를 선택해 주문번호를 입력하면 해당 주문이 승인 처리되어 결과 상태(`CONFIRMED` 또는
`PRODUCING`)가 출력되며, "3"(주문 거절)을 선택해 주문번호를 입력하면 해당 주문이 `REJECTED`로
전환되어 출력되고, "4"(이전 메뉴로)를 선택하면 메뉴 루프가 종료된다.

## 설계 결정

- 위치: `app/views/order_view.py` (기존 파일 확장, `run_order_menu`와 같은 파일 — 둘 다 "주문" 관련
  콘솔 메뉴이므로 파일을 나누지 않는다).
- 함수명: `run_order_approval_menu(order_controller) -> None`
  - 콘솔 루프: 메뉴("1. 접수된 주문 목록 조회", "2. 주문 승인", "3. 주문 거절", "4. 이전 메뉴로")를
    출력하고 `input("선택: ")`으로 선택지를 받는다.
  - `"1"`: `order_controller.list_reserved_orders()`를 호출해 각 주문을
    `f"{o.id} | {o.sample_id} | {o.customer_name} | {o.quantity}"` 형식으로 한 줄씩 출력한다.
    결과가 없으면 "접수된 주문이 없습니다." 출력.
  - `"2"`: `input()`으로 주문번호를 받아 `order_controller.approve_order(order_id)`를 호출하고,
    반환된 주문의 `id`와 `status`를 포함한 메시지를 출력한다 (예: `f"승인 처리 완료: {order.id}
    ({order.status})"` — 재고 상황에 따라 `CONFIRMED` 또는 `PRODUCING`이 그대로 표시된다).
  - `"3"`: `input()`으로 주문번호를 받아 `order_controller.reject_order(order_id)`를 호출하고,
    반환된 주문의 `id`와 `status`(`REJECTED`)를 포함한 메시지를 출력한다.
  - `"4"`: `return`으로 루프를 종료한다.
  - 그 외 입력: "잘못된 입력입니다." 출력 후 루프 계속.
  - `order_controller`는 외부에서 주입받는다 (기존 `run_order_menu`와 동일한 방식).
- 메인 메뉴 루프 연결, 생산 라인/출고/모니터링 메뉴는 이번 사이클 범위 밖 (다음 사이클들에서 진행).

## 테스트

- 파일: `tests/test_order_view.py`에 테스트를 추가한다 (기존 파일 확장).
- 테스트 이름: `test_run_order_approval_menu_lists_approves_and_rejects_orders`
- 검증 내용:
  - `tmp_path` fixture로 임시 `orders.json`, `samples.json` 경로를 만들고, 실제 `OrderRepository`,
    `SampleRepository`, `OrderController`를 생성한다 (mock 없음). 재고 충분한 시료(`S-001`,
    stock=50)를 저장한다.
  - `order_controller.place_order`를 두 번 직접 호출해(View를 거치지 않고) 주문 A(수량 5)와 주문
    B(수량 10)를 모두 `RESERVED` 상태로 미리 접수해 둔다 (테스트 준비 단계, `_today()` monkeypatch
    불필요 — 실제 오늘 날짜로 접수해도 검증에는 영향 없음, 생성된 `order.id`를 그대로 사용).
  - `monkeypatch.setattr("builtins.input", ...)`로 다음 값을 순서대로 반환하도록 스텁한다:
    `"1"`(목록 조회), `"2"`(승인 선택), 주문 A의 id, `"3"`(거절 선택), 주문 B의 id, `"4"`(종료).
  - `run_order_approval_menu(order_controller)`를 호출한다.
  - `capsys.readouterr().out`으로 표준출력을 캡처해, 목록 조회 출력에 주문 A와 B의 id가 모두 포함
    되고, 승인 처리 메시지에 주문 A의 id와 `"CONFIRMED"`가 포함되며, 거절 처리 메시지에 주문 B의
    id와 `"REJECTED"`가 포함되는지 확인한다.
- mock 없이 실제 `OrderController`, `OrderRepository`, `SampleRepository`, `Order`, `Sample`, 실제
  파일 시스템(`tmp_path`)을 사용하고, 콘솔 입력만 `monkeypatch`로 스텁한다.

## 예상되는 최소 구현 방향 (GREEN 단계 참고용)

`app/views/order_view.py`에 `run_order_approval_menu(order_controller)` 함수를 추가한다. `while
True` 루프에서 메뉴를 출력하고 `"1"`이면 `list_reserved_orders()` 결과를 출력, `"2"`면 주문번호를
입력받아 `approve_order`를 호출해 결과 출력, `"3"`이면 `reject_order`를 호출해 결과 출력, `"4"`면
`return`으로 종료한다. 메인 메뉴 연결, 다른 메뉴는 이번 사이클에서 추가하지 않는다.
