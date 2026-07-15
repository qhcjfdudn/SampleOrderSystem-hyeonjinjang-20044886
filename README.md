# 반도체 시료 생산주문관리 시스템 (SampleOrderSystem)

가상의 반도체 회사 "S-Semi"를 위한 콘솔(CLI) 기반 시료 생산주문관리 시스템입니다.
엑셀·메모장으로 관리하던 시료 주문/재고/생산 현황을 하나의 시스템에서 추적할 수 있도록 합니다.

전체 기능 명세는 [docs/PRD.md](docs/PRD.md), 개발 로드맵은 [docs/PLAN.md](docs/PLAN.md),
저장소 작업 안내는 [CLAUDE.md](CLAUDE.md)를 참고하세요.

## 주요 기능

| 기능 | 설명 |
|---|---|
| 시료 관리 | 시료 등록/조회/검색 (시료 ID, 이름, 평균 생산시간, 수율, 재고) |
| 시료 주문 | 고객 요청에 따른 주문 접수 (상태: `RESERVED`) |
| 주문 승인/거절 | 재고 상황에 따라 `CONFIRMED`/`PRODUCING`으로 자동 전환, 거절 시 `REJECTED` |
| 생산 라인 | 재고 부족분을 FIFO 큐로 생산 (실생산량 = ceil(부족분/수율)), 완료 시 `CONFIRMED`로 전환 |
| 출고 처리 | `CONFIRMED` 주문을 `RELEASE`로 전환 |
| 모니터링 | 상태별 주문 현황 및 시료별 재고 상태(여유/부족/고갈) 확인 |

주문 상태 흐름: `RESERVED` → (승인/거절) → `REJECTED` 또는 `CONFIRMED`/`PRODUCING` →
(생산 완료 시 `PRODUCING` → `CONFIRMED`) → (출고 처리) → `RELEASE`

## 요구사항

- Python 3.10 이상
- `data-persistence` 패키지 (로컬 editable 의존성, `../PoC/DataPersistence` 필요)

## 설치

```bash
pip install -e ../PoC/DataPersistence
pip install -e .[dev]
```

## 실행

```bash
python main.py
```

시료/주문 데이터는 `config.py`의 `Config.SAMPLES_FILE`/`Config.ORDERS_FILE`(기본값
`data/samples.json`, `data/orders.json`)에 JSON으로 저장됩니다. 실행 시 디렉터리가 없으면
자동으로 생성됩니다.

## 테스트

```bash
pytest tests/                                       # 전체 테스트
pytest tests/ --cov=app --cov-report=term-missing   # 커버리지 포함
```

## 프로젝트 구조

```
app/
├── models/        # Sample, Order 데이터 모델 + Repository (data_persistence 기반 영속성)
├── controllers/    # SampleController, OrderController, ProductionLineController,
│                   # MonitoringController — 비즈니스 로직
└── views/          # 기능별 콘솔 메뉴 (input()/print()만 사용)
config.py            # 데이터 파일 경로 등 전역 설정
main.py               # 진입점, 메인 메뉴 루프
tests/                # pytest 기반 테스트 (mock 없이 실제 클래스 + tmp_path 사용,
                      # 콘솔 View만 input() monkeypatch + capsys로 검증)
```

MVC 계층 간 책임 분리, TDD 진행 방식, 재고 차감 시점 등 설계 원칙은 [CLAUDE.md](CLAUDE.md)에
정리되어 있습니다.
