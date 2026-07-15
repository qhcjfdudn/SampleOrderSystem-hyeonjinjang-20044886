from app.models.sample import Sample
from app.models.sample_repository import SampleRepository


def test_save_and_find_by_id_returns_sample_with_same_field_values(tmp_path):
    file_path = tmp_path / "samples.json"
    repository = SampleRepository(str(file_path))
    sample = Sample(
        id="S-001",
        name="실리콘 웨이퍼-8인치",
        avg_production_time=30,
        yield_rate=0.9,
        stock=100,
    )

    repository.save(sample)
    found = repository.find_by_id("S-001")

    assert found is not None
    assert found.id == sample.id
    assert found.name == sample.name
    assert found.avg_production_time == sample.avg_production_time
    assert found.yield_rate == sample.yield_rate
    assert found.stock == sample.stock
