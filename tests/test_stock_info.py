"""Tests for stock / ticker information tools."""
import json
from unittest.mock import MagicMock, patch

import pytest

from tests.conftest import make_ticker_mock


class TestGetStockInfo:
    def test_returns_info_as_json(self):
        mock_ticker = make_ticker_mock(info={"symbol": "AAPL", "longName": "Apple Inc."})
        with patch("yahoo_finance_mcp.server.yf.Ticker", return_value=mock_ticker):
            from yahoo_finance_mcp.server import get_stock_info
            result = json.loads(get_stock_info("AAPL"))
        assert result["symbol"] == "AAPL"

    def test_empty_info_returns_no_data(self):
        mock_ticker = make_ticker_mock(info={})
        with patch("yahoo_finance_mcp.server.yf.Ticker", return_value=mock_ticker):
            from yahoo_finance_mcp.server import get_stock_info
            result = json.loads(get_stock_info("FAKE"))
        assert result == {"message": "No data available"}

    def test_ticker_symbol_is_forwarded(self):
        mock_ticker = make_ticker_mock(info={"symbol": "MSFT"})
        with patch("yahoo_finance_mcp.server.yf.Ticker", return_value=mock_ticker) as mock_cls:
            from yahoo_finance_mcp.server import get_stock_info
            get_stock_info("MSFT")
        mock_cls.assert_called_once_with("MSFT")


class TestGetFastInfo:
    def _make_fast_info(self, **kwargs):
        fi = MagicMock()
        fi.get = lambda key, default=None: kwargs.get(key, default)
        return fi

    def test_returns_known_fields(self):
        fi = self._make_fast_info(
            currency="USD",
            market_cap=3_000_000_000_000,
            last_price=195.0,
        )
        mock_ticker = make_ticker_mock(fast_info=fi)
        with patch("yahoo_finance_mcp.server.yf.Ticker", return_value=mock_ticker):
            from yahoo_finance_mcp.server import get_fast_info
            result = json.loads(get_fast_info("AAPL"))
        assert result["currency"] == "USD"
        assert result["market_cap"] == 3_000_000_000_000

    def test_none_values_are_excluded(self):
        fi = self._make_fast_info(currency="USD")
        mock_ticker = make_ticker_mock(fast_info=fi)
        with patch("yahoo_finance_mcp.server.yf.Ticker", return_value=mock_ticker):
            from yahoo_finance_mcp.server import get_fast_info
            result = json.loads(get_fast_info("AAPL"))
        # Fields not present in fast_info should not appear
        assert "market_cap" not in result


class TestGetHistoryMetadata:
    def test_returns_metadata_as_json(self):
        metadata = {"symbol": "AAPL", "instrumentType": "EQUITY", "exchangeName": "NMS"}
        mock_ticker = make_ticker_mock(history_metadata=metadata)
        with patch("yahoo_finance_mcp.server.yf.Ticker", return_value=mock_ticker):
            from yahoo_finance_mcp.server import get_history_metadata
            result = json.loads(get_history_metadata("AAPL"))
        assert result["instrumentType"] == "EQUITY"

    def test_empty_metadata_returns_no_data(self):
        mock_ticker = make_ticker_mock(history_metadata={})
        with patch("yahoo_finance_mcp.server.yf.Ticker", return_value=mock_ticker):
            from yahoo_finance_mcp.server import get_history_metadata
            result = json.loads(get_history_metadata("FAKE"))
        assert result == {"message": "No data available"}
