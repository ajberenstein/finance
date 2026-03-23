"""Tests for historical price data tools."""
import json
from unittest.mock import MagicMock, call, patch

import pandas as pd
import pytest

from tests.conftest import make_ticker_mock, sample_ohlcv_df


class TestGetHistoricalData:
    def test_returns_ohlcv_json(self):
        mock_ticker = make_ticker_mock()
        mock_ticker.history.return_value = sample_ohlcv_df(5)
        with patch("yahoo_finance_mcp.server.yf.Ticker", return_value=mock_ticker):
            from yahoo_finance_mcp.server import get_historical_data
            result = json.loads(get_historical_data("AAPL"))
        assert "Close" in result

    def test_uses_period_when_no_start(self):
        mock_ticker = make_ticker_mock()
        mock_ticker.history.return_value = sample_ohlcv_df(3)
        with patch("yahoo_finance_mcp.server.yf.Ticker", return_value=mock_ticker):
            from yahoo_finance_mcp.server import get_historical_data
            get_historical_data("AAPL", period="3mo", interval="1d")
        _, kwargs = mock_ticker.history.call_args
        assert kwargs["period"] == "3mo"
        assert "start" not in kwargs

    def test_uses_start_end_when_provided(self):
        mock_ticker = make_ticker_mock()
        mock_ticker.history.return_value = sample_ohlcv_df(3)
        with patch("yahoo_finance_mcp.server.yf.Ticker", return_value=mock_ticker):
            from yahoo_finance_mcp.server import get_historical_data
            get_historical_data("AAPL", start="2024-01-01", end="2024-03-01")
        _, kwargs = mock_ticker.history.call_args
        assert kwargs["start"] == "2024-01-01"
        assert kwargs["end"] == "2024-03-01"
        assert "period" not in kwargs

    def test_start_without_end_omits_end(self):
        mock_ticker = make_ticker_mock()
        mock_ticker.history.return_value = sample_ohlcv_df(3)
        with patch("yahoo_finance_mcp.server.yf.Ticker", return_value=mock_ticker):
            from yahoo_finance_mcp.server import get_historical_data
            get_historical_data("AAPL", start="2024-01-01")
        _, kwargs = mock_ticker.history.call_args
        assert "start" in kwargs
        assert "end" not in kwargs

    def test_limit_is_respected(self):
        mock_ticker = make_ticker_mock()
        mock_ticker.history.return_value = sample_ohlcv_df(80)
        with patch("yahoo_finance_mcp.server.yf.Ticker", return_value=mock_ticker):
            from yahoo_finance_mcp.server import get_historical_data
            result = json.loads(get_historical_data("AAPL", limit=10))
        assert len(list(result["Close"].values())) == 10

    def test_empty_history_returns_no_data(self):
        mock_ticker = make_ticker_mock()
        mock_ticker.history.return_value = pd.DataFrame()
        with patch("yahoo_finance_mcp.server.yf.Ticker", return_value=mock_ticker):
            from yahoo_finance_mcp.server import get_historical_data
            result = json.loads(get_historical_data("FAKE"))
        assert result == {"message": "No data available"}


class TestDownloadMultipleTickers:
    def test_returns_json_for_multiple_tickers(self):
        df = sample_ohlcv_df(5)
        with patch("yahoo_finance_mcp.server.yf.download", return_value=df):
            from yahoo_finance_mcp.server import download_multiple_tickers
            result = json.loads(download_multiple_tickers("AAPL MSFT"))
        assert "Close" in result

    def test_passes_period_when_no_start(self):
        df = sample_ohlcv_df(3)
        with patch("yahoo_finance_mcp.server.yf.download", return_value=df) as mock_dl:
            from yahoo_finance_mcp.server import download_multiple_tickers
            download_multiple_tickers("AAPL MSFT", period="1mo")
        _, kwargs = mock_dl.call_args
        assert kwargs["period"] == "1mo"

    def test_passes_start_end_when_provided(self):
        df = sample_ohlcv_df(3)
        with patch("yahoo_finance_mcp.server.yf.download", return_value=df) as mock_dl:
            from yahoo_finance_mcp.server import download_multiple_tickers
            download_multiple_tickers("AAPL MSFT", start="2024-01-01", end="2024-06-01")
        _, kwargs = mock_dl.call_args
        assert kwargs["start"] == "2024-01-01"
        assert kwargs["end"] == "2024-06-01"
