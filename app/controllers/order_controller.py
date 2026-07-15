from app.models.order import Order


class OrderController:
    def __init__(self, order_repository, sample_repository):
        self.order_repository = order_repository
        self.sample_repository = sample_repository

    def place_order(self, sample_id, customer_name, quantity, order_date) -> Order:
        formatted = order_date.strftime("%Y%m%d")
        prefix = f"ORD-{formatted}-"

        existing_count = sum(
            1 for order in self.order_repository.find_all() if order.id.startswith(prefix)
        )
        sequence = existing_count + 1
        order_id = f"{prefix}{sequence:04d}"

        order = Order(
            id=order_id,
            sample_id=sample_id,
            customer_name=customer_name,
            quantity=quantity,
            status="RESERVED",
        )
        self.order_repository.save(order)
        return order

    def approve_order(self, order_id) -> Order:
        order = self.order_repository.find_by_id(order_id)
        sample = self.sample_repository.find_by_id(order.sample_id)

        if sample.stock >= order.quantity:
            sample.stock -= order.quantity
            self.sample_repository.update(sample)

            order.status = "CONFIRMED"
            self.order_repository.update(order)
        else:
            order.status = "PRODUCING"
            self.order_repository.update(order)

        return order

    def reject_order(self, order_id) -> Order:
        order = self.order_repository.find_by_id(order_id)
        order.status = "REJECTED"
        self.order_repository.update(order)
        return order

    def list_reserved_orders(self) -> list:
        return [
            order
            for order in self.order_repository.find_all()
            if order.status == "RESERVED"
        ]
