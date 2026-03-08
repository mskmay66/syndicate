import os
import json
from typing import Dict
from platformdirs import user_config_dir, user_data_dir

appname = "syndicate"
appauthor = "mwmay"

config_dir = user_config_dir(appname, appauthor)
data_dir = user_data_dir(appname, appauthor)


def add_config_file(data: Dict, name: str):
    """Adds a config file to the config directory.

    Args:
        json (Dict): The config data to be written to the file.
        name (str): The name of the config file (e.g., "agent.json", "watchlist.json").
    """
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)

    with open(os.path.join(config_dir, name), "w") as f:
        json.dump(data, f, indent=2)


def read_config_file(name: str) -> Dict:
    """Reads a config file from the config directory.

    Args:
        name (str): The name of the config file to read (e.g., "agent.json", "watchlist.json").

    Returns:
        Dict: The contents of the config file as a dictionary.

    Raises:
        FileNotFoundError: If the specified config file does not exist in the config directory.
    """
    file_path = os.path.join(config_dir, name)
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"{name} not found in config directory.")

    with open(file_path, "r") as f:
        return json.load(f)


def add_data_file(data: Dict, name: str):
    """Adds a data file to the data directory.

    Args:
        json (Dict): The data to be written to the file.
        name (str): The name of the data file (e.g., "trade_history.json").
    """
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    with open(os.path.join(data_dir, name), "w") as f:
        json.dump(data, f, indent=2)


def read_data_file(name: str) -> Dict:
    """Reads a data file from the data directory.

    Args:
        name (str): The name of the data file to read (e.g., "trade_history.json").

    Returns:
        Dict: The contents of the data file as a dictionary.
    """
    file_path = os.path.join(data_dir, name)
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"{name} not found in data directory.")

    with open(file_path, "r") as f:
        return json.load(f)
