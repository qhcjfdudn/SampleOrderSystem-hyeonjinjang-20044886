import math


class ProductionLineController:
    def __init__(self, order_repository, sample_repository):
        self.order_repository = order_repository
        self.sample_repository = sample_repository

    def current_production(self) -> dict | None:
        producing_orders = [
            order
            for order in self.order_repository.find_all()
            if order.status == "PRODUCING"
        ]

        if not producing_orders:
            return None

        order = sorted(producing_orders, key=lambda o: o.id)[0]
        sample = self.sample_repository.find_by_id(order.sample_id)

        shortfall = order.quantity - sample.stock
        actual_production = math.ceil(shortfall / sample.yield_rate)
        total_production_time = sample.avg_production_time * actual_production

        return {
            "order": order,
            "shortfall": shortfall,
            "actual_production": actual_production,
            "total_production_time": total_production_time,
        }

    def complete_current_production(self):
        production = self.current_production()

        if production is None:
            return None

        order = production["order"]
        actual_production = production["actual_production"]

        sample = self.sample_repository.find_by_id(order.sample_id)
        sample.stock += actual_production
        sample.stock -= order.quantity
        self.sample_repository.update(sample)

        order.status = "CONFIRMED"
        self.order_repository.update(order)

        return order

    def waiting_orders(self) -> list:
        producing_orders = [
            order
            for order in self.order_repository.find_all()
            if order.status == "PRODUCING"
        ]

        sorted_orders = sorted(producing_orders, key=lambda o: o.id)

        return sorted_orders[1:]
