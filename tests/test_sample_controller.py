from app.controllers.sample_controller import SampleController
from app.models.sample_repository import SampleRepository


def test_register_creates_sample_with_zero_stock_and_saves_it(tmp_path):
    file_path = tmp_path / "samples.json"
    repository = SampleRepository(str(file_path))
    controller = SampleController(repository)

    registered = controller.register("S-001", "실리콘 웨이퍼-8인치", 30, 0.9)

    assert registered.id == "S-001"
    assert registered.name == "실리콘 웨이퍼-8인치"
    assert registered.avg_production_time == 30
    assert registered.yield_rate == 0.9
    assert registered.stock == 0

    found = repository.find_by_id("S-001")
    assert found is not None
    assert found.id == registered.id
    assert found.name == registered.name
    assert found.avg_production_time == registered.avg_production_time
    assert found.yield_rate == registered.yield_rate
    assert found.stock == 0


def test_list_samples_returns_all_registered_samples(tmp_path):
    file_path = tmp_path / "samples.json"
    repository = SampleRepository(str(file_path))
    controller = SampleController(repository)

    controller.register("S-001", "실리콘 웨이퍼-8인치", 30, 0.9)
    controller.register("S-002", "GaN 웨이퍼-6인치", 45, 0.85)

    samples = controller.list_samples()

    assert len(samples) == 2
    assert {sample.id for sample in samples} == {"S-001", "S-002"}
    assert all(sample.stock == 0 for sample in samples)
