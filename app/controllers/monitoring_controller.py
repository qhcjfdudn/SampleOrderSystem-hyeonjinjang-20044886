class MonitoringController:
    def __init__(self, order_repository, sample_repository):
        self.order_repository = order_repository
        self.sample_repository = sample_repository

    def order_status_counts(self) -> dict:
        counts = {"RESERVED": 0, "CONFIRMED": 0, "PRODUCING": 0, "RELEASE": 0}
        for order in self.order_repository.find_all():
            if order.status in counts:
                counts[order.status] += 1
        return counts

    def sample_stock_status(self) -> list:
        demand_by_sample = {}
        for order in self.order_repository.find_all():
            if order.status in ("RESERVED", "PRODUCING"):
                demand_by_sample[order.sample_id] = (
                    demand_by_sample.get(order.sample_id, 0) + order.quantity
                )

        result = []
        for sample in self.sample_repository.find_all():
            demand = demand_by_sample.get(sample.id, 0)
            if sample.stock == 0:
                status = "고갈"
            elif sample.stock < demand:
                status = "부족"
            else:
                status = "여유"
            result.append({"sample": sample, "demand": demand, "status": status})
        return result
