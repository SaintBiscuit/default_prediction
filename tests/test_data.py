from src.data.make_dataset import load_and_split_data


def test_valid_path():
    assert load_and_split_data("data/raw/UCI_Credit_Card.csv") == True


def test_invalid_path():
    assert load_and_split_data("data/models/UCI_Credit_Card.csv") == False


def test_invalid_data():
    assert load_and_split_data("data/models/UCI_Credit_Card.csv") == False
