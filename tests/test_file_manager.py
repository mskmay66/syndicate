import pytest

import syndicate.file_manager as mod  # replace with actual import


# ------------------------
# Fixtures
# ------------------------


@pytest.fixture
def temp_dirs(tmp_path, monkeypatch):
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"

    monkeypatch.setattr(mod, "config_dir", str(config_dir))
    monkeypatch.setattr(mod, "data_dir", str(data_dir))

    return config_dir, data_dir


# ------------------------
# Config file tests
# ------------------------


def test_add_and_read_config_file(temp_dirs):
    config_dir, _ = temp_dirs

    data = {"key": "value"}
    mod.add_config_file(data, "test.json")

    file_path = config_dir / "test.json"
    assert file_path.exists()

    result = mod.read_config_file("test.json")
    assert result == data


def test_read_config_file_not_found(temp_dirs):
    with pytest.raises(FileNotFoundError):
        mod.read_config_file("missing.json")


def test_add_config_creates_directory(temp_dirs):
    config_dir, _ = temp_dirs

    assert not config_dir.exists()

    mod.add_config_file({"a": 1}, "file.json")

    assert config_dir.exists()


# ------------------------
# Data file tests
# ------------------------


def test_add_and_read_data_file(temp_dirs):
    _, data_dir = temp_dirs

    data = {"trade": 123}
    mod.add_data_file(data, "data.json")

    file_path = data_dir / "data.json"
    assert file_path.exists()

    result = mod.read_data_file("data.json")
    assert result == data


def test_read_data_file_not_found(temp_dirs):
    with pytest.raises(FileNotFoundError):
        mod.read_data_file("missing.json")


def test_add_data_creates_directory(temp_dirs):
    _, data_dir = temp_dirs

    assert not data_dir.exists()

    mod.add_data_file({"x": 1}, "file.json")

    assert data_dir.exists()


# ------------------------
# Log path tests
# ------------------------


def test_generate_log_path_creates_dir(temp_dirs):
    _, data_dir = temp_dirs

    assert not data_dir.exists()

    path = mod.generate_log_path("service")

    assert data_dir.exists()
    assert path.endswith("service.log")
    assert str(data_dir) in path


def test_generate_log_path_consistency(temp_dirs):
    _, data_dir = temp_dirs

    path1 = mod.generate_log_path("service")
    path2 = mod.generate_log_path("service")

    assert path1 == path2


# ------------------------
# Edge cases
# ------------------------


def test_overwrite_config_file(temp_dirs):
    config_dir, _ = temp_dirs

    mod.add_config_file({"a": 1}, "file.json")
    mod.add_config_file({"a": 2}, "file.json")

    result = mod.read_config_file("file.json")
    assert result["a"] == 2


def test_json_serialization(temp_dirs):
    config_dir, _ = temp_dirs

    data = {"nested": {"list": [1, 2, 3]}}

    mod.add_config_file(data, "nested.json")
    result = mod.read_config_file("nested.json")

    assert result == data
