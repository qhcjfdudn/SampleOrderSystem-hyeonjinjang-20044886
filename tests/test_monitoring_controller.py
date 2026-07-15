from datetime import date

from app.controllers.monitoring_controller import MonitoringController
from app.controllers.order_controller import OrderController
from app.models.order_repository import OrderRepository
from app.models.sample import Sample
from app.models.sample_repository import SampleRepository


def test_order_status_counts_excludes_rejected_and_counts_each_status(tmp_path):
    order_repository = OrderRepository(str(tmp_path / "orders.json"))
    sample_repository = SampleRepository(str(tmp_path / "samples.json"))
    order_controller = OrderController(order_repository, sample_repository)
    monitoring_controller = MonitoringController(order_repository, sample_repository)

    sample_repository.save(
        Sample(
            id="S-001",
            name="실리콘 웨이퍼-8인치",
            avg_production_time=30,
            yield_rate=0.9,
            stock=100,
        )
    )
    sample_repository.save(
        Sample(
            id="S-002",
            name="GaN 웨이퍼-6인치",
            avg_production_time=45,
            yield_rate=0.85,
            stock=1,
        )
    )

    # 주문 A: RESERVED 유지
    order_controller.place_order("S-001", "홍길동", 5, date(2026, 4, 16))

    # 주문 B: 재고 충분 -> CONFIRMED
    order_b = order_controller.place_order("S-001", "김철수", 5, date(2026, 4, 16))
    order_controller.approve_order(order_b.id)

    # 주문 C: 승인 후 출고 -> RELEASE
    order_c = order_controller.place_order("S-001", "이영희", 5, date(2026, 4, 16))
    order_controller.approve_order(order_c.id)
    order_controller.release_order(order_c.id)

    # 주문 D: 거절 -> REJECTED (집계 제외 대상)
    order_d = order_controller.place_order("S-001", "박민수", 5, date(2026, 4, 16))
    order_controller.reject_order(order_d.id)

    # 주문 E: 재고 부족 -> PRODUCING
    order_e = order_controller.place_order("S-002", "정지훈", 20, date(2026, 4, 16))
    order_controller.approve_order(order_e.id)

    counts = monitoring_controller.order_status_counts()

    assert counts == {
        "RESERVED": 1,
        "CONFIRMED": 1,
        "PRODUCING": 1,
        "RELEASE": 1,
    }
