# PLAN.md (이번 사이클 RED 단계)

대상 로드맵: `docs/PLAN.md` 3단계 "시료 관리" 중 두 번째 항목 — 시료 조회 (PRD 5.2).

## 이번에 구현할 동작 (1가지)

여러 시료가 등록되어 있을 때 `SampleController.list_samples`를 호출하면, 등록된 모든 시료를
`Sample` 목록으로 반환한다 (각 시료의 현재 재고(stock) 포함).

## 설계 결정

- `SampleRepository`(`app/models/sample_repository.py`)에 `find_all() -> list[Sample]` 메서드를
  추가한다.
  - `data_persistence.DataPersistence.read_all() -> list[dict]`로 전체 레코드를 조회한 뒤, 각 dict를
    `Sample(**record)`로 변환해 리스트로 반환한다 (`DataPersistence.read_all`은 실제 라이브러리에 이미
    존재하는 API, `C:\reviewer\PoC\DataPersistence\data_persistence\processor.py` 확인).
  - 등록된 시료가 없으면 빈 리스트를 반환한다.
- `SampleController`(`app/controllers/sample_controller.py`)에 `list_samples() -> list[Sample]` 메서드를
  추가한다.
  - `self.sample_repository.find_all()`을 그대로 호출해 반환한다 (Controller는 정렬/필터 등 추가 로직
    없이 Repository 결과를 그대로 전달, PRD 5.2 "등록된 모든 시료 목록과 현재 재고 수량을 함께 표시"는
    재고가 이미 `Sample.stock` 필드에 있으므로 별도 가공 불필요).
- 콘솔 출력(View, 목록을 화면에 표시하는 부분)은 이번 사이클 범위 밖.
- 시료 검색 기능은 이번 사이클 범위 밖 (다음 사이클에서 진행).

## 테스트

- 파일: `tests/test_sample_controller.py`에 테스트를 추가한다 (기존 파일 확장).
- 테스트 이름: `test_list_samples_returns_all_registered_samples`
- 검증 내용:
  - `tmp_path` fixture로 임시 `samples.json` 경로를 만들고, 실제 `SampleRepository`·`SampleController`를
    생성한다 (mock 없음).
  - `controller.register("S-001", "실리콘 웨이퍼-8인치", 30, 0.9)`와
    `controller.register("S-002", "GaN 웨이퍼-6인치", 45, 0.85)`로 시료 2개를 등록한다.
  - `controller.list_samples()`를 호출한 결과가 길이 2인 리스트이며, 반환된 `Sample` 객체들의 `id`
    집합이 `{"S-001", "S-002"}`와 같은지 확인한다 (순서는 강제하지 않음, `data_persistence`가 순서를
    보장한다는 명세가 없으므로).
  - 각 `Sample`의 `stock`이 등록 직후 값인 `0`인지 확인한다 (PRD 5.2 "현재 재고 수량을 함께 표시"
    검증).
- mock 없이 실제 `SampleController`, `SampleRepository`, `Sample`, 실제 파일 시스템(`tmp_path`)을
  사용하여 검증한다.

## 예상되는 최소 구현 방향 (GREEN 단계 참고용)

`SampleRepository`에 `find_all(self) -> list`을 추가해 `self._data_persistence.read_all()` 결과 각
dict를 `Sample(**record)`로 변환한 리스트를 반환한다. `SampleController`에 `list_samples(self)`를
추가해 `self.sample_repository.find_all()`을 그대로 반환한다. 정렬, 페이지네이션, View 출력 등은
이번 사이클에서 추가하지 않는다.
