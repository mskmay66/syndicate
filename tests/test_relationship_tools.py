import json
from unittest.mock import patch, mock_open

from syndicate.tools import get_report, get_reports


SAMPLE_LOG = """[2026-03-19 10:31:26] trader.py:57 - INFO - Report: First report line
continues here
[2026-03-19 10:32:26] trader.py:58 - INFO - Report: Second report
more lines
[2026-03-19 10:33:26] trader.py:59 - INFO - Something else
"""


def test_get_report_parses_multiple_reports():
    with (
        patch("os.path.exists", return_value=True),
        patch("builtins.open", mock_open(read_data=SAMPLE_LOG)),
    ):
        reports = get_report("trader", limit=2)

        assert len(reports) == 2
        assert "First report line" in reports[0]
        assert "Second report" in reports[1]


def test_get_report_respects_limit():
    with (
        patch("os.path.exists", return_value=True),
        patch("builtins.open", mock_open(read_data=SAMPLE_LOG)),
    ):
        reports = get_report("trader", limit=1)

        assert len(reports) == 1


def test_get_report_returns_none_if_file_missing():
    with patch("os.path.exists", return_value=False):
        reports = get_report("trader")

        assert reports is None


def test_get_reports_multiple_agents():
    with (
        patch("os.path.exists", return_value=True),
        patch("builtins.open", mock_open(read_data=SAMPLE_LOG)),
    ):
        result = get_reports.func(["trader", "news_analyst"], limit=1)

        # NOTE: your code has a bug: json.dump instead of json.dumps
        # so this will likely fail — we test expected correct behavior
        assert isinstance(result, str)

        parsed = json.loads(result)
        assert "trader" in parsed
        assert "news_analyst" in parsed
        assert len(parsed["trader"]) == 1


def test_get_reports_handles_exception():
    with patch("os.path.exists", side_effect=Exception("boom")):
        result = get_reports.func(["trader"])

        assert result == "No report found."
