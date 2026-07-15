# PLAN.md (이번 사이클 RED 단계)

대상 로드맵: `docs/PLAN.md` 9단계 "메인 메뉴 연결" 중 첫 번째 항목 — 데이터 파일 경로 설정 및
시료 관리 콘솔 메뉴 연결 (PRD 5.1 메인 메뉴 중 "시료 관리", 5.2).

## 이번에 구현할 동작 (1가지)

시료 관리 콘솔 메뉴에서 사용자가 "1"(등록)을 선택해 값을 입력하면 시료가 등록되고, "2"(조회)를
선택하면 등록된 시료 목록이 재고와 함께 출력되며, "3"(검색)을 선택해 키워드를 입력하면 일치하는
시료만 출력되고, "4"(이전 메뉴로)를 선택하면 메뉴 루프가 종료된다.

## 설계 결정

- `config.py`의 `Config` 클래스에 데이터 파일 경로 상수를 추가한다.
  - `Config.SAMPLES_FILE = "data/samples.json"`
  - `Config.ORDERS_FILE = "data/orders.json"`
  - 두 상수는 이번 사이클에서 `sample_view` 테스트가 직접 사용하지는 않지만(테스트는 `tmp_path`
    사용), `main.py`가 실제 실행 시 이 경로로 Repository를 생성하는 데 사용할 예정이다 (다음
    사이클들에서 계속 재사용).
- 위치: `app/views/sample_view.py`, 함수명 `run_sample_menu(sample_controller) -> None`
  - `input()`/`print()`를 직접 사용하는 콘솔 루프 함수. 클래스가 아닌 함수 단위로 구현한다
    (PRD 8장 View 책임 — 입출력만 담당, 상태를 갖지 않음).
  - 루프 각 반복마다 메뉴("1. 시료 등록", "2. 시료 조회", "3. 시료 검색", "4. 이전 메뉴로")를
    출력하고 `input("선택: ")`으로 선택지를 받는다.
  - `"1"`: `input()`으로 시료 ID/이름/평균생산시간/수율을 각각 받아 `sample_controller.register(id,
    name, int(avg), float(yield_rate))`를 호출하고, 등록된 시료의 id/name을 출력한다.
  - `"2"`: `sample_controller.list_samples()`를 호출해 각 시료를 `"{id} | {name} | 재고 {stock}"`
    형식으로 한 줄씩 출력한다. 결과가 없으면 "등록된 시료가 없습니다." 출력.
  - `"3"`: `input()`으로 검색어를 받아 `sample_controller.search_by_name(keyword)`를 호출하고 "2"와
    동일한 형식으로 출력한다. 결과가 없으면 "일치하는 시료가 없습니다." 출력.
  - `"4"`: 루프를 종료한다 (`return`).
  - 그 외 입력: "잘못된 입력입니다." 출력 후 메뉴를 다시 표시한다 (루프 계속).
  - `sample_controller`는 외부에서 주입받는다 (View가 Repository나 Controller를 직접 생성하지
    않음, PRD 8장).
- 메인 메뉴 루프(`main.py`)와의 연결, 다른 기능(주문/생산/출고/모니터링) 메뉴는 이번 사이클 범위 밖
  (다음 사이클들에서 순차적으로 진행).

## 테스트

- 파일: `tests/test_sample_view.py` (신규)
- 테스트 이름: `test_run_sample_menu_registers_lists_and_searches_samples`
- 검증 내용:
  - `tmp_path` fixture로 임시 `samples.json` 경로를 만들고, 실제 `SampleRepository`,
    `SampleController`를 생성한다 (mock 없음 — 콘솔 입출력만 이번 테스트의 "외부 경계"이므로 그
    부분만 대체한다).
  - `monkeypatch.setattr("builtins.input", ...)`로 `input()` 호출 순서에 맞춰 다음 값을 순서대로
    반환하도록 스텁한다: `"1"`(등록 선택), `"S-001"`, `"실리콘 웨이퍼-8인치"`, `"30"`, `"0.9"`,
    `"2"`(조회 선택), `"3"`(검색 선택), `"실리콘"`, `"4"`(종료).
  - `run_sample_menu(sample_controller)`를 호출한다.
  - `capsys.readouterr().out`으로 표준출력을 캡처해, 등록 확인 메시지에 `"S-001"`이 포함되고, 조회
    출력과 검색 출력 각각에 `"실리콘 웨이퍼-8인치"`와 `"재고 0"`이 포함되는지 확인한다 (등록 직후라
    재고는 0).
- mock 없이 실제 `SampleController`, `SampleRepository`, `Sample`, 실제 파일 시스템(`tmp_path`)을
  사용하고, 콘솔 입력만 `monkeypatch`로 스텁한다.

## 예상되는 최소 구현 방향 (GREEN 단계 참고용)

`config.py`의 `Config`에 `SAMPLES_FILE`, `ORDERS_FILE` 문자열 상수를 추가한다.
`app/views/sample_view.py`에 `run_sample_menu(sample_controller)` 함수를 정의해, `while True` 루프
안에서 메뉴를 출력하고 `input()`으로 받은 선택지에 따라 등록/조회/검색을 처리하다가 `"4"`를 받으면
`return`으로 종료한다. `main.py` 연결, 다른 메뉴는 이번 사이클에서 추가하지 않는다.
