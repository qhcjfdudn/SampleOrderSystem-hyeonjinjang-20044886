# PLAN.md (이번 사이클 RED 단계)

대상 로드맵: `docs/PLAN.md` 9단계 "메인 메뉴 연결" 중 두 번째 항목 — 시료 주문 콘솔 메뉴 연결
(PRD 5.1 메인 메뉴 중 "시료 주문", 5.3).

## 이번에 구현할 동작 (1가지)

시료 주문 콘솔 메뉴에서 사용자가 "1"(주문 접수)을 선택해 시료 ID/고객명/주문 수량을 입력하면
`RESERVED` 상태의 주문이 접수되어 주문번호가 화면에 출력되고, "2"(이전 메뉴로)를 선택하면 메뉴
루프가 종료된다.

## 설계 결정

- 위치: `app/views/order_view.py`, 함수명 `run_order_menu(order_controller) -> None`
  - `OrderController.place_order(sample_id, customer_name, quantity, order_date)`는 예약 접수 시점의
    날짜(`order_date`)를 인자로 요구하지만, PRD 5.3의 "예약 시 입력 값"은 시료 ID/고객명/주문 수량
    3가지뿐이고 날짜는 사용자 입력 항목이 아니다 — 즉 View가 현재 날짜를 자동으로 채워 넣어야 한다.
  - 날짜 조회를 테스트 가능하게 만들기 위해 모듈 레벨 함수 `_today()`를 둔다:
    ```python
    from datetime import date

    def _today():
        return date.today()
    ```
    `run_order_menu`는 `date.today()`를 직접 호출하지 않고 `_today()`를 호출한다. 테스트에서는
    `monkeypatch.setattr("app.views.order_view._today", lambda: date(2026, 4, 16))`로 고정된 날짜를
    주입해 결정론적으로 검증한다 (실제 실행 시에는 `_today()`가 진짜 오늘 날짜를 반환).
  - 콘솔 루프: 메뉴("1. 시료 주문 접수", "2. 이전 메뉴로")를 출력하고 `input("선택: ")`으로 선택지를
    받는다.
  - `"1"`: `input()`으로 시료 ID, 고객명, 주문 수량(정수 변환)을 순서대로 받아
    `order_controller.place_order(sample_id, customer_name, int(quantity), _today())`를 호출하고,
    생성된 주문의 `id`와 `status`를 포함한 확인 메시지를 출력한다 (예: `f"주문 접수 완료:
    {order.id} ({order.status})"`).
  - `"2"`: `return`으로 루프를 종료한다.
  - 그 외 입력: "잘못된 입력입니다." 출력 후 루프 계속.
  - `order_controller`는 외부에서 주입받는다 (View가 Repository를 직접 생성하지 않음).
- 메인 메뉴 루프 연결, 주문 승인/거절 메뉴는 이번 사이클 범위 밖 (다음 사이클들에서 진행).

## 테스트

- 파일: `tests/test_order_view.py` (신규)
- 테스트 이름: `test_run_order_menu_places_order_and_shows_confirmation`
- 검증 내용:
  - `tmp_path` fixture로 임시 `orders.json`, `samples.json` 경로를 만들고, 실제 `OrderRepository`,
    `SampleRepository`, `OrderController`를 생성한다 (mock 없음). 재고 충분한 시료(`S-001`,
    stock=50)를 저장한다.
  - `monkeypatch.setattr("app.views.order_view._today", lambda: date(2026, 4, 16))`로 날짜를
    고정한다.
  - `monkeypatch.setattr("builtins.input", ...)`로 다음 값을 순서대로 반환하도록 스텁한다:
    `"1"`(주문 접수 선택), `"S-001"`, `"홍길동"`, `"5"`, `"2"`(종료).
  - `run_order_menu(order_controller)`를 호출한다.
  - `capsys.readouterr().out`으로 표준출력을 캡처해, 생성된 주문번호(`"ORD-20260416-0001"`)와
    상태(`"RESERVED"`)가 모두 출력에 포함되는지 확인한다.
- mock 없이 실제 `OrderController`, `OrderRepository`, `SampleRepository`, `Order`, `Sample`, 실제
  파일 시스템(`tmp_path`)을 사용하고, 콘솔 입력과 날짜 조회만 `monkeypatch`로 스텁한다.

## 예상되는 최소 구현 방향 (GREEN 단계 참고용)

`app/views/order_view.py`에 `_today()` 헬퍼와 `run_order_menu(order_controller)` 함수를 정의한다.
`while True` 루프에서 메뉴를 출력하고 `"1"`이면 시료 ID/고객명/수량을 입력받아
`order_controller.place_order(...)`를 호출한 뒤 주문번호/상태를 출력하고, `"2"`면 `return`으로
종료한다. 승인/거절 메뉴, 메인 메뉴 연결은 이번 사이클에서 추가하지 않는다.
