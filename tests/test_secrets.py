import pytest
from unittest.mock import MagicMock

import syndicate.secrets as mod


# ------------------------
# Fixtures
# ------------------------


@pytest.fixture
def mock_logger(monkeypatch):
    mock = MagicMock()
    monkeypatch.setattr(mod, "logger", mock)
    return mock


@pytest.fixture
def mock_add_config_file(monkeypatch):
    mock = MagicMock()
    monkeypatch.setattr(mod, "add_config_file", mock)
    return mock


@pytest.fixture
def mock_read_config_file(monkeypatch):
    mock = MagicMock()
    monkeypatch.setattr(mod, "read_config_file", mock)
    return mock


# ------------------------
# add_secret_to_sys
# ------------------------


def test_add_secret_to_sys_success(mock_add_config_file, mock_logger):
    mod.add_secret_to_sys("service", "secret")

    mock_add_config_file.assert_called_once_with(
        {
            "service_name": "service",
            "username": mod.username,
            "secret": "secret",
        },
        ".secrets.json",
    )
    mock_logger.error.assert_not_called()


def test_add_secret_to_sys_failure(
    mock_add_config_file,
    mock_logger,
):
    mock_add_config_file.side_effect = Exception("fail")

    mod.add_secret_to_sys("service", "secret")

    mock_logger.error.assert_called_once()
    assert "Failed to add secret for service" in mock_logger.error.call_args[0][0]


# ------------------------
# get_secret_from_sys
# ------------------------


def test_get_secret_from_sys_success(mock_read_config_file, mock_logger):
    mock_read_config_file.return_value = [
        {
            "service_name": "service",
            "username": mod.username,
            "secret": "mysecret",
        }
    ]

    result = mod.get_secret_from_sys("service")

    assert result == "mysecret"
    mock_logger.info.assert_called_once()


def test_get_secret_from_sys_missing_service(mock_read_config_file, mock_logger):
    mock_read_config_file.return_value = [
        {
            "service_name": "other_service",
            "username": mod.username,
            "secret": "secret",
        }
    ]

    result = mod.get_secret_from_sys("service")

    assert result == ""
    mock_logger.warning.assert_called_once()


def test_get_secret_from_sys_wrong_username(mock_read_config_file, mock_logger):
    mock_read_config_file.return_value = [
        {
            "service_name": "service",
            "username": "other_user",
            "secret": "secret",
        }
    ]

    result = mod.get_secret_from_sys("service")

    assert result == ""
    mock_logger.warning.assert_called_once()


def test_get_secret_from_sys_exception(mock_read_config_file, mock_logger):
    mock_read_config_file.side_effect = Exception("boom")

    result = mod.get_secret_from_sys("service")

    assert result == ""
    mock_logger.error.assert_called_once()
    assert "Failed to retrieve secret for service" in mock_logger.error.call_args[0][0]


# ------------------------
# set_all_secrets
# ------------------------


def test_set_all_secrets_success(mock_add_config_file):
    secrets = {k: f"value_{k}" for k in mod.REQUIRED_SECRETS}

    mod.set_all_secrets(secrets)

    expected_records = [
        {
            "service_name": key,
            "username": mod.username,
            "secret": f"value_{key}",
        }
        for key in mod.REQUIRED_SECRETS
    ]

    mock_add_config_file.assert_called_once_with(
        expected_records,
        ".secrets.json",
    )


def test_set_all_secrets_invalid_keys():
    secrets = {"wrong_key": "value"}

    with pytest.raises(AssertionError):
        mod.set_all_secrets(secrets)


# ------------------------
# load_all_secrets
# ------------------------


def test_load_all_secrets_success(mock_read_config_file, mock_logger):
    mock_read_config_file.return_value = [
        {
            "service_name": "broker_api_key",
            "username": mod.username,
            "secret": "broker-secret",
        },
        {
            "service_name": "model_api_key",
            "username": mod.username,
            "secret": "model-secret",
        },
        {
            "service_name": "not_required",
            "username": mod.username,
            "secret": "ignore-me",
        },
    ]

    result = mod.load_all_secrets()

    assert result == {
        "broker_api_key": "broker-secret",
        "model_api_key": "model-secret",
    }

    mock_logger.info.assert_called_once()


def test_load_all_secrets_empty(mock_read_config_file, mock_logger):
    mock_read_config_file.return_value = []

    result = mod.load_all_secrets()

    assert result == {}
    mock_logger.info.assert_called_once()
