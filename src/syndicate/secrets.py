import os
import keyring
import logging

logger = logging.getLogger(__name__)


def add_secret_to_keyring(service_name: str, username: str, secret: str) -> None:
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


def get_secret_from_keyring(service_name: str, username: str) -> str:
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


def set_env_vars(secret: str, service: str) -> None:
    """
    Set environment variables for the given secrets.

    Args:
        secrets (Dict[str, str]): A dictionary of secrets where the key is the environment variable name and the value is the secret value.
    """
    if secret:
        os.environ[service] = secret
        logger.info(f"Environment variable {service} set successfully.")
    else:
        logger.warning(f"Secret for {service} is empty. Environment variable not set.")
