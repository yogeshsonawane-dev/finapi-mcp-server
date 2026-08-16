# FinAPI MCP Server

A Model Context Protocol (MCP) server that provides comprehensive access to mutual fund and IPO analytics data through AI assistants, enabling intelligent financial analysis and investment discovery.

## Overview

The FinAPI MCP Server is a powerful analytics platform that integrates mutual fund performance data and IPO market intelligence into the Model Context Protocol. It allows AI assistants to access real-time market data, fund analytics, and IPO information for informed investment decisions.

## Features

### Mutual Fund Analytics
- **Performance Analysis**: Top performers, worst performers, and consistent performers across multiple timeframes (1Y, 3Y, 5Y, 7Y, 10Y)
- **Fund Discovery by Holdings**: Find funds holding specific stocks with position weightage
- **Sector Exposure Analysis**: Identify funds with highest exposure to specific sectors
- **Risk & Rating Filters**: Filter funds by Morningstar ratings (1-5 stars) and risk levels
- **Fund Manager Search**: Discover funds managed by specific portfolio managers
- **Benchmark Tracking**: Find funds benchmarked against specific indices

### Portfolio Allocation Analysis
- **Cash Allocation**: Identify funds with highest cash positions
- **Equity Allocation**: Find equity-focused funds
- **Market Cap Distribution**: Analyze large-cap, mid-cap, and small-cap heavy funds
- **Cost Efficiency**: Identify lowest expense ratio and most cost-efficient funds
- **Volatility Analysis**: Find stable, low-volatility funds for risk-averse investors

### Fund Metadata & Classification
- **Category Analytics**: Browse fund categories and category leaders
- **Fund Houses**: Explore all AMCs (Asset Management Companies) and their offerings
- **Vintage Analysis**: Discover oldest and newest mutual funds
- **Direct Fund Lookup**: Access funds by scheme code, ISIN, or fund house
- **Fund Search**: Wildcard search by scheme name
- **NAV History**: Retrieve historical Net Asset Value data

### IPO Intelligence
- **Live IPOs**: Track currently open IPO subscriptions
- **Upcoming IPOs**: Monitor IPOs opening soon
- **IPO Analytics**: Identify most subscribed IPOs and highest Grey Market Premium (GMP)
- **IPO Search**: Look up historical and current IPO details
- **Market Overview**: Get comprehensive IPO market summary by status and type

### Market Information
- **Exchange Holidays**: Access stock market holiday calendars
- **Health Checks**: Monitor FinAPI API server availability

## Installation

### Prerequisites
- Python 3.8 or higher
- pip or uv package manager

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd finapi-mcp-server
```

2. Install dependencies:
```bash
# Using pip
pip install -r requirements.txt

# Or using uv
uv sync
```

3. Run the server:
```bash
python main.py
```

The server will start on `http://localhost:8004` with HTTP transport.

## Configuration

### Environment Variables
- `MCP_PORT`: Port for the MCP server (default: 8004)
- `FINAPI_API_KEY`: Optional FinAPI API key. When set, it is sent as the `X-API-Key` header on every FinAPI API call, which grants higher rate limits. Omit it to call the API without a key.

### Server Details
- **Name**: FinAPI MCP Server
- **Transport**: HTTP
- **Port**: 8004
- **API Base**: `https://api.finapi.upvaly.com`

## Usage

### Authentication
All tools are unauthenticated and directly access the FinAPI Analytics API. Optionally, you can configure a FinAPI API key to get higher rate limits — the server will send it as the `X-API-Key` header on every request. To enable it, set the `FINAPI_API_KEY` environment variable when starting the server, e.g. in your MCP client configuration:

```json
{
  "mcpServers": {
    "finapi": {
      "command": "python",
      "args": ["main.py"],
      "env": {
        "FINAPI_API_KEY": "your-finapi-api-key"
      }
    }
  }
}
```

Or when running directly:

```bash
FINAPI_API_KEY=your-finapi-api-key python main.py
```

The header is only sent when a key is configured; requests work without it.

### Tool Invocation

Example usage patterns:

```
# Get mutual fund analytics
get_mf_top_performers(period="3y", limit=10)
get_mf_consistent_performers()
get_mf_worst_performers(period="1y")

# Find funds by holdings, sector, or manager
get_mf_by_holding(stockName="HDFC Bank")
get_mf_by_sector_exposure(sector="Financial Services")
get_mf_by_fund_manager(managerName="Prashant Jain")

# Filter by ratings and risk
get_mf_by_rating(rating=5)
get_mf_by_risk_level(risk="Low")

# Portfolio allocation analysis
get_mf_highest_equity_allocation()
get_mf_large_cap_heavy()
get_mf_lowest_expense_ratio()
get_mf_lowest_volatility()

# Fund discovery
get_mf_categories()
get_mf_fund_houses()
get_mf_category_leaders()
get_mf_by_category(category="Large Cap")

# Direct fund lookup
get_mf_by_scheme_code(schemeCode="118989")
get_mf_by_isin(isin="INF209K01YH3")
search_mf(query="Axis Bluechip")
get_mf_nav_by_isin(isin="INF209K01YH3", startDate="2025-01-01")

# IPO analytics
get_ipo_live()
get_ipo_upcoming()
get_ipo_most_subscribed()
get_ipo_highest_gmp()
search_ipo(name="Zomato")
get_ipo_overview()

# Market information
check_health()
get_exchange_holidays()
```

## Architecture

### Core Components

- **main.py**: Server entry point and FastMCP initialization
- **tools/tools.py**: Tool definitions and implementation for mutual fund and IPO analytics

### API Integration

The server communicates with the FinAPI Analytics API at `https://api.finapi.upvaly.com`:

- Format: JSON
- Timeout: 15 seconds per request
- Authentication: No authentication required (public API)

### Error Handling

- Invalid requests return descriptive `ToolError` exceptions
- Network timeouts are handled with appropriate error messages

## Development

### Project Structure
```
finapi-mcp-server/
├── main.py                    # Server entry point
├── requirements.txt           # Python dependencies
├── README.md                  # Project documentation
├── tools/
│   ├── __init__.py
│   └── tools.py              # Tool implementations
└── prod-deployment-scripts/  # Production deployment configuration
```

### Dependencies

- **fastmcp** (>=2.14.5): Model Context Protocol server framework
- **fastapi** (>=0.128.0): Web framework for HTTP transport
- **httpx**: Async HTTP client for API calls
- **cyclopts** (>=5.0.0a1): CLI framework

## Security Considerations

1. **Public API**: All tools are unauthenticated - they access public market data
2. **No Session Management**: Server does not maintain session state
3. **HTTPS**: All API communication uses HTTPS
4. **Read-Only**: All endpoints are read-only analytics queries
5. **Rate Limiting**: Subject to FinAPI API rate limits

## Troubleshooting

### Connection Issues
- Ensure FinAPI API is accessible at `https://api.finapi.upvaly.com`
- Check network connectivity
- Verify HTTP timeout settings (15s default)

### Tool Failures
- Review error message for specific API error details
- Ensure required parameters are provided
- Check FinAPI API documentation for endpoint specifics

## Support

For issues related to:
- **FinAPI Platform**: Visit [FinAPI](https://api.finapi.upvaly.com)
- **MCP Protocol**: See [Model Context Protocol](https://modelcontextprotocol.io)
- **FastMCP**: Check [FastMCP GitHub](https://github.com/jlowin/fastmcp)

## License

This project is provided as-is for access to FinAPI analytics data.

## Disclaimer

This MCP server provides programmatic access to financial market analytics data. Use responsibly for research, analysis, and investment discovery. Always verify data accuracy and consult with financial advisors before making investment decisions.
