"""Tests for error handling and edge cases in tools with try/except blocks."""
import json
from unittest.mock import MagicMock, PropertyMock, patch

import pandas as pd

from tests.conftest import make_ticker_mock, sample_ohlcv_df


class TestGetCapitalGains:
    def test_returns_data_when_available(self):
        df = sample_ohlcv_df(3)
        mock_ticker = make_ticker_mock()
        mock_ticker.get_capital_gains.return_value = df
        with patch("yahoo_finance_mcp.server.yf.Ticker", return_value=mock_ticker):
            from yahoo_finance_mcp.server import get_capital_gains
            result = json.loads(get_capital_gains("SPY"))
        assert "Close" in result

    def test_returns_message_on_exception(self):
        mock_ticker = make_ticker_mock()
        mock_ticker.get_capital_gains.side_effect = Exception("no data")
        with patch("yahoo_finance_mcp.server.yf.Ticker", return_value=mock_ticker):
            from yahoo_finance_mcp.server import get_capital_gains
            result = json.loads(get_capital_gains("AAPL"))
        assert "message" in result


class TestGetAnalystPriceTargets:
    def test_returns_dict_data(self):
        targets = {"low": 150.0, "mean": 200.0, "high": 250.0, "current": 195.0}
        mock_ticker = make_ticker_mock(analyst_price_targets=targets)
        with patch("yahoo_finance_mcp.server.yf.Ticker", return_value=mock_ticker):
            from yahoo_finance_mcp.server import get_analyst_price_targets
            result = json.loads(get_analyst_price_targets("AAPL"))
        assert result["mean"] == 200.0

    def test_returns_message_on_exception(self):
        mock_ticker = MagicMock()
        type(mock_ticker).analyst_price_targets = PropertyMock(side_effect=Exception("unavailable"))
        with patch("yahoo_finance_mcp.server.yf.Ticker", return_value=mock_ticker):
            from yahoo_finance_mcp.server import get_analyst_price_targets
            result = json.loads(get_analyst_price_targets("FAKE"))
        assert "message" in result


class TestGetIsin:
    def test_returns_isin_when_available(self):
        mock_ticker = make_ticker_mock(isin="US0378331005")
        with patch("yahoo_finance_mcp.server.yf.Ticker", return_value=mock_ticker):
            from yahoo_finance_mcp.server import get_isin
            result = json.loads(get_isin("AAPL"))
        assert result["isin"] == "US0378331005"

    def test_returns_message_on_exception(self):
        mock_ticker = MagicMock()
        type(mock_ticker).isin = PropertyMock(side_effect=Exception("not available"))
        with patch("yahoo_finance_mcp.server.yf.Ticker", return_value=mock_ticker):
            from yahoo_finance_mcp.server import get_isin
            result = json.loads(get_isin("FAKE"))
        assert "message" in result


class TestGetOptionsChain:
    def test_returns_calls_and_puts(self):
        calls_df = pd.DataFrame({"strike": [150, 155], "lastPrice": [5.0, 3.0]})
        puts_df = pd.DataFrame({"strike": [145, 140], "lastPrice": [4.0, 2.0]})
        chain = MagicMock()
        chain.calls = calls_df
        chain.puts = puts_df

        mock_ticker = make_ticker_mock()
        mock_ticker.options = ("2024-03-15", "2024-04-19")
        mock_ticker.option_chain.return_value = chain

        with patch("yahoo_finance_mcp.server.yf.Ticker", return_value=mock_ticker):
            from yahoo_finance_mcp.server import get_options_chain
            result = json.loads(get_options_chain("AAPL"))
        assert "calls" in result
        assert "puts" in result
        assert result["expiration"] == "2024-03-15"

    def test_returns_message_when_no_options(self):
        mock_ticker = make_ticker_mock()
        mock_ticker.options = ()
        with patch("yahoo_finance_mcp.server.yf.Ticker", return_value=mock_ticker):
            from yahoo_finance_mcp.server import get_options_chain
            result = json.loads(get_options_chain("FAKE"))
        assert "message" in result

    def test_uses_requested_expiration_if_valid(self):
        calls_df = pd.DataFrame({"strike": [150]})
        puts_df = pd.DataFrame({"strike": [145]})
        chain = MagicMock()
        chain.calls = calls_df
        chain.puts = puts_df

        mock_ticker = make_ticker_mock()
        mock_ticker.options = ("2024-03-15", "2024-04-19")
        mock_ticker.option_chain.return_value = chain

        with patch("yahoo_finance_mcp.server.yf.Ticker", return_value=mock_ticker):
            from yahoo_finance_mcp.server import get_options_chain
            get_options_chain("AAPL", expiration="2024-04-19")
        mock_ticker.option_chain.assert_called_once_with("2024-04-19")

    def test_falls_back_to_first_expiration_if_invalid(self):
        calls_df = pd.DataFrame({"strike": [150]})
        puts_df = pd.DataFrame({"strike": [145]})
        chain = MagicMock()
        chain.calls = calls_df
        chain.puts = puts_df

        mock_ticker = make_ticker_mock()
        mock_ticker.options = ("2024-03-15", "2024-04-19")
        mock_ticker.option_chain.return_value = chain

        with patch("yahoo_finance_mcp.server.yf.Ticker", return_value=mock_ticker):
            from yahoo_finance_mcp.server import get_options_chain
            get_options_chain("AAPL", expiration="9999-99-99")
        mock_ticker.option_chain.assert_called_once_with("2024-03-15")


class TestTtmTools:
    def test_ttm_income_statement_returns_data(self):
        # Columns are date labels, rows are line items — same orientation as yfinance.
        df = pd.DataFrame({"2024": [1000]}, index=["Revenue"])
        mock_ticker = make_ticker_mock(ttm_income_stmt=df)
        with patch("yahoo_finance_mcp.server.yf.Ticker", return_value=mock_ticker):
            from yahoo_finance_mcp.server import get_ttm_income_statement
            result = json.loads(get_ttm_income_statement("AAPL"))
        assert "2024" in result
        assert result["2024"]["Revenue"] == 1000

    def test_ttm_income_statement_returns_message_on_exception(self):
        mock_ticker = MagicMock()
        type(mock_ticker).ttm_income_stmt = PropertyMock(side_effect=Exception("no TTM"))
        with patch("yahoo_finance_mcp.server.yf.Ticker", return_value=mock_ticker):
            from yahoo_finance_mcp.server import get_ttm_income_statement
            result = json.loads(get_ttm_income_statement("FAKE"))
        assert "message" in result

    def test_ttm_cash_flow_returns_message_on_exception(self):
        mock_ticker = MagicMock()
        type(mock_ticker).ttm_cashflow = PropertyMock(side_effect=Exception("no TTM"))
        with patch("yahoo_finance_mcp.server.yf.Ticker", return_value=mock_ticker):
            from yahoo_finance_mcp.server import get_ttm_cash_flow
            result = json.loads(get_ttm_cash_flow("FAKE"))
        assert "message" in result
