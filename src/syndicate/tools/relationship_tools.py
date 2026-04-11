import os
import re
import getpass
import json
from typing import List
from platformdirs import user_data_dir
from langchain_core.tools import tool

appname = "syndicate"
appuser = getpass.getuser()

data_dir = user_data_dir(appname, appuser)
log_pattern = re.compile(
    r"^\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\] \w+\.py:\d+ - INFO - Report: ([\s\S]*?)(?=^\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\]|\Z)",
    re.MULTILINE,
)


def get_report(agent: str, limit: int = 3):
    """Gets the reports of other agents from the log files.

    Args:
        agent (str): The name of the agent whose reports you want to get. Available agents are trader, technical_analyst, news_analyst, fundementals_analyst.
        limit (int, optional): The maximum number of reports to retrieve. Defaults to 3.

    Returns:
        _type_: A list of reports from the specified agent, limited to the specified number.
    """
    log_path = os.path.join(data_dir, agent + ".log")
    if not os.path.exists(log_path):
        return

    with open(log_path, "r") as f:
        content = f.read()

    reports = re.findall(log_pattern, content)
    return reports[:limit]


@tool(
    "get_reports",
    return_direct=True,
    description="Gets the reports of other agents. Available agests are trader, technical_analyst, news_analyst, fundementals_analyst. Limit controls how many you get for each",
)
def get_reports(agents: List[str], limit: int = 3):
    """Gets the reports of other agents from the log files.

    Args:
        agents (List[str]): A list of agent names whose reports you want to get. Available agents are trader, technical_analyst, news_analyst, fundementals_analyst.
        limit (int, optional): The maximum number of reports to retrieve. Defaults to 3.

    Returns:
        str: A JSON string containing the reports from the specified agents, limited to the specified number for each agent. The JSON object will have agent names as keys and lists of reports as values. If no reports are found for any of the specified agents, a message indicating that no report was found will be returned.
    """
    try:
        reports = {}
        for agent in agents:
            reports[agent] = get_report(agent, limit)
        return json.dumps(reports)
    except Exception:
        return "No report found."
