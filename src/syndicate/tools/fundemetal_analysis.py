import json
from typing import List
import pandas as pd
import yfinance as yf

from langchain_core.tools import tool
from ..models import User


class FundementalTools:
    def __init__(self, user: User) -> None:
        self.user = user

    @staticmethod
    def _convert_timestamp_cols(df):
        for col in df.columns:
            if isinstance(col, pd.Timestamp):
                df.rename(columns={col: col.strftime("%Y-%m-%d")}, inplace=True)
        return df

    def build_tools(self):
        @tool(
            "get_fundementals",
            return_direct=True,
            description="Gets the fundementals for a given ticker or list of tickers using yfinance. Example usage: get_fundementals('AAPL') or get_fundementals(['AAPL', 'GOOG'])",
        )
        def get_fundementals(tickers: List[str]) -> str:
            """Gets the fundementals for a given ticker using yfinance.

            Args:
                ticker (str): The ticker to get the fundementals for.

            Returns:
                str: The fundementals for the given ticker in JSON format.
            """
            if isinstance(tickers, str):
                tickers = [tickers]
            fundementals = {}
            for ticker in tickers:
                try:
                    stock = yf.Ticker(ticker)
                    fundementals[ticker] = {
                        "market_cap": stock.info.get("marketCap"),
                        "pe_ratio": stock.info.get("trailingPE"),
                        "pb_ratio": stock.info.get("priceToBook"),
                        "roe": stock.info.get("returnOnEquity"),
                        "eps": stock.info.get("trailingEps"),
                        "payout_ratio": stock.info.get("payoutRatio"),
                        "dividend_yield": stock.info.get("dividendYield"),
                        "fifty_two_week_high": stock.info.get("fiftyTwoWeekHigh"),
                        "fifty_two_week_low": stock.info.get("fiftyTwoWeekLow"),
                    }
                except Exception as e:
                    fundementals[ticker] = {"error": str(e)}
            return json.dumps(fundementals, indent=2, default=str)

        @tool(
            "get_balance_sheet",
            return_direct=True,
            description="Gets the balance sheet for a given ticker or list of tickers using yfinance. Example usage: get_balance_sheet('AAPL') or get_balance_sheet(['AAPL', 'GOOG'])",
        )
        def get_balance_sheet(tickers: List[str]) -> str:
            """Gets the balance sheet for a given ticker or list of tickers using yfinance.

            Args:
                tickers (List[str]): The ticker or list of tickers to get the balance sheet for.

            Returns:
                str: The balance sheet for the given ticker or list of tickers in JSON format.
            """
            if isinstance(tickers, str):
                tickers = [tickers]
            balance_sheets = {}
            for ticker in tickers:
                try:
                    stock = yf.Ticker(ticker)
                    balance_sheets[ticker] = self._convert_timestamp_cols(
                        stock.balance_sheet
                    ).to_dict()
                except Exception as e:
                    balance_sheets[ticker] = {"error": str(e)}
            return json.dumps(balance_sheets, indent=2, default=str)

        @tool(
            "get_income_statement",
            return_direct=True,
            description="Gets the income statement for a given ticker or list of tickers using yfinance. Example usage: get_income_statement('AAPL') or get_income_statement(['AAPL', 'GOOG'])",
        )
        def get_income_statement(tickers: List[str]) -> str:
            """Gets the income statement for a given ticker or list of tickers using yfinance.

            Args:
                tickers (List[str]): The ticker or list of tickers to get the income statement for.

            Returns:
                str: The income statement for the given ticker or list of tickers in JSON format.
            """
            if isinstance(tickers, str):
                tickers = [tickers]
            income_statements = {}
            for ticker in tickers:
                try:
                    stock = yf.Ticker(ticker)
                    income_statements[ticker] = self._convert_timestamp_cols(
                        stock.income_stmt
                    ).to_dict()
                except Exception as e:
                    income_statements[ticker] = {"error": str(e)}
            return json.dumps(income_statements, indent=2, default=str)

        @tool(
            "get_cashflow",
            return_direct=True,
            description="Gets the cashflow statement for a given ticker or list of tickers using yfinance. Example usage: get_cashflow('AAPL') or get_cashflow(['AAPL', 'GOOG'])",
        )
        def get_cashflow(tickers: List[str]) -> str:
            """Gets the cashflow statement for a given ticker or list of tickers using yfinance.

            Args:
                tickers (List[str]): The ticker or list of tickers to get the cashflow statement for.

            Returns:
                str: The cashflow statement for the given ticker or list of tickers in JSON format.
            """
            if isinstance(tickers, str):
                tickers = [tickers]
            cashflows = {}
            for ticker in tickers:
                try:
                    stock = yf.Ticker(ticker)
                    cashflows[ticker] = self._convert_timestamp_cols(
                        stock.cashflow
                    ).to_dict()
                except Exception as e:
                    cashflows[ticker] = {"error": str(e)}
            return json.dumps(cashflows, indent=2, default=str)

        return [get_fundementals, get_balance_sheet, get_income_statement, get_cashflow]
