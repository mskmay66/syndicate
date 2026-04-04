import getpass
import keyring
from typing import Dict
from .log_config import setup_logging

logger = setup_logging(__name__, "secrets")

username = getpass.getuser()

REQUIRED_SECRETS = [
    "broker_api_key",
    "broker_secret_key",
    "alpha_vantage_api_key",
    "model_api_key",
]


def add_secret_to_keyring(service_name: str, secret: str) -> None:
    """
    Add a secret to the keyring.

    Args:
        service_name (str): The name of the service the secret is associated with.
        username (str): The username associated with the secret.
        secret (str): The secret value to be stored.
    """
    try:
        keyring.set_password(service_name, username, secret)
        logger.info(f"Secret for {service_name} added successfully.")
    except Exception as e:
        logger.error(f"Failed to add secret for {service_name}. Reason: {str(e)}")


def get_secret_from_keyring(service_name: str) -> str:
    """
    Retrieve a secret from the keyring.

    Args:
        service_name (str): The name of the service the secret is associated with.
        username (str): The username associated with the secret.

    Returns:
        str: The retrieved secret value.
    """
    try:
        secret = keyring.get_password(service_name, username)
        if secret is None:
            logger.warning(f"No secret found for {service_name} and {username}.")
            return ""
        logger.info(f"Secret for {service_name} retrieved successfully.")
        return secret
    except Exception as e:
        logger.error(f"Failed to retrieve secret for {service_name}. Reason: {str(e)}")
        return ""


def set_all_secrets(secrets: Dict) -> None:
    """Sets all necessary secrets in the keyring for the application.

    Args:
        secrets (dict): A dictionary containing all secrets needed for the application,
        with service names as keys and secret values as values.
    """
    assert set(secrets.keys()) == set(REQUIRED_SECRETS), (
        f"Secrets keys must match required secrets: {REQUIRED_SECRETS}"
    )
    for service_name, secret in secrets.items():
        add_secret_to_keyring(service_name, secret)


def load_all_secrets() -> Dict[str, str]:
    """Loads all necessary secrets from the keyring for the application.

    Returns:
        List: A list of all secrets needed for the application, in the order they are expected.
    """
    return {k: get_secret_from_keyring(k) for k in REQUIRED_SECRETS}
