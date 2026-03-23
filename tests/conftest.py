"""Shared fixtures for Yahoo Finance MCP server tests."""
import json
from unittest.mock import MagicMock

import pandas as pd
import pytest


def make_ticker_mock(**kwargs) -> MagicMock:
    """Build a MagicMock mimicking yf.Ticker with the given attribute overrides."""
    mock = MagicMock()
    for key, value in kwargs.items():
        setattr(mock, key, value)
    return mock


def sample_ohlcv_df(rows: int = 5) -> pd.DataFrame:
    dates = pd.date_range("2024-01-01", periods=rows, freq="B")
    return pd.DataFrame(
        {
            "Open": [100.0] * rows,
            "High": [105.0] * rows,
            "Low": [99.0] * rows,
            "Close": [103.0] * rows,
            "Volume": [1_000_000] * rows,
        },
        index=dates,
    )


def parse(result: str) -> dict | list:
    return json.loads(result)
