from data_persistence import DataPersistence

from app.models.sample import Sample


class SampleRepository:
    def __init__(self, file_path):
        self._data_persistence = DataPersistence(file_path)

    def save(self, sample: Sample) -> None:
        record = {
            "id": sample.id,
            "name": sample.name,
            "avg_production_time": sample.avg_production_time,
            "yield_rate": sample.yield_rate,
            "stock": sample.stock,
        }
        self._data_persistence.create(record)

    def update(self, sample: Sample) -> None:
        record = {
            "id": sample.id,
            "name": sample.name,
            "avg_production_time": sample.avg_production_time,
            "yield_rate": sample.yield_rate,
            "stock": sample.stock,
        }
        self._data_persistence.update(sample.id, record)

    def find_by_id(self, id):
        record = self._data_persistence.read(id)
        if record is None:
            return None
        return Sample(**record)

    def find_all(self) -> list:
        records = self._data_persistence.read_all()
        return [Sample(**record) for record in records]
