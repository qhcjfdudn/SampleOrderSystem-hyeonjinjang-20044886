from config import Config


def test_config_has_data_file_paths():
    assert Config.SAMPLES_FILE == "data/samples.json"
    assert Config.ORDERS_FILE == "data/orders.json"
