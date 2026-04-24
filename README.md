# Famvest MCP Server

A Model Context Protocol (MCP) server that integrates with the Famvest portfolio management platform, enabling AI assistants to access and analyze your investment portfolio data.

## Overview

The Famvest MCP Server provides a secure gateway for AI assistants to interact with your Famvest account. It implements the Model Context Protocol to offer AI systems safe, authenticated access to portfolio management tools and data.

## Features

### Portfolio Management
- **Stock Holdings**: Retrieve current stock holdings with quantity and value information
- **Mutual Fund Holdings**: Access mutual fund portfolio data and holdings
- **Positions**: View active positions and open trades with entry/current prices and P&L
- **Orders**: Track recent stock orders and execution details
- **Mutual Fund Orders**: Monitor mutual fund order history and status
- **SIPs**: Manage and view Systematic Investment Plan (SIP) details

### Market Intelligence
- **Gainers & Losers**: Identify top performing and underperforming holdings across multiple timeframes (1D, 1W, 1M, 3M, 6M, 1Y)
- **Market Timings**: Check exchange open/close times and market hours
- **Market Holidays**: View scheduled market holidays
- **Upcoming Expiries**: Track derivative contract expiry dates
- **IPO Management**: Browse available IPOs and manage IPO applications

### Account Management
- **User Profile**: Access your profile information and preferences
- **Account Profiles**: View linked trading accounts
- **Funds**: Check account balance and fund availability

### Search & Discovery
- **Instrument Search**: Find trading instruments by symbol, token, or exchange

### Admin Features
- **Schedulers**: Monitor scheduled job status and execution history
- **Application Users**: View system users (admin access required)

## Installation

### Prerequisites
- Python 3.14 or higher
- pip or uv package manager

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd famvest-mcp-server
```

2. Install dependencies:
```bash
# Using pip
pip install -r requirements.txt

# Or using uv
uv install
```

3. Run the server:
```bash
python main.py
```

The server will start on `http://localhost:8003` with HTTP transport.

## Configuration

### Environment Variables
- `MCP_PORT`: Port for the MCP server (default: 8003)

### Server Details
- **Name**: Famvest MCP Server
- **Transport**: HTTP
- **Port**: 8003
- **API Base**: `https://famvest.upvaly.com`

## Usage

### Authentication

All tools (except `login`) require authentication:

1. Call the `login()` tool to get login instructions
2. Follow the provided login URL and complete authentication
3. The server will automatically manage session tokens for subsequent API calls

⚠️ **Security Warning**: AI systems are unpredictable and non-deterministic. Use with caution when connecting to real trading accounts.

### Tool Invocation

Example usage patterns:

```
# Check authentication
login()

# Get portfolio overview
get_stock_holdings()
get_mutual_fund_holdings()
get_funds()

# Analyze performance
get_gainers_losers(timeframe="3M")

# Check account status
get_positions()
get_orders()

# Market information
get_market_timings()
get_market_holidays()
```

## Architecture

### Middleware Pipeline

The server implements a two-stage middleware pipeline:

1. **OnRequestMiddleware** (`middleware/on_request_middleware.py`)
   - Extracts and stores session ID from incoming MCP requests
   - Manages session context for downstream components

2. **OnCallToolMiddleware** (`middleware/on_call_tool_middleware.py`)
   - Intercepts all tool calls (except `login`)
   - Fetches authentication tokens using session ID
   - Automatically injects Bearer token into API requests
   - Enforces login requirement for protected endpoints

### Core Components

- **main.py**: Server entry point and FastMCP initialization
- **tools/tools.py**: Tool definitions and implementation
- **middleware/**: Request/response processing pipeline

## API Integration

The server communicates with the Famvest API at `https://famvest.upvaly.com/rest/v1/`:

- Authentication: Bearer token in Authorization header
- Format: JSON
- Timeout: 10 seconds per request

### Error Handling

- Invalid requests return descriptive `ToolError` exceptions
- Authentication failures trigger login prompts
- Network timeouts are handled with appropriate error messages

## Development

### Project Structure
```
famvest-mcp-server/
├── main.py                    # Server entry point
├── pyproject.toml            # Project metadata
├── requirements.txt          # Python dependencies
├── tools/
│   ├── __init__.py
│   └── tools.py             # Tool implementations
└── middleware/
    ├── __init__.py
    ├── on_request_middleware.py
    └── on_call_tool_middleware.py
```

### Dependencies

- **fastmcp** (>=2.14.5): Model Context Protocol server framework
- **fastapi** (>=0.128.0): Web framework for HTTP transport
- **httpx**: Async HTTP client for API calls
- **cyclopts** (>=5.0.0a1): CLI framework
- **ipykernel**: Jupyter kernel support

## Security Considerations

1. **Authentication**: All tool access requires successful Famvest login
2. **Session Management**: Server manages tokens via session IDs
3. **Authorization**: Token-based authorization for all API calls
4. **HTTPS**: All API communication uses HTTPS
5. **Scope**: AI assistants can only access your own account data

## Troubleshooting

### Connection Issues
- Ensure Famvest API is accessible at `https://famvest.upvaly.com`
- Check network connectivity
- Verify HTTP timeout settings (10s default)

### Authentication Errors
- Confirm login was completed successfully
- Check session ID validity
- Verify token is not expired

### Tool Failures
- Review error message for specific API error details
- Ensure required parameters are provided
- Check Famvest API documentation for endpoint specifics

## Support

For issues related to:
- **Famvest Platform**: Visit [Famvest](https://famvest.upvaly.com)
- **MCP Protocol**: See [Model Context Protocol](https://modelcontextprotocol.io)
- **FastMCP**: Check [FastMCP GitHub](https://github.com/jlowin/fastmcp)

## License

This project is provided as-is for integration with the Famvest platform.

## Disclaimer

This MCP server provides programmatic access to your trading account. Use responsibly and ensure you understand the implications of AI-driven portfolio decisions. Always review actions before they execute on your account.
