from app.models.order import Order
from app.models.order_repository import OrderRepository


def test_save_and_find_by_id_returns_order_with_same_field_values(tmp_path):
    file_path = tmp_path / "orders.json"
    repository = OrderRepository(str(file_path))
    order = Order(
        id="ORD-20260416-0043",
        sample_id="S-001",
        customer_name="홍길동",
        quantity=20,
        status="RESERVED",
    )

    repository.save(order)
    found = repository.find_by_id("ORD-20260416-0043")

    assert found is not None
    assert found.id == order.id
    assert found.sample_id == order.sample_id
    assert found.customer_name == order.customer_name
    assert found.quantity == order.quantity
    assert found.status == order.status
