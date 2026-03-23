# Yahoo Finance MCP Server

MCP (Model Context Protocol) server that provides comprehensive access to Yahoo Finance market data via the `yfinance` library.

## Features

**49 tools** covering the full Yahoo Finance API:

| Category | Tools |
|---|---|
| **Stock Info** | `get_stock_info`, `get_fast_info`, `get_history_metadata` |
| **Price History** | `get_historical_data`, `download_multiple_tickers` |
| **Financial Statements** | `get_income_statement`, `get_balance_sheet`, `get_cash_flow`, `get_financials` |
| **TTM Data** | `get_ttm_income_statement`, `get_ttm_cash_flow`, `get_ttm_financials` |
| **Dividends & Splits** | `get_dividends`, `get_splits`, `get_actions`, `get_capital_gains` |
| **Holders** | `get_major_holders`, `get_institutional_holders`, `get_mutualfund_holders`, `get_insider_transactions`, `get_insider_purchases`, `get_insider_roster_holders` |
| **Analyst Data** | `get_recommendations`, `get_recommendations_summary`, `get_upgrades_downgrades`, `get_analyst_price_targets` |
| **Earnings & Estimates** | `get_earnings`, `get_earnings_dates`, `get_earnings_estimate`, `get_revenue_estimate`, `get_earnings_history`, `get_eps_trend`, `get_eps_revisions`, `get_growth_estimates` |
| **Options** | `get_options_expirations`, `get_options_chain` |
| **ESG** | `get_sustainability` |
| **News & Calendar** | `get_news`, `get_calendar` |
| **Shares & Filings** | `get_shares_count`, `get_shares_full`, `get_sec_filings`, `get_isin` |
| **Funds (ETF/MF)** | `get_funds_data` |
| **Search** | `search_tickers` |
| **Sector & Industry** | `get_sector_info`, `get_industry_info` |
| **Market Screener** | `screen_market` |
| **Market Info** | `get_market_summary` |

## Installation

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install
pip install -e .
```

## Usage

### Run as stdio server (for Claude Desktop, etc.)

```bash
yahoo-finance-mcp
```

### Claude Desktop configuration

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "yahoo-finance": {
      "command": "/path/to/.venv/bin/yahoo-finance-mcp"
    }
  }
}
```

### Run with MCP CLI

```bash
mcp dev src/yahoo_finance_mcp/server.py
```

## Examples

Once connected, you can ask your LLM things like:

- "Get me Apple's stock info"
- "Show me MSFT's quarterly income statement"
- "What are the analyst recommendations for TSLA?"
- "Download historical data for AAPL, GOOG, and AMZN for the last year"
- "Show me the options chain for SPY"
- "Screen the market for tech stocks with market cap over 10 billion"
- "What are the top institutional holders of NVDA?"

## Remote deployment (DigitalOcean / Hetzner VPS)

The server can run remotely and be consumed by Claude Desktop or Claude.ai web via HTTPS.
It uses [Caddy](https://caddyserver.com/) as a reverse proxy with automatic TLS via Let's Encrypt,
and [sslip.io](https://sslip.io) for a free HTTPS domain derived from the server IP.

### First-time setup on a fresh Ubuntu VPS

```bash
# 1. Install Docker
curl -fsSL https://get.docker.com | sh

# 2. Clone the repo
git clone https://github.com/ajberenstein/finance.git /opt/yahoo-finance-mcp
cd /opt/yahoo-finance-mcp

# 3. Set your domain (replace dots with dashes in the server IP)
#    Example: IP 1.2.3.4 → DOMAIN=1-2-3-4.sslip.io
echo "DOMAIN=YOUR-IP-WITH-DASHES.sslip.io" > .env

# 4. Build and start
docker compose up -d --build
```

The server will be available at `https://YOUR-IP-WITH-DASHES.sslip.io/sse`.

### Updating after a code change

```bash
cd /opt/yahoo-finance-mcp && git pull && docker compose up -d --build
```

### Useful ops commands

```bash
# Check running containers
docker compose ps

# Follow live logs
docker compose logs -f

# Restart without rebuilding
docker compose restart

# Stop everything
docker compose down
```

### Connect Claude Desktop to the remote server

Add to `claude_desktop_config.json`:

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "yahoo-finance": {
      "url": "https://YOUR-IP-WITH-DASHES.sslip.io/sse"
    }
  }
}
```

### Connect Claude.ai web

Settings → Integrations → Add MCP Server → enter your `https://…sslip.io/sse` URL.

## Running tests

```bash
pip install -e ".[dev]"
python -m pytest tests/
```

## Requirements

- Python >= 3.10
- `yfinance >= 0.2.30`
- `mcp[cli] >= 1.0.0`
- `pandas >= 2.0.0`
