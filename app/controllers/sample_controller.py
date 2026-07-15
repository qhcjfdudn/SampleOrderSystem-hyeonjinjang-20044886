from app.models.sample import Sample


class SampleController:
    def __init__(self, sample_repository):
        self.sample_repository = sample_repository

    def register(self, id, name, avg_production_time, yield_rate):
        sample = Sample(
            id=id,
            name=name,
            avg_production_time=avg_production_time,
            yield_rate=yield_rate,
            stock=0,
        )
        self.sample_repository.save(sample)
        return sample

    def list_samples(self) -> list:
        return self.sample_repository.find_all()
