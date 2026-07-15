# CLAUDE.md

이 파일은 Claude Code가 이 저장소에서 작업할 때 참고하는 안내 문서입니다.

## 프로젝트 개요
### 프로젝트 목적
반도체 시료 생산주문관리 시스템

### 프로젝트 시나리오
여기 가상의 반도체 회사 "S-Semi" 가 있습니다.

이 회사는 다양한 종류의 반도체 시료(Sample)를 생산하여 연구소, 팹리스(Fabless) 업체, 대학 연구실 등의 고객에게
납품하고 있습니다. 시료는 주문이 들어오면 웨이퍼 공정 설비를 통해 제작되고, 검수를 거쳐 고객에게 출고됩니다.
그런데 최근 들어 주문량이 급증하면서 문제가 생겼습니다.

"어, 이 주문 처리됐나요?"

"공정 예약을 했는데, 언제 완성되는지 모르겠어요."

"이미 충분한 시료 재고가 있는데, 왜 추가 공정이 돌아가고 있나요?"

엑셀과 메모장으로 주문을 관리하다 보니, 실수가 잦고 재고와 공정 현황을 한눈에 파악하기 어려웠습니다.
이러한 이유로 S-Semi에서는 더 체계적인 시료 관리를 위한 "반도체 시료 생산주문관리 시스템" 을 개발하기로 결정
했습니다.

## 주요 기능

시스템은 콘솔(CLI) 메뉴 기반으로 동작하며, 아래 6가지 핵심 기능으로 구성됩니다.
전체 기능 명세는 [docs/PRD.md](docs/PRD.md)를 참고하세요.

| 기능 | 설명 |
|---|---|
| 시료 관리 | 시료 등록/조회/검색 (속성: 시료 ID, 이름, 평균 생산시간, 수율, 재고) |
| 시료 주문 | 고객 요청에 따른 주문 접수 (상태: RESERVED) |
| 주문 승인/거절 | 재고 상황에 따라 CONFIRMED 또는 PRODUCING으로 자동 전환, 거절 시 REJECTED |
| 생산 라인 | 재고 부족분을 FIFO 큐로 생산 (실생산량 = ceil(부족분/수율)), 완료 시 CONFIRMED로 전환 |
| 출고 처리 | CONFIRMED 주문을 RELEASE로 전환 |
| 모니터링 | 상태별 주문 현황 및 시료별 재고 상태(여유/부족/고갈) 확인 |

### 주문 상태(Order Status)

`RESERVED`(접수) → 승인/거절 → `REJECTED`(거절, 모니터링 제외) 또는 재고 확인 → `CONFIRMED`(출고 대기) /
`PRODUCING`(생산 중, 생산 완료 후 CONFIRMED로 전환) → 출고 처리 → `RELEASE`(출고 완료)

### 요구사항 문서

- 기능 명세 정리본: `docs/PRD.md`

## 빌드 및 실행 명령어

```bash
# 의존성 설치 (최초 1회, 로컬 editable 패키지 포함)
pip install -e ../PoC/DataPersistence
pip install -e .[dev]

# 콘솔 앱 실행
python main.py
```

- 데이터 파일 경로는 `config.py`의 `Config.SAMPLES_FILE`/`Config.ORDERS_FILE`(기본값
  `data/samples.json`, `data/orders.json`)에 정의되어 있으며, 실행 시 디렉터리가 없으면
  `data_persistence`가 자동으로 생성한다.

## 테스트 명령어

```bash
pytest tests/                          # 전체 테스트 실행
pytest tests/ --cov=app --cov-report=term-missing   # 커버리지 포함
pytest tests/test_order_controller.py  # 특정 파일만 실행
```

## 코드 스타일 및 규칙

- 폴더 구조: MVC 3계층 (`app/models`, `app/controllers`, `app/views`), 진입점은 `main.py`,
  전역 설정은 `config.py`.
  - Model(`app/models`): 데이터 클래스(`Sample`, `Order`)와 Repository(`SampleRepository`,
    `OrderRepository`). Repository는 `data_persistence.DataPersistence`에만 파일 I/O를 위임하고
    직접 `open`/`json`을 사용하지 않는다.
  - Controller(`app/controllers`): 기능 단위로 분리(`SampleController`, `OrderController`,
    `ProductionLineController`, `MonitoringController`). 저장소를 생성자 주입으로 받아 비즈니스
    로직(상태 전이, 재고 계산, FIFO 큐 등)을 담당하고, 콘솔 입출력은 하지 않는다.
  - View(`app/views`): 기능별 파일 분리(`sample_view.py`, `order_view.py`, `production_view.py`,
    `monitoring_view.py`). `input()`/`print()`만 사용하며 Controller를 외부에서 주입받아 호출할 뿐,
    Repository를 직접 생성하거나 비즈니스 로직을 갖지 않는다.
- TDD 사이클: 매 사이클 "이번에 구현할 동작 1가지"만 다루며, 루트 `PLAN.md`에 RED 단계 설계를
  먼저 기록한 뒤 실패 테스트 → 최소 구현 → 검증 순서로 진행한다 (`docs/PLAN.md` 9장·10장 참고).
- 테스트는 mock 없이 실제 클래스와 `tmp_path`(임시 파일 시스템)를 사용하는 것을 원칙으로 하며,
  콘솔 View 테스트만 `input()`을 `monkeypatch`하고 `capsys`로 출력을 검증한다 (콘솔 입출력이 유일한
  "외부 경계"이기 때문).
- 재고 차감은 주문이 `CONFIRMED`로 전환되는 시점에만 이뤄진다 (즉시 승인이든 생산 완료 후 전환이든
  동일). 출고(`RELEASE`)는 상태만 전환하며 재고를 다시 건드리지 않는다.
- 생산 큐는 별도 자료구조 없이 `OrderRepository`에 저장된 `PRODUCING` 주문을 주문번호(`id`,
  `ORD-YYYYMMDD-NNNN` 형식이라 문자열 정렬이 곧 시간순)로 정렬해 파생 조회하는 방식으로 구현했다.

## 원본 설계 자료와의 UX 차이 (참고용, 의도적으로 유지)

`temp/requirements/feature requirements/*_예시 UI 화면.png`에 있는 원본 예시 화면과 실제 구현을
비교한 결과, 다음과 같은 차이가 있다. 기능적으로는 요구사항을 충족하지만 세부 UX가 다르므로 참고용으로
기록해둔다 (10단계 마무리 시 사용자와 협의해 코드는 변경하지 않고 문서화만 하기로 결정함).

- **뒤로가기/종료 번호**: 예시 UI는 모든 하위 메뉴에서 뒤로가기·종료를 항상 `[0]`으로 표시한다.
  실제 구현은 각 메뉴의 마지막 순번(예: 시료 관리는 `4`, 메인 메뉴는 `7`)을 사용한다.
- **메인 메뉴 항목 순서**: 예시 UI는 `[4] 모니터링 [5] 생산 라인 조회 [6] 출고 처리` 순서이나, 실제
  구현은 `4=생산 라인 조회, 5=출고 처리, 6=모니터링` 순서다 (`CLAUDE.md` 표 순서를 따름, PRD 5.1 표
  순서와도 다름).
- **승인/거절·출고 처리의 입력 방식**: 예시 UI는 번호가 매겨진 목록에서 순번을 선택하고, 승인 시
  재고 확인 메시지와 `[Y]/[N]` 확인 단계를 거친다. 실제 구현은 주문번호(문자열)를 직접 입력받아
  확인 단계 없이 바로 처리한다.
- **생산 라인/모니터링 표시 정보**: 예시 UI는 진행률(%), 완료 예정 시각, 재고 잔여율 막대 등을
  보여주지만, 실제 구현은 이 시스템이 시간 경과를 시뮬레이션하지 않는 점(생산 완료는 담당자의 명시적
  액션)에 맞춰 부족분/실생산량/총생산시간과 여유·부족·고갈 상태만 텍스트로 보여준다 (PRD 5.5/5.7
  "표기 정보 수준은 구현 시 자율적으로 결정" 조항에 따른 의도적 단순화).

## 기타 참고 사항

- 생산 라인은 단일 라인으로 동작하며, 한 번에 하나의 시료만 생산합니다.
- 생산 대기열은 FIFO(선입선출) 방식으로 처리됩니다.
- `REJECTED` 상태는 정상 흐름 밖의 상태로, 모니터링 집계에서 제외됩니다.
