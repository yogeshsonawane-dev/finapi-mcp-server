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
- `GOOGLE_CLIENT_ID`: Google OAuth client ID (e.g. `123456789.apps.googleusercontent.com`). Enables OAuth on the MCP server.
- `GOOGLE_CLIENT_SECRET`: Google OAuth client secret.
- `MCP_PUBLIC_URL`: Public HTTPS base URL where the server is reachable (e.g. `https://mcp.example.com`). Required for OAuth.
- `FINAPI_SUBSCRIPTION_API_URL`: URL of the FinAPI internal endpoint that resolves an email to the user's active FinAPI API key. When set (with the API key), per-user key resolution is enabled.
- `FINAPI_SUBSCRIPTION_API_KEY`: Shared secret sent to the subscription endpoint.
- `FINAPI_SUBSCRIPTION_API_HEADER`: Header used for the secret (default: `X-API-Key`).
- `FINAPI_SUBSCRIPTION_CACHE_TTL`: Cache TTL for resolved keys in seconds (default: 300).
- `FINAPI_SUBSCRIPTION_NEGATIVE_CACHE_TTL`: Cache TTL for "user not found" / "no key" lookups in seconds (default: 60).
- `FINAPI_SUBSCRIPTION_API_TIMEOUT`: Timeout for the subscription request (default: 5s).

When `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, and `MCP_PUBLIC_URL` are all set, the server runs with OAuth protection. Otherwise it runs unauthenticated as before.

## OAuth Authentication (Google Sign-In)

Claude.ai web does not support MCP servers that require API keys; instead it requires the server to implement the [MCP OAuth 2.0 authorization flow](https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization). This server uses FastMCP's built-in `GoogleProvider`, which implements the full flow (authorization endpoint, PKCE, token exchange, and consent) with a "Sign in with Google" button.

### How it works

When OAuth is enabled, the server exposes these endpoints (served over Streamable HTTP):

- `/.well-known/oauth-authorization-server` and `/.well-known/openid-configuration` — OAuth discovery metadata
- `/authorize` — MCP client authorization
- `/token` — token exchange
- `/register` — dynamic client registration
- `/auth/callback` — Google OAuth callback

A user connecting (e.g. in Claude) is redirected to Google to sign in, then back, and their session is authorized to call the server's tools.

### Prerequisites

1. **A public HTTPS URL** for the server. OAuth requires a publicly reachable endpoint with a valid TLS certificate (localhost will not work for Claude.ai web). Deploy behind a reverse proxy (nginx, Caddy, a load balancer, etc.) or a tunnel.

2. **A Google OAuth app** in the [Google Cloud Console](https://console.cloud.google.com/apis/credentials):
   - Create an OAuth client ID of type **Web application**.
   - Add `https://accounts.google.com` as an authorized JavaScript origin.
   - Add `<MCP_PUBLIC_URL>/auth/callback` as an authorized redirect URI (e.g. `https://mcp.example.com/auth/callback`).
   - Note the client ID and client secret.

### Configuration

Start the server with OAuth enabled:

```bash
export GOOGLE_CLIENT_ID="123456789.apps.googleusercontent.com"
export GOOGLE_CLIENT_SECRET="GOCSPX-..."
export MCP_PUBLIC_URL="https://mcp.example.com"
python main.py
```

### Connecting from Claude

1. In Claude, add an MCP server of type **OAuth 2.0** / **Custom** and enter your `MCP_PUBLIC_URL`.
2. Claude discovers the OAuth endpoints and opens the authorization URL.
3. Sign in with Google and approve the consent screen.
4. Claude stores the token and can now call the FinAPI tools.

> **Note:** FinAPI's own "Sign in with Google" button belongs to FinAPI's platform and cannot be reused. The OAuth app configured above is independent and controls who can access your MCP server.

### Hosted API-key configuration

For Claude Desktop using `mcp-remote`, pass the key as a forwarded HTTP header. An `env` value by itself only sets an environment variable for the local `mcp-remote` process; it is not sent to the hosted server.

```json
{
  "mcpServers": {
    "finapi": {
      "command": "npx",
      "args": [
        "mcp-remote",
        "https://mcp.finapi.upvaly.com/mcp",
        "--header",
        "X-API-Key:${FINAPI_API_KEY}"
      ],
      "env": {
        "FINAPI_API_KEY": "fna_live_your_key"
      }
    }
  }
}
```

With `X-API-Key` configured, the hosted server accepts the request directly and does not start OAuth. Keep the key private; anyone who obtains it can use the associated FinAPI account.

### API Key Resolution (a key is required)

An API key is **required** to use the MCP server. It is obtained one of three ways:

1. **Configure a key in a locally launched server** — set `FINAPI_API_KEY` in the server env. The key is used directly on every analytics call and OAuth login is skipped entirely.
2. **Pass a key to the hosted server** — send `X-API-Key` on MCP requests. This is the bring-your-own-key option for `mcp.finapi.upvaly.com`; it takes precedence over a cached OAuth token and OAuth is skipped.
3. **Google OAuth login** — when neither a server key nor an `X-API-Key` header is present, the server requires OAuth. After login it reads the caller's Google email and asks FinAPI's subscription endpoint to resolve the user's latest active API key.

The resolved key is cached per email (5 min by default). Outcomes from the subscription lookup are surfaced to the AI:

- **User not found (HTTP 404)** → the tool tells the user their Google account isn't registered on FinAPI, and to create a profile at `https://finapi.upvaly.com`, then either add the API key to the MCP config (`FINAPI_API_KEY`) or log in with the same email.
- **User found but no key (`{"api_key": null}`)** → the tool tells the user to create at least one API key at `https://finapi.upvaly.com`.
- **User found with key** → the key is used for all subsequent calls.

**Expected subscription endpoint contract** (implemented on your FinAPI server):

```
GET {FINAPI_SUBSCRIPTION_API_URL}?email=user@example.com
Header: X-API-Key: <FINAPI_SUBSCRIPTION_API_KEY>

200 OK (has key): {"api_key": "abc-123..."}
200 OK (no key):  {"api_key": null}
404 (unknown user)
```

## Getting Google OAuth Credentials

To get `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`:

1. Go to the [Google Cloud Console](https://console.cloud.google.com/) and create/select a project.
2. Search for and enable **Google Identity Services** (OAuth consent screen is configured under "APIs & Services" → "OAuth consent screen").
3. Under **APIs & Services → OAuth consent screen**: choose *External*, add your app name, and add `https://accounts.google.com` and your public origin as *Authorized domains*.
4. Under **APIs & Services → Credentials → Create Credentials → OAuth client ID**:
   - **Application type**: *Web application*
   - **Authorized JavaScript origins**: add `https://accounts.google.com`
   - **Authorized redirect URIs**: add `<MCP_PUBLIC_URL>/auth/callback` (e.g. `https://mcp.example.com/auth/callback` or `http://localhost:8004/auth/callback` for local testing — Google allows `http://localhost` for development)
5. Copy the **Client ID** and **Client secret** into `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`.

### What is `MCP_PUBLIC_URL`?

It is the public HTTPS URL where the MCP server's OAuth endpoints are reachable. Google must be able to redirect users back to `<MCP_PUBLIC_URL>/auth/callback`, so it must match an entry in your OAuth app's redirect URIs.

- **Local testing**: `http://localhost:8004` (works without a tunnel; add `http://localhost:8004/auth/callback` to Google).
- **Testing with Claude.ai web**: a public HTTPS URL. Use a tunnel (`ngrok http 8004`, `cloudflared tunnel --url http://localhost:8004`) or deploy behind a reverse proxy with TLS. Claude cannot reach localhost, and Google requires HTTPS except for localhost.
- **Production**: your deployed domain, e.g. `https://mcp.example.com`.

## Testing

### 1. Smoke test the OAuth endpoints (no browser)

Run the server with OAuth enabled, then check discovery metadata:

```bash
GOOGLE_CLIENT_ID=... GOOGLE_CLIENT_SECRET=... MCP_PUBLIC_URL=http://localhost:8004 python main.py
```

```bash
curl http://localhost:8004/.well-known/oauth-authorization-server
# -> 200, shows authorization_endpoint + token_endpoint

curl http://localhost:8004/mcp
# -> 401 (protected, expected)
```

### 2. Full OAuth flow test (browser + real Google sign-in)

`test_oauth.py` starts the server, checks discovery, then connects as an OAuth client which opens a browser for Google sign-in:

```bash
GOOGLE_CLIENT_ID=... GOOGLE_CLIENT_SECRET=... MCP_PUBLIC_URL=http://localhost:8004 python test_oauth.py
```

Expected output: the discovery endpoints return 200, the browser opens, you sign in with Google, and `check_health` returns data.

### 3. Test per-user key resolution (no Google needed)

Mock the subscription endpoint and verify pro users get a key and free users don't (as shown in the development session). Point `FINAPI_SUBSCRIPTION_API_URL` at a stub that returns `{"api_key": "..."}` for a pro email, then confirm the `X-API-Key` header on outgoing FinAPI analytics calls.

### 4. Test with Claude.ai web

1. Start a tunnel to your server: `ngrok http 8004`, take the HTTPS URL as `MCP_PUBLIC_URL`.
2. Add `<tunnel-url>/auth/callback` to your Google OAuth app's redirect URIs.
3. Start the server with `MCP_PUBLIC_URL=<tunnel-url>`.
4. In Claude, add an MCP server (type OAuth) with that URL; complete the Google sign-in.

### Server Details
- **Name**: FinAPI MCP Server
- **Transport**: HTTP
- **Port**: 8004
- **API Base**: `https://api.finapi.upvaly.com`

## Usage

### Authentication
The server accepts either OAuth or a client-provided `X-API-Key` header. For a locally launched server, you can configure the key through `FINAPI_API_KEY`:

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

For the hosted server, use the `mcp-remote --header` configuration shown above. The header key takes precedence over a cached OAuth identity. Requests without a header continue through Google OAuth and per-user subscription lookup.

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

1. **Public API**: The underlying FinAPI API is public - the tools access public market data
2. **Server Auth**: When `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, and `MCP_PUBLIC_URL` are set, MCP clients must sign in with Google before calling any tool. Without them, the server runs unauthenticated
3. **No Session Management**: Server does not maintain its own session state
4. **HTTPS**: All API communication uses HTTPS
5. **Read-Only**: All endpoints are read-only analytics queries
6. **Rate Limiting**: Subject to FinAPI API rate limits

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
