# Tushare MCP Server

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![MCP](https://img.shields.io/badge/MCP-1.0+-green.svg)](https://modelcontextprotocol.io/)

A [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server that provides AI assistants with access to [Tushare](https://tushare.pro/) financial data API. This enables AI models to query Chinese stock market data, financial statements, macroeconomic indicators, and more.

## Features

This MCP server exposes 18 financial data tools across multiple categories:

### Stock Data
- **stock_basic** - Stock list with basic information (code, name, industry, listing date)
- **stock_company** - Company profile and basic information
- **daily_quote** - Daily price data (OHLCV)
- **daily_basic** - Daily valuation metrics (PE, PB, PS, market cap)
- **trade_cal** - Trading calendar

### Financial Statements
- **income** - Income statement data
- **balance_sheet** - Balance sheet data
- **cashflow** - Cash flow statement data
- **fina_indicator** - Financial indicators (ROE, gross margin, net margin)

### Market Data
- **daily_limit** - Daily limit-up/limit-down statistics
- **moneyflow_hsgt** - Stock Connect (Northbound) capital flow
- **top10_holders** - Top 10 shareholders

### Concept & Index
- **concept** - Concept stock categories
- **concept_detail** - Concept stock constituents
- **index_basic** - Index basic information
- **index_daily** - Index daily quotes

### Futures
- **future_basic** - Futures contract basic info
- **future_daily** - Futures daily market data

## Installation

### From Source

```bash
git clone https://github.com/lijinly/tushare-mcp-server.git
cd tushare-mcp-server
pip install -e .
```

### Requirements

- Python >= 3.10
- Tushare API Token ([Get one free](https://tushare.pro/register))

## Configuration

### 1. Get Tushare API Token

Register at [Tushare Pro](https://tushare.pro/register) and get your API token from your profile page.

### 2. Configure Environment Variable

```bash
# Linux/macOS
export TUSHARE_TOKEN="your_token_here"

# Windows PowerShell
$env:TUSHARE_TOKEN="your_token_here"

# Windows CMD
set TUSHARE_TOKEN=your_token_here
```

### 3. Configure MCP Client

Add to your MCP client configuration (e.g., Claude Desktop, Cline):

```json
{
  "mcpServers": {
    "tushare": {
      "command": "python",
      "args": ["-m", "tushare_mcp_server"],
      "env": {
        "TUSHARE_TOKEN": "your_token_here"
      }
    }
  }
}
```

**Claude Desktop Config Location:**
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`

## Usage

### Manual Start

```bash
python -m tushare_mcp_server
```

### With MCP Client

Once configured, the AI assistant can directly call Tushare data tools:

**Example queries:**
- "Get the daily quote for 000001.SZ"
- "Show me the PE ratio of Kweichow Moutai"
- "What's the stock connect capital flow today?"
- "List all concept stocks for artificial intelligence"

## Data Format

All tools return JSON formatted data:

```json
{
  "data": [...],
  "count": 100,
  "columns": ["ts_code", "trade_date", "close", "pe", "pb"]
}
```

## Project Structure

```
tushare-mcp-server/
├── src/tushare_mcp_server/
│   ├── __init__.py
│   ├── __main__.py
│   └── server.py          # Main MCP server implementation
├── pyproject.toml         # Project configuration
├── README.md
└── .gitignore
```

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| mcp | >=1.0.0 | MCP protocol implementation |
| tushare | >=1.4.0 | Tushare API client |
| pandas | >=2.0.0 | Data manipulation |

## Development

### Setup Development Environment

```bash
# Create virtual environment
conda create -n tushare-mcp python=3.10 -y
conda activate tushare-mcp

# Install in editable mode
pip install -e .
```

### Testing

```bash
python -m tushare_mcp_server
```

## Troubleshooting

### "TUSHARE_TOKEN environment variable is not set"
Make sure you've set the `TUSHARE_TOKEN` environment variable before starting the server.

### "Error connecting to Tushare API"
- Check your internet connection
- Verify your Tushare token is valid
- Ensure your Tushare account has sufficient API points

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Tushare](https://tushare.pro/) - Chinese financial data platform
- [Model Context Protocol](https://modelcontextprotocol.io/) - Open protocol for AI tool integration

## Related Links

- [Tushare API Documentation](https://tushare.pro/document/2)
- [MCP Specification](https://spec.modelcontextprotocol.io/)
