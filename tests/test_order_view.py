from datetime import date

from app.controllers.order_controller import OrderController
from app.models.order_repository import OrderRepository
from app.models.sample import Sample
from app.models.sample_repository import SampleRepository
from app.views.order_view import run_order_menu


def test_run_order_menu_places_order_and_shows_confirmation(tmp_path, monkeypatch, capsys):
    order_repository = OrderRepository(str(tmp_path / "orders.json"))
    sample_repository = SampleRepository(str(tmp_path / "samples.json"))
    order_controller = OrderController(order_repository, sample_repository)

    sample_repository.save(
        Sample(
            id="S-001",
            name="실리콘 웨이퍼-8인치",
            avg_production_time=30,
            yield_rate=0.9,
            stock=50,
        )
    )

    monkeypatch.setattr("app.views.order_view._today", lambda: date(2026, 4, 16))

    inputs = iter(["1", "S-001", "홍길동", "5", "2"])
    monkeypatch.setattr("builtins.input", lambda *args: next(inputs))

    run_order_menu(order_controller)

    output = capsys.readouterr().out

    assert "ORD-20260416-0001" in output
    assert "RESERVED" in output
