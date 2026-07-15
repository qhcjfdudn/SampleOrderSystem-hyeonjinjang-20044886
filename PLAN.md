# PLAN.md (이번 사이클 RED 단계)

대상 로드맵: `docs/PLAN.md` 3단계 "시료 관리" 중 세 번째 항목 — 시료 검색 (PRD 5.2).

## 이번에 구현할 동작 (1가지)

여러 시료가 등록되어 있을 때 `SampleController.search_by_name`에 이름의 일부(부분 문자열)를
전달하면, 해당 문자열을 이름에 포함한 시료만 `Sample` 목록으로 반환한다.

## 설계 결정

- `app/controllers/sample_controller.py`의 `SampleController`에 `search_by_name(keyword) ->
  list[Sample]` 메서드를 추가한다.
  - `self.sample_repository.find_all()`로 전체 시료를 조회한 뒤, `keyword in sample.name`(부분 문자열
    포함 여부)을 만족하는 `Sample`만 리스트로 반환한다 (PRD 5.2 "이름 등 속성으로 특정 시료를 검색" —
    이번 사이클은 이름 속성 검색만 범위로 한정).
  - 대소문자 구분, 정렬 등 추가 규칙은 PRD에 명시가 없으므로 이번 사이클에서 다루지 않는다 (파이썬
    `in` 연산자의 기본 대소문자 구분 동작을 그대로 사용).
  - 일치하는 시료가 없으면 빈 리스트를 반환한다.
  - `SampleRepository`에는 변경이 없다 (이미 존재하는 `find_all()`을 재사용, 검색 필터링은 Controller
    책임으로 둔다 — PRD 8장에서 데이터 접근은 Repository, 조회 로직 조합은 Controller가 담당).
- 이름 외 다른 속성(수율, 생산시간 등)으로의 검색은 이번 사이클 범위 밖 — PRD 5.2가 "이름 등"이라고만
  서술해 구체적 속성 목록을 특정하지 않았으므로, 이번 사이클은 이름 검색만 구현하고 다른 속성 검색은
  추후 필요 시 별도 사이클로 확장한다.
- 콘솔 입출력(View)은 이번 사이클 범위 밖.

## 테스트

- 파일: `tests/test_sample_controller.py`에 테스트를 추가한다 (기존 파일 확장).
- 테스트 이름: `test_search_by_name_returns_only_samples_matching_keyword`
- 검증 내용:
  - `tmp_path` fixture로 임시 `samples.json` 경로를 만들고, 실제 `SampleRepository`·`SampleController`를
    생성한다 (mock 없음).
  - `controller.register("S-001", "실리콘 웨이퍼-8인치", 30, 0.9)`,
    `controller.register("S-002", "실리콘 웨이퍼-12인치", 40, 0.88)`,
    `controller.register("S-003", "GaN 웨이퍼-6인치", 45, 0.85)`로 시료 3개를 등록한다.
  - `controller.search_by_name("실리콘")`을 호출한 결과가 길이 2인 리스트이며, 반환된 `Sample`들의
    `id` 집합이 `{"S-001", "S-002"}`와 같은지 확인한다 (`GaN` 시료는 제외되어야 함).
  - `controller.search_by_name("존재하지않는이름")`을 호출하면 빈 리스트가 반환되는지 확인한다.
- mock 없이 실제 `SampleController`, `SampleRepository`, `Sample`, 실제 파일 시스템(`tmp_path`)을
  사용하여 검증한다.

## 예상되는 최소 구현 방향 (GREEN 단계 참고용)

`SampleController`에 `search_by_name(self, keyword)`을 추가해 `self.sample_repository.find_all()`
결과를 `keyword in sample.name`으로 필터링한 리스트를 반환한다. `SampleRepository`나 `Sample`은
변경하지 않는다. 다른 속성 검색, 정렬, View 출력 등은 이번 사이클에서 추가하지 않는다.
