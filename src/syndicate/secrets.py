import getpass
import keyring
from .log_config import setup_logging

logger = setup_logging(__name__, "secrets")

username = getpass.getuser()


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
