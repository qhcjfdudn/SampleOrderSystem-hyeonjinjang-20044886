import math
from datetime import date

from app.controllers.order_controller import OrderController
from app.controllers.production_line_controller import ProductionLineController
from app.models.order_repository import OrderRepository
from app.models.sample import Sample
from app.models.sample_repository import SampleRepository
from app.views.production_view import run_production_menu


def test_run_production_menu_shows_current_production_waiting_orders_and_completes(
    tmp_path, monkeypatch, capsys
):
    order_repository = OrderRepository(str(tmp_path / "orders.json"))
    sample_repository = SampleRepository(str(tmp_path / "samples.json"))
    order_controller = OrderController(order_repository, sample_repository)
    production_line_controller = ProductionLineController(order_repository, sample_repository)

    sample_repository.save(
        Sample(
            id="S-001",
            name="실리콘 웨이퍼-8인치",
            avg_production_time=30,
            yield_rate=0.9,
            stock=5,
        )
    )

    first_order = order_controller.place_order("S-001", "홍길동", 20, date(2026, 4, 16))
    second_order = order_controller.place_order("S-001", "김철수", 20, date(2026, 4, 16))
    order_controller.approve_order(first_order.id)
    order_controller.approve_order(second_order.id)

    inputs = iter(["1", "2", "3", "4"])
    monkeypatch.setattr("builtins.input", lambda *args: next(inputs))

    run_production_menu(production_line_controller)

    output = capsys.readouterr().out

    expected_shortfall = 20 - 5
    expected_actual_production = math.ceil(expected_shortfall / 0.9)

    assert first_order.id in output
    assert str(expected_shortfall) in output
    assert str(expected_actual_production) in output
    assert second_order.id in output
    assert "CONFIRMED" in output
