from unittest.mock import MagicMock, patch
import pandas as pd
import json

from syndicate.tools import FundementalTools


class DummyUser:
    pass


def test_convert_timestamp_cols():
    df = pd.DataFrame(
        {
            pd.Timestamp("2024-01-01"): [1, 2],
            "normal_col": [3, 4],
        }
    )

    result = FundementalTools._convert_timestamp_cols(df)

    assert "2024-01-01" in result.columns
    assert "normal_col" in result.columns


@patch("syndicate.tools.fundemetal_analysis.yf.Ticker")
def test_get_fundementals_success(mock_ticker):
    mock_stock = MagicMock()
    mock_stock.info = {
        "marketCap": 100,
        "trailingPE": 10,
        "priceToBook": 2,
        "returnOnEquity": 0.2,
        "trailingEps": 5,
        "payoutRatio": 0.3,
        "dividendYield": 0.01,
        "fiftyTwoWeekHigh": 200,
        "fiftyTwoWeekLow": 100,
    }

    mock_ticker.return_value = mock_stock

    tools = FundementalTools(DummyUser())
    get_fundementals = tools.build_tools()[0].func

    result = get_fundementals(["AAPL"])
    parsed = json.loads(result)

    assert parsed["AAPL"]["market_cap"] == 100
    assert parsed["AAPL"]["pe_ratio"] == 10


@patch("syndicate.tools.fundemetal_analysis.yf.Ticker")
def test_get_fundementals_single_string(mock_ticker):
    mock_stock = MagicMock()
    mock_stock.info = {}
    mock_ticker.return_value = mock_stock

    tools = FundementalTools(DummyUser())
    get_fundementals = tools.build_tools()[0].func

    result = get_fundementals("AAPL")
    parsed = json.loads(result)

    assert "AAPL" in parsed


@patch("syndicate.tools.fundemetal_analysis.yf.Ticker", side_effect=Exception("fail"))
def test_get_fundementals_error(mock_ticker):
    tools = FundementalTools(DummyUser())
    get_fundementals = tools.build_tools()[0].func

    result = get_fundementals(["AAPL"])
    parsed = json.loads(result)

    assert "error" in parsed["AAPL"]


@patch("syndicate.tools.fundemetal_analysis.yf.Ticker")
def test_get_balance_sheet_success(mock_ticker):
    df = pd.DataFrame({pd.Timestamp("2024-01-01"): [100]})

    mock_stock = MagicMock()
    mock_stock.balance_sheet = df
    mock_ticker.return_value = mock_stock

    tools = FundementalTools(DummyUser())
    _, get_balance_sheet, _, _ = tools.build_tools()

    result = get_balance_sheet.func(["AAPL"])
    parsed = json.loads(result)

    assert "AAPL" in parsed
    assert "2024-01-01" in parsed["AAPL"]


@patch("syndicate.tools.fundemetal_analysis.yf.Ticker")
def test_get_income_statement_success(mock_ticker):
    df = pd.DataFrame({pd.Timestamp("2024-01-01"): [200]})

    mock_stock = MagicMock()
    mock_stock.income_stmt = df
    mock_ticker.return_value = mock_stock

    tools = FundementalTools(DummyUser())
    _, _, get_income_statement, _ = tools.build_tools()

    result = get_income_statement.func(["AAPL"])
    parsed = json.loads(result)

    assert "AAPL" in parsed


@patch("syndicate.tools.fundemetal_analysis.yf.Ticker")
def test_get_cashflow_success(mock_ticker):
    df = pd.DataFrame({pd.Timestamp("2024-01-01"): [300]})

    mock_stock = MagicMock()
    mock_stock.cashflow = df
    mock_ticker.return_value = mock_stock

    tools = FundementalTools(DummyUser())
    _, _, _, get_cashflow = tools.build_tools()

    result = get_cashflow.func(["AAPL"])
    parsed = json.loads(result)

    assert "AAPL" in parsed


@patch("syndicate.tools.fundemetal_analysis.yf.Ticker", side_effect=Exception("boom"))
def test_financial_tools_error(mock_ticker):
    tools = FundementalTools(DummyUser())
    _, get_balance_sheet, get_income_statement, get_cashflow = tools.build_tools()

    for fn in [get_balance_sheet, get_income_statement, get_cashflow]:
        result = fn.func(["AAPL"])
        parsed = json.loads(result)

        assert "error" in parsed["AAPL"]


@patch("syndicate.tools.fundemetal_analysis.yf.Ticker")
def test_multiple_tickers(mock_ticker):
    df = pd.DataFrame({pd.Timestamp("2024-01-01"): [1]})

    mock_stock = MagicMock()
    mock_stock.balance_sheet = df
    mock_stock.income_stmt = df
    mock_stock.cashflow = df
    mock_stock.info = {}

    mock_ticker.return_value = mock_stock

    tools = FundementalTools(DummyUser())
    get_fundementals, get_balance_sheet, _, _ = tools.build_tools()

    result = get_balance_sheet.func(["AAPL", "GOOG"])
    parsed = json.loads(result)

    assert "AAPL" in parsed
    assert "GOOG" in parsed
