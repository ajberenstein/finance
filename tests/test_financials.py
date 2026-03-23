"""Tests for financial statement tools."""
import json
from unittest.mock import patch

import pandas as pd
import pytest

from tests.conftest import make_ticker_mock


def _make_financials_df() -> pd.DataFrame:
    # Columns are dates, index rows are financial line items — mirrors yfinance output.
    return pd.DataFrame(
        {"2023-12-31": [100_000, 80_000], "2022-12-31": [90_000, 72_000]},
        index=["TotalRevenue", "GrossProfit"],
    )


def _assert_financials_result(result: dict) -> None:
    """_df_to_json serialises with dates as top-level keys; line items are nested."""
    assert "2023-12-31" in result
    assert result["2023-12-31"]["TotalRevenue"] == 100_000


class TestGetIncomeStatement:
    def test_annual_returns_income_stmt(self):
        df = _make_financials_df()
        mock_ticker = make_ticker_mock(income_stmt=df, quarterly_income_stmt=pd.DataFrame())
        with patch("yahoo_finance_mcp.server.yf.Ticker", return_value=mock_ticker):
            from yahoo_finance_mcp.server import get_income_statement
            result = json.loads(get_income_statement("AAPL", quarterly=False))
        _assert_financials_result(result)

    def test_quarterly_uses_quarterly_attr(self):
        df = _make_financials_df()
        mock_ticker = make_ticker_mock(income_stmt=pd.DataFrame(), quarterly_income_stmt=df)
        with patch("yahoo_finance_mcp.server.yf.Ticker", return_value=mock_ticker):
            from yahoo_finance_mcp.server import get_income_statement
            result = json.loads(get_income_statement("AAPL", quarterly=True))
        _assert_financials_result(result)

    def test_empty_returns_no_data(self):
        mock_ticker = make_ticker_mock(income_stmt=pd.DataFrame())
        with patch("yahoo_finance_mcp.server.yf.Ticker", return_value=mock_ticker):
            from yahoo_finance_mcp.server import get_income_statement
            result = json.loads(get_income_statement("FAKE"))
        assert result == {"message": "No data available"}


class TestGetBalanceSheet:
    def test_annual_returns_balance_sheet(self):
        df = _make_financials_df()
        mock_ticker = make_ticker_mock(balance_sheet=df, quarterly_balance_sheet=pd.DataFrame())
        with patch("yahoo_finance_mcp.server.yf.Ticker", return_value=mock_ticker):
            from yahoo_finance_mcp.server import get_balance_sheet
            result = json.loads(get_balance_sheet("AAPL"))
        _assert_financials_result(result)

    def test_quarterly_uses_quarterly_attr(self):
        df = _make_financials_df()
        mock_ticker = make_ticker_mock(balance_sheet=pd.DataFrame(), quarterly_balance_sheet=df)
        with patch("yahoo_finance_mcp.server.yf.Ticker", return_value=mock_ticker):
            from yahoo_finance_mcp.server import get_balance_sheet
            result = json.loads(get_balance_sheet("AAPL", quarterly=True))
        _assert_financials_result(result)


class TestGetCashFlow:
    def test_annual_returns_cashflow(self):
        df = _make_financials_df()
        mock_ticker = make_ticker_mock(cashflow=df, quarterly_cashflow=pd.DataFrame())
        with patch("yahoo_finance_mcp.server.yf.Ticker", return_value=mock_ticker):
            from yahoo_finance_mcp.server import get_cash_flow
            result = json.loads(get_cash_flow("AAPL"))
        _assert_financials_result(result)

    def test_quarterly_uses_quarterly_attr(self):
        df = _make_financials_df()
        mock_ticker = make_ticker_mock(cashflow=pd.DataFrame(), quarterly_cashflow=df)
        with patch("yahoo_finance_mcp.server.yf.Ticker", return_value=mock_ticker):
            from yahoo_finance_mcp.server import get_cash_flow
            result = json.loads(get_cash_flow("AAPL", quarterly=True))
        _assert_financials_result(result)
