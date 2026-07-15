from app.controllers.sample_controller import SampleController
from app.models.sample_repository import SampleRepository
from app.views.sample_view import run_sample_menu


def test_run_sample_menu_registers_lists_and_searches_samples(tmp_path, monkeypatch, capsys):
    sample_repository = SampleRepository(str(tmp_path / "samples.json"))
    sample_controller = SampleController(sample_repository)

    inputs = iter(
        [
            "1",
            "S-001",
            "실리콘 웨이퍼-8인치",
            "30",
            "0.9",
            "2",
            "3",
            "실리콘",
            "4",
        ]
    )
    monkeypatch.setattr("builtins.input", lambda *args: next(inputs))

    run_sample_menu(sample_controller)

    output = capsys.readouterr().out

    assert "S-001" in output
    assert output.count("실리콘 웨이퍼-8인치") >= 2
    assert "재고 0" in output
