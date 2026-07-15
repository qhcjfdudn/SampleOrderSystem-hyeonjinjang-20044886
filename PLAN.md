# PLAN.md (이번 사이클 RED 단계)

대상 로드맵: `docs/PLAN.md` 2단계 "데이터 계층 (Model)" 중 세 번째 항목 — 시료(Sample) 데이터의
`data_persistence` 연동.

## 이번에 구현할 동작 (1가지)

`SampleRepository`로 `Sample`을 저장(save)하면, 같은 id로 다시 조회했을 때(find_by_id) 저장한 시료와
동일한 필드 값을 가진 `Sample`을 반환한다.

## 설계 결정

- 위치: `app/models/sample_repository.py`
- 클래스명: `SampleRepository`
- 생성자: `SampleRepository(file_path)` — `data_persistence.DataPersistence(file_path)`를 내부에서
  생성해 `samples.json` 파일 경로를 그대로 전달받는다 (PRD 7장, 파일 경로는 저장소 밖에서 결정).
- 메서드:
  - `save(sample: Sample) -> None` — `Sample` 객체를 dict로 변환해 `DataPersistence.create(record)`로
    저장한다.
  - `find_by_id(id) -> Sample | None` — `DataPersistence.read(id)`로 dict를 조회한 뒤 `Sample` 객체로
    변환해 반환한다.
- `Sample` ↔ dict 변환: `Sample`의 5개 필드(id, name, avg_production_time, yield_rate, stock)를 그대로
  dict의 키/값으로 매핑한다. 변환 책임은 `SampleRepository` 내부에 최소한으로 둔다(this 사이클 범위 한정,
  `Sample`에는 `to_dict`/`from_dict`를 추가하지 않고 저장소에서 직접 dict를 구성/해석한다).
- Order 저장소(`OrderRepository`)는 이번 사이클 범위 밖 (다음 사이클에서 진행).
- 파일 I/O는 `data_persistence.DataPersistence`에 위임하며, 직접 `open`/`json` 등을 사용하지 않는다.

## 테스트

- 파일: `tests/test_sample_repository.py`
- 테스트 이름: `test_save_and_find_by_id_returns_sample_with_same_field_values`
- 검증 내용:
  - `tmp_path` fixture로 임시 디렉터리에 `samples.json` 경로를 만들고, 그 경로로 `SampleRepository`를
    생성한다 (실제 파일 시스템 사용, mock 없음).
  - `Sample(id="S-001", name="실리콘 웨이퍼-8인치", avg_production_time=30, yield_rate=0.9, stock=100)`을
    생성해 `repository.save(sample)`로 저장한다.
  - `repository.find_by_id("S-001")`로 조회한 결과가 `None`이 아니며, `id`, `name`,
    `avg_production_time`, `yield_rate`, `stock` 속성이 저장한 시료와 각각 동일한 값인지 확인한다.
- mock 없이 실제 `SampleRepository`, `Sample`, `DataPersistence`, 실제 파일 시스템(`tmp_path`)을 사용하여
  검증한다.

## 예상되는 최소 구현 방향 (GREEN 단계 참고용)

`app/models/sample_repository.py`에 `SampleRepository` 클래스를 정의한다. 생성자에서
`DataPersistence(file_path)` 인스턴스를 보관하고, `save`는 `Sample` 필드를 dict로 만들어 `create`를
호출하며, `find_by_id`는 `read(id)`로 얻은 dict를 `Sample(**dict)`로 복원해 반환한다. 그 외 update/delete,
목록 조회, Order 연동 등은 이번 사이클에서 추가하지 않는다.
