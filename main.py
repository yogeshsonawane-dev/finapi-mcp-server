from fastmcp import FastMCP
from tools.tools import setup_tools

mcp = FastMCP(
    name="FinAPI MCP Server",
    instructions="""
        This server provides mutual fund and IPO related information tools. The mutual fund tools include fetching the latest NAV, historical NAV, portfolio allocation, holdings, and fund performance. The IPO tools provide details about upcoming IPOs, including company information, expected listing date, and price range. Use these tools to get accurate and up-to-date financial information.
    """,
)


setup_tools(mcp)

if __name__ == "__main__":
    mcp.run(transport="http", port=8004)