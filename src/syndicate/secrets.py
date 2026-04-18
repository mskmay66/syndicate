import getpass
from typing import Dict
from .log_config import setup_logging
from .file_manager import add_config_file, read_config_file

logger = setup_logging(__name__, "secrets")

username = getpass.getuser()

REQUIRED_SECRETS = [
    "broker_api_key",
    "broker_secret_key",
    "alpha_vantage_api_key",
    "model_api_key",
]


def add_secret_to_sys(service_name: str, secret: str) -> None:
    """Adds a secret to the file with the service name.

    Args:
        service_name (str): The name of the service the secret is associated with.
        username (str): The username associated with the secret.
        secret (str): The secret value to be stored.
    """
    try:
        add_config_file(
            {"service_name": service_name, "username": username, "secret": secret},
            ".secrets.json",
        )
    except Exception as e:
        logger.error(f"Failed to add secret for {service_name}. Reason: {str(e)}")


def get_secret_from_sys(service_name: str) -> str:
    """Retrieves a secret from the file with the service name.

    Args:
        service_name (str): The name of the service the secret is associated with.

    Returns:
        str: The retrieved secret value.
    """
    try:
        secrets = read_config_file(".secrets.json")
        for secret in secrets:
            if (
                secret["service_name"] == service_name
                and secret["username"] == username
            ):
                logger.info(f"Secret for {service_name} retrieved successfully.")
                return secret["secret"]
        logger.warning(f"No secret found for {service_name} and {username}.")
        return ""
    except Exception as e:
        logger.error(f"Failed to retrieve secret for {service_name}. Reason: {str(e)}")
        return ""


def set_all_secrets(secrets: Dict) -> None:
    """Sets all necessary secrets in the keyring for the application.

    Args:
        secrets (dict): A dictionary containing all secrets needed for the application, with service names as keys and secret values as values.
    """
    assert set(secrets.keys()) == set(REQUIRED_SECRETS), (
        f"Secrets keys must match required secrets: {REQUIRED_SECRETS}"
    )
    records = []
    for service_name, secret in secrets.items():
        records.append(
            {"service_name": service_name, "username": username, "secret": secret}
        )
    add_config_file(records, ".secrets.json")


def load_all_secrets() -> Dict[str, str]:
    """Loads all necessary secrets from the keyring for the application.

    Returns:
        List: A list of all secrets needed for the application, in the order they are expected.
    """
    values = read_config_file(".secrets.json")
    logger.info(f"Loaded secrets from .secrets.json: {values}")
    return {
        v["service_name"]: v["secret"]
        for v in values
        if v["service_name"] in REQUIRED_SECRETS
    }
