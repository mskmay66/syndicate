import pytest
from unittest.mock import MagicMock

import syndicate.secrets as mod  # replace with actual import


# ------------------------
# Fixtures
# ------------------------


@pytest.fixture
def mock_keyring(monkeypatch):
    mock = MagicMock()
    monkeypatch.setattr(mod, "keyring", mock)
    return mock


@pytest.fixture
def mock_logger(monkeypatch):
    mock = MagicMock()
    monkeypatch.setattr(mod, "logger", mock)
    return mock


# ------------------------
# add_secret_to_keyring
# ------------------------


def test_add_secret_success(mock_keyring, mock_logger):
    mod.add_secret_to_keyring("service", "secret")

    mock_keyring.set_password.assert_called_once_with("service", mod.username, "secret")
    mock_logger.info.assert_called_once()


def test_add_secret_failure(mock_keyring, mock_logger):
    mock_keyring.set_password.side_effect = Exception("fail")

    mod.add_secret_to_keyring("service", "secret")

    mock_logger.error.assert_called_once()
    assert "Failed to add secret" in mock_logger.error.call_args[0][0]


# ------------------------
# get_secret_from_keyring
# ------------------------


def test_get_secret_success(mock_keyring, mock_logger):
    mock_keyring.get_password.return_value = "mysecret"

    result = mod.get_secret_from_keyring("service")

    assert result == "mysecret"
    mock_logger.info.assert_called_once()


def test_get_secret_missing(mock_keyring, mock_logger):
    mock_keyring.get_password.return_value = None

    result = mod.get_secret_from_keyring("service")

    assert result == ""
    mock_logger.warning.assert_called_once()


def test_get_secret_exception(mock_keyring, mock_logger):
    mock_keyring.get_password.side_effect = Exception("boom")

    result = mod.get_secret_from_keyring("service")

    assert result == ""
    mock_logger.error.assert_called_once()


# ------------------------
# set_all_secrets
# ------------------------


def test_set_all_secrets_success(monkeypatch):
    calls = []

    def fake_add(service, secret):
        calls.append((service, secret))

    monkeypatch.setattr(mod, "add_secret_to_keyring", fake_add)

    secrets = {k: f"value_{k}" for k in mod.REQUIRED_SECRETS}

    mod.set_all_secrets(secrets)

    assert len(calls) == len(mod.REQUIRED_SECRETS)
    for k in mod.REQUIRED_SECRETS:
        assert (k, f"value_{k}") in calls


def test_set_all_secrets_invalid_keys():
    secrets = {"wrong_key": "value"}

    with pytest.raises(AssertionError):
        mod.set_all_secrets(secrets)


# ------------------------
# load_all_secrets
# ------------------------


def test_load_all_secrets(monkeypatch):
    def fake_get(service):
        return f"value_{service}"

    monkeypatch.setattr(mod, "get_secret_from_keyring", fake_get)

    result = mod.load_all_secrets()

    assert isinstance(result, dict)
    for key in mod.REQUIRED_SECRETS:
        assert result[key] == f"value_{key}"
