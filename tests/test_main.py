from config import Config
from main import main


def test_main_shows_summary_and_routes_to_sample_menu_before_exit(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(Config, "SAMPLES_FILE", str(tmp_path / "samples.json"))
    monkeypatch.setattr(Config, "ORDERS_FILE", str(tmp_path / "orders.json"))

    inputs = iter(
        [
            "1",  # 메인 메뉴 -> 시료 관리
            "1",  # 시료 관리 -> 등록
            "S-001",
            "실리콘 웨이퍼-8인치",
            "30",
            "0.9",
            "4",  # 시료 관리 -> 메인 메뉴로
            "7",  # 메인 메뉴 -> 종료
        ]
    )
    monkeypatch.setattr("builtins.input", lambda *args: next(inputs))

    main()

    output = capsys.readouterr().out

    assert "등록 시료 수: 0" in output
    assert "1. 시료 관리" in output
    assert "2. 시료 주문" in output
    assert "3. 주문 승인/거절" in output
    assert "4. 생산 라인 조회" in output
    assert "5. 출고 처리" in output
    assert "6. 모니터링" in output
    assert "7. 종료" in output
    assert "S-001" in output
