# PLAN.md (이번 사이클 RED 단계)

대상 로드맵: `docs/PLAN.md` 2단계 "데이터 계층 (Model)" 중 첫 번째 항목 — 시료(Sample) 모델.

## 이번에 구현할 동작 (1가지)

Sample 객체를 시료 ID/이름/평균 생산시간/수율/현재 재고 값으로 생성하면 각 속성에 그 값이 그대로 저장된다.

## 설계 결정

- 위치: `app/models/sample.py`
- 클래스명: `Sample`
- 생성자 인자 및 속성명 (PRD 6장 "시료(Sample)" 필드 매핑):
  - `id` — 시료 ID (예: "S-001")
  - `name` — 이름 (예: "실리콘 웨이퍼-8인치")
  - `avg_production_time` — 평균 생산시간 (min/ea)
  - `yield_rate` — 수율 (0~1)
  - `stock` — 현재 재고 (ea)
- `id` 속성은 시료 ID 값을 그대로 담는다 (doc-consistency-verify 검토 결과 반영, `data_persistence`의
  레코드 `id` 필드와 자연스럽게 대응시키기 위함).
- data_persistence 연동, Order 모델은 이번 사이클 범위 밖 (다음 사이클에서 진행).

## 테스트

- 파일: `tests/test_sample_model.py`
- 테스트 이름: `test_sample_stores_all_field_values`
- 검증 내용: `Sample(id="S-001", name="실리콘 웨이퍼-8인치", avg_production_time=10, yield_rate=0.9, stock=50)`로
  생성한 인스턴스의 `id`, `name`, `avg_production_time`, `yield_rate`, `stock` 속성이 각각 생성 시 전달한 값과
  동일한지 확인한다.
- mock 없이 실제 `Sample` 클래스를 import하여 검증한다.

## 예상되는 최소 구현 방향 (GREEN 단계 참고용)

`app/models/sample.py`에 `Sample` 클래스(또는 `dataclass`)를 정의하고, 생성자에서 받은 값을 각각 동일한 이름의
속성에 저장한다. 그 외 메서드나 검증 로직은 이번 사이클에서 추가하지 않는다.
