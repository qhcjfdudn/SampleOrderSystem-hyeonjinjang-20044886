from data_persistence import DataPersistence

from app.models.order import Order


class OrderRepository:
    def __init__(self, file_path):
        self._data_persistence = DataPersistence(file_path)

    def save(self, order: Order) -> None:
        record = {
            "id": order.id,
            "sample_id": order.sample_id,
            "customer_name": order.customer_name,
            "quantity": order.quantity,
            "status": order.status,
        }
        self._data_persistence.create(record)

    def update(self, order: Order) -> None:
        record = {
            "id": order.id,
            "sample_id": order.sample_id,
            "customer_name": order.customer_name,
            "quantity": order.quantity,
            "status": order.status,
        }
        self._data_persistence.update(order.id, record)

    def find_by_id(self, id):
        record = self._data_persistence.read(id)
        if record is None:
            return None
        return Order(**record)

    def find_all(self) -> list:
        records = self._data_persistence.read_all()
        return [Order(**record) for record in records]
