from app.models.sample import Sample


def test_sample_stores_all_field_values():
    sample = Sample(
        id="S-001",
        name="실리콘 웨이퍼-8인치",
        avg_production_time=10,
        yield_rate=0.9,
        stock=50,
    )

    assert sample.id == "S-001"
    assert sample.name == "실리콘 웨이퍼-8인치"
    assert sample.avg_production_time == 10
    assert sample.yield_rate == 0.9
    assert sample.stock == 50
