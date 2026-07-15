# PLAN.md (이번 사이클 RED 단계)

대상 로드맵: `docs/PLAN.md` 9단계 "메인 메뉴 연결" 중 마지막 항목 — `main.py`에서 메인 메뉴 루프
연결 (PRD 5.1). 9단계 전체의 마지막 사이클이다.

## 이번에 구현할 동작 (1가지)

`main()`을 실행하면 시료/주문 저장소와 4개 Controller가 생성되고, 메인 메뉴 루프가 매 반복마다 요약
정보(등록 시료 수/총 재고/전체 주문 건수/생산라인 대기 건수)와 6개 기능 메뉴("1. 시료 관리" ~
"6. 모니터링") + "7. 종료"를 출력한다. 1~6을 선택하면 해당 기능의 콘솔 메뉴 함수가 호출되고(그
메뉴에서 뒤로가기하면 메인 메뉴로 돌아옴), "7"을 선택하면 `main()`이 종료된다.

## 설계 결정

- `main.py`에서 다음을 조립한다:
  - `sample_repository = SampleRepository(Config.SAMPLES_FILE)`
  - `order_repository = OrderRepository(Config.ORDERS_FILE)`
  - `sample_controller = SampleController(sample_repository)`
  - `order_controller = OrderController(order_repository, sample_repository)`
  - `production_line_controller = ProductionLineController(order_repository, sample_repository)`
  - `monitoring_controller = MonitoringController(order_repository, sample_repository)`
  - (Repository/Controller 생성 시점에 `Config`의 클래스 속성을 그대로 사용 — 인스턴스화하지 않음,
    현재 `Config`가 상수 컨테이너로만 쓰이고 있는 기존 관례를 따른다.)
- 요약 정보 계산 (매 루프 반복마다 최신값으로 다시 계산):
  - 등록 시료 수 = `len(sample_controller.list_samples())`
  - 총 재고 = 등록된 각 시료의 `stock` 합계
  - 전체 주문 건수 = `len(order_repository.find_all())` (상태 무관 전체 건수, PRD 5.1 "전체 주문
    건수"는 상태 필터를 언급하지 않으므로 전체로 해석)
  - 생산라인 대기 건수 = `monitoring_controller.order_status_counts()["PRODUCING"]` (현재 생산 중 +
    대기 중을 합친 전체 `PRODUCING` 건수 — "생산 라인에 걸려 있는 건수"로 해석, 6단계에서 이미 검증된
    집계 재사용)
  - 한 줄로 출력: `f"등록 시료 수: {n} | 총 재고: {stock} | 전체 주문 건수: {orders} | 생산라인 대기
    건수: {producing}"`
- 메뉴 출력: "1. 시료 관리", "2. 시료 주문", "3. 주문 승인/거절", "4. 생산 라인 조회", "5. 출고
  처리", "6. 모니터링", "7. 종료" (PRD 5.1 메인 메뉴 표 순서 그대로).
- `input("선택: ")`으로 받은 값에 따라 각각 `run_sample_menu(sample_controller)`,
  `run_order_menu(order_controller)`, `run_order_approval_menu(order_controller)`,
  `run_production_menu(production_line_controller)`, `run_release_menu(order_controller)`,
  `run_monitoring_menu(monitoring_controller)`를 호출한다 (모두 기존에 구현·검증된 함수, 그대로
  재사용). `"7"`이면 `return`으로 `main()`을 종료한다. 그 외 입력은 "잘못된 입력입니다." 출력 후
  루프 계속.
- 이 사이클로 9단계(메인 메뉴 연결) 전체가 완성된다.

## 테스트

- 파일: `tests/test_main.py` (신규)
- 테스트 이름: `test_main_shows_summary_and_routes_to_sample_menu_before_exit`
- 검증 내용:
  - `monkeypatch.setattr(Config, "SAMPLES_FILE", str(tmp_path / "samples.json"))`,
    `monkeypatch.setattr(Config, "ORDERS_FILE", str(tmp_path / "orders.json"))`로 데이터 파일 경로를
    임시 디렉터리로 바꾼다 (`main()`이 직접 `Config` 속성을 읽으므로, 이렇게 하면 실제 파일 시스템에
    영향을 주지 않고 테스트할 수 있다 — mock이 아니라 진짜 파일 I/O가 임시 경로에서 일어난다).
  - `monkeypatch.setattr("builtins.input", ...)`로 다음 시나리오를 시뮬레이션한다: 메인 메뉴에서
    `"1"`(시료 관리 진입) → 시료 관리 메뉴에서 `"1"`(등록), `"S-001"`, `"실리콘 웨이퍼-8인치"`,
    `"30"`, `"0.9"` → 시료 관리 메뉴에서 `"4"`(메인 메뉴로 복귀) → 메인 메뉴에서 `"7"`(종료).
  - `main()`을 호출한다 (`from main import main`).
  - `capsys.readouterr().out`으로 표준출력을 캡처해, 첫 루프에서 "등록 시료 수: 0"이 포함된 요약
    줄이 출력되고, "1. 시료 관리"부터 "7. 종료"까지 메뉴 문구가 모두 포함되며, 시료 등록 확인
    메시지에 `"S-001"`이 포함되는지 확인한다.
- mock 없이 실제 `SampleRepository`, `OrderRepository`, 4개 Controller, 실제 파일 시스템
  (`tmp_path`, `Config` 속성 monkeypatch로 리다이렉션)을 사용하고, 콘솔 입력만 `monkeypatch`로
  스텁한다.

## 예상되는 최소 구현 방향 (GREEN 단계 참고용)

`main.py`에서 `Config`, 4개 Repository/Controller, `app/views/*`의 6개 메뉴 함수를 import한다.
`main()` 안에서 Repository/Controller를 조립하고, `while True` 루프에서 요약 정보를 계산해 출력한
뒤 메뉴를 표시하고, 선택지에 따라 해당 메뉴 함수를 호출하거나(`"1"`~`"6"`) `"7"`이면 `return`으로
종료한다. `if __name__ == "__main__": main()`은 그대로 유지한다.
