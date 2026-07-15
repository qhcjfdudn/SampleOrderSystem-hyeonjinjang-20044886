from app.models.order import Order


def test_order_stores_all_field_values():
    order = Order(
        id="ORD-20260416-0043",
        sample_id="S-001",
        customer_name="홍길동",
        quantity=20,
        status="RESERVED",
    )

    assert order.id == "ORD-20260416-0043"
    assert order.sample_id == "S-001"
    assert order.customer_name == "홍길동"
    assert order.quantity == 20
    assert order.status == "RESERVED"
