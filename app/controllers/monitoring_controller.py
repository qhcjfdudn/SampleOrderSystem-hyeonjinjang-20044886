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
