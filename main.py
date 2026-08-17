import os

from dotenv import load_dotenv
from fastmcp import FastMCP

from auth.api_key import GoogleProviderWithApiKey
from auth.subscription import tier_client_from_env
from tools.tools import set_tier_client, setup_tools

load_dotenv()


def _build_auth():
    # A key configured in the MCP config means no OAuth is needed.
    if os.getenv("FINAPI_API_KEY"):
        return None
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
    base_url = os.getenv("MCP_PUBLIC_URL")
    if not (client_id and client_secret and base_url):
        return None
    return GoogleProviderWithApiKey(
        client_id=client_id,
        client_secret=client_secret,
        base_url=base_url,
        required_scopes=["openid", "email"],
    )


mcp = FastMCP(
    name="FinAPI MCP Server",
    instructions="""
        This server provides mutual fund and IPO related information tools. The mutual fund tools include fetching the latest NAV, historical NAV, portfolio allocation, holdings, and fund performance. The IPO tools provide details about upcoming IPOs, including company information, expected listing date, and price range. Use these tools to get accurate and up-to-date financial information.
    """,
    auth=_build_auth(),
)

tier_client = tier_client_from_env()
if tier_client is not None:
    set_tier_client(tier_client)

setup_tools(mcp)

if __name__ == "__main__":
    mcp.run(transport="http", port=int(os.getenv("MCP_PORT", "8004")))
