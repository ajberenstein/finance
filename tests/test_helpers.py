"""Tests for helper utilities: _df_to_json, _safe_dict, _safe_list."""
import json

import pandas as pd
import pytest

from yahoo_finance_mcp.server import _df_to_json, _safe_dict, _safe_list


# ---------------------------------------------------------------------------
# _df_to_json
# ---------------------------------------------------------------------------

class TestDfToJson:
    def test_none_returns_no_data(self):
        result = json.loads(_df_to_json(None))
        assert result == {"message": "No data available"}

    def test_empty_dataframe_returns_no_data(self):
        result = json.loads(_df_to_json(pd.DataFrame()))
        assert result == {"message": "No data available"}

    def test_empty_series_returns_no_data(self):
        result = json.loads(_df_to_json(pd.Series([], dtype=float)))
        assert result == {"message": "No data available"}

    def test_dataframe_returns_valid_json(self):
        df = pd.DataFrame({"price": [1.0, 2.0]}, index=["a", "b"])
        result = json.loads(_df_to_json(df))
        assert "price" in result

    def test_series_is_converted_to_frame(self):
        s = pd.Series({"revenue": 1000, "expenses": 800}, name="2023")
        result = json.loads(_df_to_json(s))
        assert isinstance(result, dict)

    def test_limit_is_applied(self):
        df = pd.DataFrame({"v": range(200)})
        result = json.loads(_df_to_json(df, limit=10))
        # JSON object: keys are column names; each column has 'limit' entries
        values = list(result["v"].values())
        assert len(values) == 10

    def test_default_limit_is_100(self):
        df = pd.DataFrame({"v": range(150)})
        result = json.loads(_df_to_json(df))
        assert len(list(result["v"].values())) == 100

    def test_index_is_stringified(self):
        dates = pd.date_range("2024-01-01", periods=3, freq="D")
        df = pd.DataFrame({"price": [1, 2, 3]}, index=dates)
        result = json.loads(_df_to_json(df))
        for key in result["price"]:
            assert isinstance(key, str)

    def test_columns_are_stringified(self):
        df = pd.DataFrame({1: [10], 2: [20]})
        result = json.loads(_df_to_json(df))
        for col in result:
            assert isinstance(col, str)


# ---------------------------------------------------------------------------
# _safe_dict
# ---------------------------------------------------------------------------

class TestSafeDict:
    def test_none_returns_no_data(self):
        assert json.loads(_safe_dict(None)) == {"message": "No data available"}

    def test_empty_dict_returns_no_data(self):
        assert json.loads(_safe_dict({})) == {"message": "No data available"}

    def test_populated_dict_is_serialized(self):
        result = json.loads(_safe_dict({"symbol": "AAPL", "price": 150.0}))
        assert result["symbol"] == "AAPL"
        assert result["price"] == 150.0

    def test_non_serializable_values_use_str_fallback(self):
        from datetime import date
        data = {"date": date(2024, 1, 1)}
        result = json.loads(_safe_dict(data))
        assert isinstance(result["date"], str)


# ---------------------------------------------------------------------------
# _safe_list
# ---------------------------------------------------------------------------

class TestSafeList:
    def test_none_returns_no_data(self):
        assert json.loads(_safe_list(None)) == {"message": "No data available"}

    def test_empty_list_returns_no_data(self):
        assert json.loads(_safe_list([])) == {"message": "No data available"}

    def test_populated_list_is_serialized(self):
        result = json.loads(_safe_list([{"title": "news1"}, {"title": "news2"}]))
        assert len(result) == 2
        assert result[0]["title"] == "news1"

    def test_non_serializable_items_use_str_fallback(self):
        from datetime import date
        result = json.loads(_safe_list([date(2024, 1, 1)]))
        assert isinstance(result[0], str)
