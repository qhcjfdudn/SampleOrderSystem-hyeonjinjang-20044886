import math
from datetime import date

from app.controllers.order_controller import OrderController
from app.controllers.production_line_controller import ProductionLineController
from app.models.order_repository import OrderRepository
from app.models.sample import Sample
from app.models.sample_repository import SampleRepository


def test_current_production_returns_none_when_no_producing_order(tmp_path):
    order_repository = OrderRepository(str(tmp_path / "orders.json"))
    sample_repository = SampleRepository(str(tmp_path / "samples.json"))
    production_controller = ProductionLineController(order_repository, sample_repository)

    assert production_controller.current_production() is None


def test_current_production_calculates_shortfall_and_actual_production_for_earliest_producing_order(
    tmp_path,
):
    order_repository = OrderRepository(str(tmp_path / "orders.json"))
    sample_repository = SampleRepository(str(tmp_path / "samples.json"))
    order_controller = OrderController(order_repository, sample_repository)
    production_controller = ProductionLineController(order_repository, sample_repository)

    sample_repository.save(
        Sample(
            id="S-001",
            name="실리콘 웨이퍼-8인치",
            avg_production_time=30,
            yield_rate=0.9,
            stock=5,
        )
    )
    placed_order = order_controller.place_order("S-001", "홍길동", 20, date(2026, 4, 16))
    order_controller.approve_order(placed_order.id)

    result = production_controller.current_production()

    assert result is not None
    assert result["order"].id == placed_order.id

    expected_shortfall = 20 - 5
    expected_actual_production = math.ceil(expected_shortfall / 0.9)
    expected_total_time = 30 * expected_actual_production

    assert result["shortfall"] == expected_shortfall
    assert result["actual_production"] == expected_actual_production
    assert result["total_production_time"] == expected_total_time
