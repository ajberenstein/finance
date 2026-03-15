"""Yahoo Finance MCP Server - Comprehensive access to Yahoo Finance data via yfinance."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any

import pandas as pd
import yfinance as yf
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Yahoo Finance")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _df_to_json(df: pd.DataFrame | pd.Series | None, limit: int = 100) -> str:
    """Convert a pandas DataFrame/Series to a JSON string safe for MCP responses."""
    if df is None or (isinstance(df, (pd.DataFrame, pd.Series)) and df.empty):
        return json.dumps({"message": "No data available"})
    if isinstance(df, pd.Series):
        df = df.to_frame()
    df = df.head(limit).copy()
    df.index = df.index.astype(str)
    df.columns = [str(c) for c in df.columns]
    return df.to_json(date_format="iso", default_handler=str)


def _safe_dict(data: dict | None) -> str:
    if not data:
        return json.dumps({"message": "No data available"})
    return json.dumps(data, default=str)


def _safe_list(data: list | None) -> str:
    if not data:
        return json.dumps({"message": "No data available"})
    return json.dumps(data, default=str)


# =====================================================================
# 1. STOCK / TICKER INFORMATION
# =====================================================================

@mcp.tool()
def get_stock_info(ticker: str) -> str:
    """Get comprehensive information about a stock/ETF/index.

    Returns company profile, market data, financial ratios, dividends info,
    and more for the given ticker symbol.
    """
    t = yf.Ticker(ticker)
    return _safe_dict(t.info)


@mcp.tool()
def get_fast_info(ticker: str) -> str:
    """Get a quick summary of key metrics for a ticker.

    Returns fast-access data: price, market cap, volume, 52-week range, etc.
    Much faster than get_stock_info for basic data.
    """
    t = yf.Ticker(ticker)
    fi = t.fast_info
    data = {
        "currency": fi.get("currency"),
        "market_cap": fi.get("market_cap") or fi.get("marketCap"),
        "last_price": fi.get("last_price") or fi.get("lastPrice"),
        "previous_close": fi.get("previous_close") or fi.get("previousClose"),
        "open": fi.get("open"),
        "day_low": fi.get("day_low") or fi.get("dayLow"),
        "day_high": fi.get("day_high") or fi.get("dayHigh"),
        "fifty_day_average": fi.get("fifty_day_average") or fi.get("fiftyDayAverage"),
        "two_hundred_day_average": fi.get("two_hundred_day_average") or fi.get("twoHundredDayAverage"),
        "year_low": fi.get("year_low") or fi.get("yearLow"),
        "year_high": fi.get("year_high") or fi.get("yearHigh"),
        "shares_outstanding": fi.get("shares"),
        "timezone": fi.get("timezone"),
    }
    return json.dumps({k: v for k, v in data.items() if v is not None}, default=str)


@mcp.tool()
def get_history_metadata(ticker: str) -> str:
    """Get metadata about a ticker's price history.

    Returns exchange info, instrument type, trading period details,
    valid ranges and intervals, etc.
    """
    t = yf.Ticker(ticker)
    return _safe_dict(t.history_metadata)


# =====================================================================
# 2. HISTORICAL PRICE DATA
# =====================================================================

@mcp.tool()
def get_historical_data(
    ticker: str,
    period: str = "1mo",
    interval: str = "1d",
    start: str | None = None,
    end: str | None = None,
    prepost: bool = False,
    actions: bool = True,
    limit: int = 100,
) -> str:
    """Get historical OHLCV price data for a ticker.

    Args:
        ticker: Stock symbol (e.g. "AAPL", "MSFT")
        period: Data period - 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
        interval: Data interval - 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
        start: Start date string (YYYY-MM-DD). Overrides period if set.
        end: End date string (YYYY-MM-DD). Defaults to today.
        prepost: Include pre/post market data
        actions: Include dividends and stock splits
        limit: Max number of rows to return (default 100)
    """
    t = yf.Ticker(ticker)
    kwargs: dict[str, Any] = {
        "interval": interval,
        "prepost": prepost,
        "actions": actions,
    }
    if start:
        kwargs["start"] = start
        if end:
            kwargs["end"] = end
    else:
        kwargs["period"] = period
    df = t.history(**kwargs)
    return _df_to_json(df, limit=limit)


@mcp.tool()
def download_multiple_tickers(
    tickers: str,
    period: str = "1mo",
    interval: str = "1d",
    start: str | None = None,
    end: str | None = None,
    limit: int = 50,
) -> str:
    """Download historical data for multiple tickers at once.

    Args:
        tickers: Space-separated ticker symbols (e.g. "AAPL MSFT GOOG")
        period: Data period - 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
        interval: Data interval - 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
        start: Start date (YYYY-MM-DD). Overrides period if set.
        end: End date (YYYY-MM-DD).
        limit: Max rows per ticker (default 50)
    """
    kwargs: dict[str, Any] = {"interval": interval}
    if start:
        kwargs["start"] = start
        if end:
            kwargs["end"] = end
    else:
        kwargs["period"] = period
    df = yf.download(tickers, **kwargs)
    return _df_to_json(df, limit=limit)


# =====================================================================
# 3. FINANCIAL STATEMENTS
# =====================================================================

@mcp.tool()
def get_income_statement(ticker: str, quarterly: bool = False) -> str:
    """Get income statement (profit & loss) for a ticker.

    Args:
        ticker: Stock symbol
        quarterly: If True, return quarterly data; otherwise annual
    """
    t = yf.Ticker(ticker)
    df = t.quarterly_income_stmt if quarterly else t.income_stmt
    return _df_to_json(df)


@mcp.tool()
def get_balance_sheet(ticker: str, quarterly: bool = False) -> str:
    """Get balance sheet for a ticker.

    Args:
        ticker: Stock symbol
        quarterly: If True, return quarterly data; otherwise annual
    """
    t = yf.Ticker(ticker)
    df = t.quarterly_balance_sheet if quarterly else t.balance_sheet
    return _df_to_json(df)


@mcp.tool()
def get_cash_flow(ticker: str, quarterly: bool = False) -> str:
    """Get cash flow statement for a ticker.

    Args:
        ticker: Stock symbol
        quarterly: If True, return quarterly data; otherwise annual
    """
    t = yf.Ticker(ticker)
    df = t.quarterly_cashflow if quarterly else t.cashflow
    return _df_to_json(df)


@mcp.tool()
def get_financials(ticker: str, quarterly: bool = False) -> str:
    """Get combined financials (income statement) for a ticker.

    Args:
        ticker: Stock symbol
        quarterly: If True, return quarterly data; otherwise annual
    """
    t = yf.Ticker(ticker)
    df = t.quarterly_financials if quarterly else t.financials
    return _df_to_json(df)


# =====================================================================
# 4. DIVIDENDS, SPLITS & CORPORATE ACTIONS
# =====================================================================

@mcp.tool()
def get_dividends(ticker: str) -> str:
    """Get full dividend history for a ticker."""
    t = yf.Ticker(ticker)
    return _df_to_json(t.dividends)


@mcp.tool()
def get_splits(ticker: str) -> str:
    """Get full stock split history for a ticker."""
    t = yf.Ticker(ticker)
    return _df_to_json(t.splits)


@mcp.tool()
def get_actions(ticker: str) -> str:
    """Get all corporate actions (dividends + splits + capital gains) for a ticker."""
    t = yf.Ticker(ticker)
    return _df_to_json(t.actions)


@mcp.tool()
def get_capital_gains(ticker: str) -> str:
    """Get capital gains distributions (mainly for ETFs/Mutual Funds)."""
    t = yf.Ticker(ticker)
    try:
        data = t.get_capital_gains()
        return _df_to_json(data)
    except Exception:
        return json.dumps({"message": "No capital gains data available for this ticker"})


# =====================================================================
# 5. HOLDERS
# =====================================================================

@mcp.tool()
def get_major_holders(ticker: str) -> str:
    """Get major holders breakdown for a ticker (insider %, institutional %, etc.)."""
    t = yf.Ticker(ticker)
    return _df_to_json(t.major_holders)


@mcp.tool()
def get_institutional_holders(ticker: str) -> str:
    """Get top institutional holders for a ticker."""
    t = yf.Ticker(ticker)
    return _df_to_json(t.institutional_holders)


@mcp.tool()
def get_mutualfund_holders(ticker: str) -> str:
    """Get top mutual fund holders for a ticker."""
    t = yf.Ticker(ticker)
    return _df_to_json(t.mutualfund_holders)


@mcp.tool()
def get_insider_transactions(ticker: str) -> str:
    """Get recent insider transactions for a ticker."""
    t = yf.Ticker(ticker)
    return _df_to_json(t.insider_transactions)


@mcp.tool()
def get_insider_purchases(ticker: str) -> str:
    """Get aggregated insider purchase data for a ticker."""
    t = yf.Ticker(ticker)
    return _df_to_json(t.insider_purchases)


@mcp.tool()
def get_insider_roster_holders(ticker: str) -> str:
    """Get insider roster (list of insiders with positions) for a ticker."""
    t = yf.Ticker(ticker)
    return _df_to_json(t.insider_roster_holders)


# =====================================================================
# 6. ANALYST & RECOMMENDATIONS
# =====================================================================

@mcp.tool()
def get_recommendations(ticker: str) -> str:
    """Get analyst recommendations (buy/hold/sell ratings) for a ticker."""
    t = yf.Ticker(ticker)
    return _df_to_json(t.recommendations)


@mcp.tool()
def get_recommendations_summary(ticker: str) -> str:
    """Get summary of analyst recommendations for a ticker."""
    t = yf.Ticker(ticker)
    return _df_to_json(t.recommendations_summary)


@mcp.tool()
def get_upgrades_downgrades(ticker: str) -> str:
    """Get history of analyst upgrades and downgrades for a ticker."""
    t = yf.Ticker(ticker)
    return _df_to_json(t.upgrades_downgrades)


@mcp.tool()
def get_analyst_price_targets(ticker: str) -> str:
    """Get analyst price target estimates (low, mean, median, high, current)."""
    t = yf.Ticker(ticker)
    try:
        data = t.analyst_price_targets
        if isinstance(data, dict):
            return _safe_dict(data)
        return _df_to_json(data)
    except Exception:
        return json.dumps({"message": "No analyst price target data available"})


# =====================================================================
# 7. EARNINGS & ESTIMATES
# =====================================================================

@mcp.tool()
def get_earnings(ticker: str, quarterly: bool = False) -> str:
    """Get earnings data for a ticker.

    Args:
        ticker: Stock symbol
        quarterly: If True, return quarterly earnings; otherwise annual
    """
    t = yf.Ticker(ticker)
    df = t.quarterly_earnings if quarterly else t.earnings
    return _df_to_json(df)


@mcp.tool()
def get_earnings_dates(ticker: str, limit: int = 12) -> str:
    """Get upcoming and past earnings dates with EPS estimates and actuals.

    Args:
        ticker: Stock symbol
        limit: Maximum number of earnings dates to return
    """
    t = yf.Ticker(ticker)
    df = t.get_earnings_dates(limit=limit)
    return _df_to_json(df, limit=limit)


@mcp.tool()
def get_earnings_estimate(ticker: str) -> str:
    """Get current earnings estimates from analysts for a ticker."""
    t = yf.Ticker(ticker)
    return _df_to_json(t.earnings_estimate)


@mcp.tool()
def get_revenue_estimate(ticker: str) -> str:
    """Get current revenue estimates from analysts for a ticker."""
    t = yf.Ticker(ticker)
    return _df_to_json(t.revenue_estimate)


@mcp.tool()
def get_earnings_history(ticker: str) -> str:
    """Get historical earnings with EPS estimates vs actuals (surprises)."""
    t = yf.Ticker(ticker)
    return _df_to_json(t.earnings_history)


@mcp.tool()
def get_eps_trend(ticker: str) -> str:
    """Get EPS trend data showing how estimates have changed over time."""
    t = yf.Ticker(ticker)
    return _df_to_json(t.eps_trend)


@mcp.tool()
def get_eps_revisions(ticker: str) -> str:
    """Get EPS revision data (upgrades/downgrades in estimates)."""
    t = yf.Ticker(ticker)
    return _df_to_json(t.eps_revisions)


@mcp.tool()
def get_growth_estimates(ticker: str) -> str:
    """Get growth estimates for a ticker vs sector and industry."""
    t = yf.Ticker(ticker)
    return _df_to_json(t.growth_estimates)


# =====================================================================
# 8. OPTIONS
# =====================================================================

@mcp.tool()
def get_options_expirations(ticker: str) -> str:
    """Get available option expiration dates for a ticker."""
    t = yf.Ticker(ticker)
    return json.dumps(list(t.options))


@mcp.tool()
def get_options_chain(ticker: str, expiration: str | None = None) -> str:
    """Get the full options chain (calls and puts) for a given expiration date.

    Args:
        ticker: Stock symbol
        expiration: Expiration date (YYYY-MM-DD). If not provided, uses the nearest expiration.
    """
    t = yf.Ticker(ticker)
    expirations = t.options
    if not expirations:
        return json.dumps({"message": "No options data available for this ticker"})
    exp = expiration if expiration and expiration in expirations else expirations[0]
    chain = t.option_chain(exp)
    calls = chain.calls.head(50)
    puts = chain.puts.head(50)
    return json.dumps({
        "expiration": exp,
        "calls": json.loads(calls.to_json(date_format="iso", default_handler=str)),
        "puts": json.loads(puts.to_json(date_format="iso", default_handler=str)),
    }, default=str)


# =====================================================================
# 9. SUSTAINABILITY / ESG
# =====================================================================

@mcp.tool()
def get_sustainability(ticker: str) -> str:
    """Get ESG (Environmental, Social, Governance) sustainability scores for a ticker."""
    t = yf.Ticker(ticker)
    return _df_to_json(t.sustainability)


# =====================================================================
# 10. NEWS & CALENDAR
# =====================================================================

@mcp.tool()
def get_news(ticker: str) -> str:
    """Get recent news articles related to a ticker."""
    t = yf.Ticker(ticker)
    return _safe_list(t.news)


@mcp.tool()
def get_calendar(ticker: str) -> str:
    """Get upcoming events calendar for a ticker (earnings dates, ex-dividend, etc.)."""
    t = yf.Ticker(ticker)
    cal = t.calendar
    if isinstance(cal, pd.DataFrame):
        return _df_to_json(cal)
    return _safe_dict(cal)


# =====================================================================
# 11. SHARES & SEC FILINGS
# =====================================================================

@mcp.tool()
def get_shares_count(ticker: str) -> str:
    """Get historical share count over time for a ticker."""
    t = yf.Ticker(ticker)
    return _df_to_json(t.shares)


@mcp.tool()
def get_shares_full(ticker: str, start: str | None = None, end: str | None = None) -> str:
    """Get full granularity share count history.

    Args:
        ticker: Stock symbol
        start: Start date (YYYY-MM-DD)
        end: End date (YYYY-MM-DD)
    """
    t = yf.Ticker(ticker)
    kwargs: dict[str, Any] = {}
    if start:
        kwargs["start"] = start
    if end:
        kwargs["end"] = end
    data = t.get_shares_full(**kwargs)
    return _df_to_json(data)


@mcp.tool()
def get_sec_filings(ticker: str) -> str:
    """Get recent SEC filings for a ticker."""
    t = yf.Ticker(ticker)
    filings = t.sec_filings
    if isinstance(filings, pd.DataFrame):
        return _df_to_json(filings)
    return _safe_list(filings)


@mcp.tool()
def get_isin(ticker: str) -> str:
    """Get the ISIN (International Securities Identification Number) for a ticker."""
    t = yf.Ticker(ticker)
    try:
        return json.dumps({"isin": t.isin})
    except Exception:
        return json.dumps({"message": "ISIN not available for this ticker"})


# =====================================================================
# 12. FUNDS DATA (ETFs / Mutual Funds)
# =====================================================================

@mcp.tool()
def get_funds_data(ticker: str) -> str:
    """Get fund-specific data for an ETF or Mutual Fund.

    Returns fund description, overview, operations, asset classes,
    top holdings, equity holdings, bond holdings, etc.
    """
    t = yf.Ticker(ticker)
    try:
        fd = t.funds_data
        result: dict[str, Any] = {}
        for attr in [
            "description", "fund_overview", "fund_operations",
            "asset_classes", "top_holdings", "equity_holdings",
            "bond_holdings", "bond_ratings", "sector_weightings",
        ]:
            try:
                val = getattr(fd, attr, None)
                if val is not None:
                    if isinstance(val, pd.DataFrame):
                        result[attr] = json.loads(val.to_json(default_handler=str))
                    elif isinstance(val, dict):
                        result[attr] = val
                    else:
                        result[attr] = str(val)
            except Exception:
                continue
        return json.dumps(result, default=str) if result else json.dumps({"message": "No fund data available"})
    except Exception:
        return json.dumps({"message": "No fund data available for this ticker"})


# =====================================================================
# 13. SEARCH
# =====================================================================

@mcp.tool()
def search_tickers(query: str, max_results: int = 10) -> str:
    """Search for tickers by company name or symbol.

    Args:
        query: Search term (e.g. "Apple", "tech", "AAPL")
        max_results: Maximum number of results to return (default 10)
    """
    search = yf.Search(query)
    results: dict[str, Any] = {}
    try:
        results["quotes"] = search.quotes[:max_results] if search.quotes else []
    except Exception:
        results["quotes"] = []
    try:
        results["news"] = search.news[:max_results] if search.news else []
    except Exception:
        results["news"] = []
    return json.dumps(results, default=str)


# =====================================================================
# 14. SECTOR & INDUSTRY
# =====================================================================

@mcp.tool()
def get_sector_info(sector_key: str) -> str:
    """Get information about a market sector.

    Args:
        sector_key: Sector key (e.g. "technology", "healthcare", "financial-services",
                    "consumer-cyclical", "industrials", "energy", "utilities",
                    "real-estate", "communication-services", "consumer-defensive",
                    "basic-materials")
    """
    try:
        sector = yf.Sector(sector_key)
        result: dict[str, Any] = {}
        for attr in ["key", "name", "symbol", "overview", "top_companies", "research_reports"]:
            try:
                val = getattr(sector, attr, None)
                if val is not None:
                    if isinstance(val, pd.DataFrame):
                        result[attr] = json.loads(val.head(20).to_json(default_handler=str))
                    elif isinstance(val, dict):
                        result[attr] = val
                    else:
                        result[attr] = str(val)
            except Exception:
                continue
        return json.dumps(result, default=str)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
def get_industry_info(industry_key: str) -> str:
    """Get information about a specific industry.

    Args:
        industry_key: Industry key (e.g. "software-infrastructure", "semiconductors",
                      "biotechnology", "banks-diversified", "oil-gas-integrated")
    """
    try:
        industry = yf.Industry(industry_key)
        result: dict[str, Any] = {}
        for attr in ["key", "name", "symbol", "overview", "top_companies", "research_reports"]:
            try:
                val = getattr(industry, attr, None)
                if val is not None:
                    if isinstance(val, pd.DataFrame):
                        result[attr] = json.loads(val.head(20).to_json(default_handler=str))
                    elif isinstance(val, dict):
                        result[attr] = val
                    else:
                        result[attr] = str(val)
            except Exception:
                continue
        return json.dumps(result, default=str)
    except Exception as e:
        return json.dumps({"error": str(e)})


# =====================================================================
# 15. MARKET SCREENER
# =====================================================================

@mcp.tool()
def screen_market(
    query_type: str = "equity",
    exchange: str = "NMS",
    sector: str | None = None,
    industry: str | None = None,
    min_market_cap: float | None = None,
    max_market_cap: float | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    limit: int = 25,
) -> str:
    """Screen the market using various filters.

    Args:
        query_type: Asset type - "equity", "etf", "mutualfund", "index", "future", "currency"
        exchange: Exchange code (e.g. "NMS" for NASDAQ, "NYQ" for NYSE)
        sector: Filter by sector (e.g. "Technology")
        industry: Filter by industry
        min_market_cap: Minimum market cap filter
        max_market_cap: Maximum market cap filter
        min_price: Minimum price filter
        max_price: Maximum price filter
        limit: Maximum results to return (default 25)
    """
    try:
        from yfinance import EquityQuery, Screener

        conditions: list = []

        if sector:
            conditions.append(EquityQuery("eq", ["sector", sector]))
        if industry:
            conditions.append(EquityQuery("eq", ["industry", industry]))
        if min_market_cap is not None:
            conditions.append(EquityQuery("gt", ["intradaymarketcap", min_market_cap]))
        if max_market_cap is not None:
            conditions.append(EquityQuery("lt", ["intradaymarketcap", max_market_cap]))
        if min_price is not None:
            conditions.append(EquityQuery("gt", ["intradayprice", min_price]))
        if max_price is not None:
            conditions.append(EquityQuery("lt", ["intradayprice", max_price]))

        if not conditions:
            conditions.append(EquityQuery("gt", ["intradaymarketcap", 0]))

        if len(conditions) == 1:
            query = conditions[0]
        else:
            query = EquityQuery("and", conditions)

        sc = Screener()
        sc.set_default_body(query, size=limit)
        result = sc.response
        return json.dumps(result, default=str)
    except ImportError:
        return json.dumps({"error": "Market screener requires yfinance >= 0.2.37 with EquityQuery support"})
    except Exception as e:
        return json.dumps({"error": str(e)})


# =====================================================================
# 16. MARKET INFO
# =====================================================================

@mcp.tool()
def get_market_summary(market: str = "us_market") -> str:
    """Get summary information about a financial market.

    Args:
        market: Market identifier (e.g. "us_market", "uk_market", "de_market",
                "fr_market", "es_market", "it_market", "ca_market", "in_market",
                "hk_market", "au_market", "br_market")
    """
    try:
        m = yf.Market(market)
        result: dict[str, Any] = {}
        for attr in ["status", "summary"]:
            try:
                val = getattr(m, attr, None)
                if val is not None:
                    if isinstance(val, pd.DataFrame):
                        result[attr] = json.loads(val.to_json(default_handler=str))
                    elif isinstance(val, dict):
                        result[attr] = val
                    else:
                        result[attr] = str(val)
            except Exception:
                continue
        return json.dumps(result, default=str)
    except Exception as e:
        return json.dumps({"error": str(e)})


# =====================================================================
# 17. TTM (Trailing Twelve Months) DATA
# =====================================================================

@mcp.tool()
def get_ttm_income_statement(ticker: str) -> str:
    """Get trailing twelve months (TTM) income statement for a ticker."""
    t = yf.Ticker(ticker)
    try:
        return _df_to_json(t.ttm_income_stmt)
    except Exception:
        return json.dumps({"message": "TTM income statement not available"})


@mcp.tool()
def get_ttm_cash_flow(ticker: str) -> str:
    """Get trailing twelve months (TTM) cash flow statement for a ticker."""
    t = yf.Ticker(ticker)
    try:
        return _df_to_json(t.ttm_cashflow)
    except Exception:
        return json.dumps({"message": "TTM cash flow not available"})


@mcp.tool()
def get_ttm_financials(ticker: str) -> str:
    """Get trailing twelve months (TTM) financials for a ticker."""
    t = yf.Ticker(ticker)
    try:
        return _df_to_json(t.ttm_financials)
    except Exception:
        return json.dumps({"message": "TTM financials not available"})


# =====================================================================
# ENTRY POINT
# =====================================================================

def main():
    """Run the Yahoo Finance MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
