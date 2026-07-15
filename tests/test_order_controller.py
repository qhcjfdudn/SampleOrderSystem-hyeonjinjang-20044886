from datetime import date

from app.controllers.order_controller import OrderController
from app.models.order_repository import OrderRepository
from app.models.sample import Sample
from app.models.sample_repository import SampleRepository


def test_place_order_generates_order_id_and_saves_reserved_order(tmp_path):
    order_repository = OrderRepository(str(tmp_path / "orders.json"))
    sample_repository = SampleRepository(str(tmp_path / "samples.json"))
    controller = OrderController(order_repository, sample_repository)

    first_order = controller.place_order("S-001", "홍길동", 20, date(2026, 4, 16))

    assert first_order.id == "ORD-20260416-0001"
    assert first_order.sample_id == "S-001"
    assert first_order.customer_name == "홍길동"
    assert first_order.quantity == 20
    assert first_order.status == "RESERVED"

    second_order = controller.place_order("S-002", "김철수", 5, date(2026, 4, 16))

    assert second_order.id == "ORD-20260416-0002"

    found = order_repository.find_by_id("ORD-20260416-0001")
    assert found is not None
    assert found.sample_id == first_order.sample_id
    assert found.customer_name == first_order.customer_name
    assert found.quantity == first_order.quantity
    assert found.status == first_order.status


def test_reject_order_transitions_status_to_rejected(tmp_path):
    order_repository = OrderRepository(str(tmp_path / "orders.json"))
    sample_repository = SampleRepository(str(tmp_path / "samples.json"))
    controller = OrderController(order_repository, sample_repository)

    placed_order = controller.place_order("S-001", "홍길동", 20, date(2026, 4, 16))

    rejected_order = controller.reject_order(placed_order.id)

    assert rejected_order.status == "REJECTED"

    found = order_repository.find_by_id(placed_order.id)
    assert found is not None
    assert found.status == "REJECTED"


def test_approve_order_confirms_order_and_deducts_stock_when_stock_is_sufficient(tmp_path):
    order_repository = OrderRepository(str(tmp_path / "orders.json"))
    sample_repository = SampleRepository(str(tmp_path / "samples.json"))
    controller = OrderController(order_repository, sample_repository)

    sample_repository.save(
        Sample(
            id="S-001",
            name="실리콘 웨이퍼-8인치",
            avg_production_time=30,
            yield_rate=0.9,
            stock=50,
        )
    )
    placed_order = controller.place_order("S-001", "홍길동", 20, date(2026, 4, 16))

    approved_order = controller.approve_order(placed_order.id)

    assert approved_order.status == "CONFIRMED"

    found_order = order_repository.find_by_id(placed_order.id)
    assert found_order is not None
    assert found_order.status == "CONFIRMED"

    found_sample = sample_repository.find_by_id("S-001")
    assert found_sample is not None
    assert found_sample.stock == 30


def test_approve_order_sets_producing_and_keeps_stock_when_stock_is_insufficient(tmp_path):
    order_repository = OrderRepository(str(tmp_path / "orders.json"))
    sample_repository = SampleRepository(str(tmp_path / "samples.json"))
    controller = OrderController(order_repository, sample_repository)

    sample_repository.save(
        Sample(
            id="S-001",
            name="실리콘 웨이퍼-8인치",
            avg_production_time=30,
            yield_rate=0.9,
            stock=5,
        )
    )
    placed_order = controller.place_order("S-001", "홍길동", 20, date(2026, 4, 16))

    approved_order = controller.approve_order(placed_order.id)

    assert approved_order.status == "PRODUCING"

    found_order = order_repository.find_by_id(placed_order.id)
    assert found_order is not None
    assert found_order.status == "PRODUCING"

    found_sample = sample_repository.find_by_id("S-001")
    assert found_sample is not None
    assert found_sample.stock == 5


def test_list_reserved_orders_returns_only_reserved_orders(tmp_path):
    order_repository = OrderRepository(str(tmp_path / "orders.json"))
    sample_repository = SampleRepository(str(tmp_path / "samples.json"))
    controller = OrderController(order_repository, sample_repository)

    sample_repository.save(
        Sample(
            id="S-001",
            name="실리콘 웨이퍼-8인치",
            avg_production_time=30,
            yield_rate=0.9,
            stock=50,
        )
    )
    order_a = controller.place_order("S-001", "홍길동", 10, date(2026, 4, 16))
    order_b = controller.place_order("S-001", "김철수", 5, date(2026, 4, 16))
    controller.approve_order(order_b.id)

    reserved_orders = controller.list_reserved_orders()

    assert len(reserved_orders) == 1
    assert reserved_orders[0].id == order_a.id
    assert reserved_orders[0].status == "RESERVED"


def test_list_confirmed_orders_returns_only_confirmed_orders(tmp_path):
    order_repository = OrderRepository(str(tmp_path / "orders.json"))
    sample_repository = SampleRepository(str(tmp_path / "samples.json"))
    controller = OrderController(order_repository, sample_repository)

    sample_repository.save(
        Sample(
            id="S-001",
            name="실리콘 웨이퍼-8인치",
            avg_production_time=30,
            yield_rate=0.9,
            stock=50,
        )
    )
    order_a = controller.place_order("S-001", "홍길동", 10, date(2026, 4, 16))
    controller.approve_order(order_a.id)
    controller.place_order("S-001", "김철수", 5, date(2026, 4, 16))

    confirmed_orders = controller.list_confirmed_orders()

    assert len(confirmed_orders) == 1
    assert confirmed_orders[0].id == order_a.id
    assert confirmed_orders[0].status == "CONFIRMED"


def test_release_order_transitions_status_to_release_without_changing_stock(tmp_path):
    order_repository = OrderRepository(str(tmp_path / "orders.json"))
    sample_repository = SampleRepository(str(tmp_path / "samples.json"))
    controller = OrderController(order_repository, sample_repository)

    sample_repository.save(
        Sample(
            id="S-001",
            name="실리콘 웨이퍼-8인치",
            avg_production_time=30,
            yield_rate=0.9,
            stock=50,
        )
    )
    placed_order = controller.place_order("S-001", "홍길동", 20, date(2026, 4, 16))
    controller.approve_order(placed_order.id)

    released_order = controller.release_order(placed_order.id)

    assert released_order.status == "RELEASE"

    found_order = order_repository.find_by_id(placed_order.id)
    assert found_order is not None
    assert found_order.status == "RELEASE"

    found_sample = sample_repository.find_by_id("S-001")
    assert found_sample is not None
    assert found_sample.stock == 30
