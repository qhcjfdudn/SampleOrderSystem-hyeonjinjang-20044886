from datetime import date

from app.controllers.monitoring_controller import MonitoringController
from app.controllers.order_controller import OrderController
from app.models.order_repository import OrderRepository
from app.models.sample import Sample
from app.models.sample_repository import SampleRepository
from app.views.monitoring_view import run_monitoring_menu


def test_run_monitoring_menu_shows_order_status_counts_and_sample_stock_status(
    tmp_path, monkeypatch, capsys
):
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
            stock=20,
        )
    )
    order_controller.place_order("S-001", "홍길동", 5, date(2026, 4, 16))

    inputs = iter(["1", "2", "3"])
    monkeypatch.setattr("builtins.input", lambda *args: next(inputs))

    run_monitoring_menu(monitoring_controller)

    output = capsys.readouterr().out

    assert "RESERVED: 1건" in output
    assert "CONFIRMED: 0건" in output
    assert "S-001" in output
    assert "여유" in output
