from datetime import date

from app.controllers.order_controller import OrderController
from app.models.order_repository import OrderRepository


def test_place_order_generates_order_id_and_saves_reserved_order(tmp_path):
    file_path = tmp_path / "orders.json"
    repository = OrderRepository(str(file_path))
    controller = OrderController(repository)

    first_order = controller.place_order("S-001", "홍길동", 20, date(2026, 4, 16))

    assert first_order.id == "ORD-20260416-0001"
    assert first_order.sample_id == "S-001"
    assert first_order.customer_name == "홍길동"
    assert first_order.quantity == 20
    assert first_order.status == "RESERVED"

    second_order = controller.place_order("S-002", "김철수", 5, date(2026, 4, 16))

    assert second_order.id == "ORD-20260416-0002"

    found = repository.find_by_id("ORD-20260416-0001")
    assert found is not None
    assert found.sample_id == first_order.sample_id
    assert found.customer_name == first_order.customer_name
    assert found.quantity == first_order.quantity
    assert found.status == first_order.status
