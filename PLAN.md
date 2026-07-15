# PLAN.md (이번 사이클 RED 단계)

대상 로드맵: `docs/PLAN.md` 3단계 "시료 관리" 중 첫 번째 항목 — 시료 등록 (PRD 5.2).

## 이번에 구현할 동작 (1가지)

`SampleController.register`에 시료 ID/이름/평균 생산시간/수율을 전달해 새 시료를 등록하면, 재고
(stock) 0으로 시작하는 `Sample`이 생성되어 저장소에 저장되고, 등록된 `Sample`이 반환된다.

## 설계 결정

- 위치: `app/controllers/sample_controller.py`
- 클래스명: `SampleController`
- 생성자: `SampleController(sample_repository)` — 기존 `SampleRepository` 인스턴스를 주입받는다
  (Controller는 저장소 구현을 직접 생성하지 않고 의존성으로 받는다, PRD 8장 MVC 계층 분리).
- 메서드: `register(id, name, avg_production_time, yield_rate) -> Sample`
  - 전달받은 값으로 `Sample(id=id, name=name, avg_production_time=avg_production_time,
    yield_rate=yield_rate, stock=0)`을 생성한다. 신규 등록 시점에는 아직 생산된 실물이 없으므로
    재고는 항상 0으로 시작한다 (PRD 5.2 — 등록 시 입력값은 시료 ID/이름/평균 생산시간/수율뿐이며
    재고는 입력값에 없음).
  - `sample_repository.save(sample)`로 저장한다.
  - 저장한 `Sample` 객체를 그대로 반환한다 (View가 등록 결과를 표시할 때 사용, 이번 사이클은 View
    연동 범위 밖).
- 콘솔 입출력(View)은 이번 사이클 범위 밖 — Controller의 순수 로직만 구현하고, 사용자 입력 처리/
  화면 출력은 이후 사이클(9단계 메인 메뉴 연결 전 별도 View 사이클)에서 다룬다.
- 시료 조회/검색 기능은 이번 사이클 범위 밖 (다음 사이클에서 진행).
- id 중복 검사 등 유효성 검증은 이번 사이클 범위 밖 (PRD에 별도 명시 없음, 최소 구현으로 시작).

## 테스트

- 파일: `tests/test_sample_controller.py`
- 테스트 이름: `test_register_creates_sample_with_zero_stock_and_saves_it`
- 검증 내용:
  - `tmp_path` fixture로 임시 `samples.json` 경로를 만들고, 실제 `SampleRepository`를 생성한다
    (mock 없음, 이전 사이클에서 검증된 `SampleRepository`를 그대로 사용).
  - `SampleController(repository)`를 생성하고 `controller.register("S-001", "실리콘 웨이퍼-8인치",
    30, 0.9)`를 호출한다.
  - 반환된 `Sample`의 `id`, `name`, `avg_production_time`, `yield_rate`가 입력값과 동일하고
    `stock`이 `0`인지 확인한다.
  - `repository.find_by_id("S-001")`로 다시 조회했을 때도 동일한 필드 값(재고 0 포함)을 가진
    `Sample`이 반환되는지 확인해, 실제로 저장소에 저장되었음을 검증한다.
- mock 없이 실제 `SampleController`, `SampleRepository`, `Sample`, 실제 파일 시스템(`tmp_path`)을
  사용하여 검증한다.

## 예상되는 최소 구현 방향 (GREEN 단계 참고용)

`app/controllers/sample_controller.py`에 `SampleController` 클래스를 정의한다. 생성자에서
`sample_repository`를 보관하고, `register`는 인자로 받은 값과 `stock=0`으로 `Sample`을 생성해
`sample_repository.save(sample)`를 호출한 뒤 그 `Sample`을 반환한다. 조회/검색 메서드나 View 연동은
이번 사이클에서 추가하지 않는다.
