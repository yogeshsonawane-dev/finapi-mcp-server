"""End-to-end test for the OAuth-protected MCP server.

Starts the server with the configured Google OAuth provider, smoke-tests the
OAuth discovery endpoints, then connects as an OAuth client and calls a tool.

The full-flow part opens a browser so you can sign in with Google.

Usage:
    GOOGLE_CLIENT_ID=... \
    GOOGLE_CLIENT_SECRET=... \
    MCP_PUBLIC_URL=http://localhost:8004 \
    python test_oauth.py
"""

from __future__ import annotations

import asyncio
import os
import threading

import httpx
import uvicorn
from fastmcp import Client

import main as server_module

PORT = int(os.getenv("MCP_PORT", "8004"))
BASE_URL = os.getenv("MCP_PUBLIC_URL", f"http://localhost:{PORT}")


def _start_server() -> threading.Thread:
    config = uvicorn.Config(
        server_module.mcp.http_app(transport="streamable-http"),
        host="127.0.0.1",
        port=PORT,
        log_level="warning",
    )
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    return thread


async def _smoke_test_discovery() -> None:
    print("== Discovery endpoint smoke test ==")
    async with httpx.AsyncClient() as client:
        for path in (
            "/.well-known/oauth-authorization-server",
            "/.well-known/oauth-protected-resource/mcp",
        ):
            r = await client.get(f"{BASE_URL}{path}")
            ok = "OK" if r.status_code == 200 else "FAIL"
            print(f"  {path} -> {r.status_code} {ok}")
            if ok == "OK":
                print(f"    authorization_endpoint: {r.json().get('authorization_endpoint')}")
                print(f"    token_endpoint: {r.json().get('token_endpoint')}")
        r = await client.get(f"{BASE_URL}/mcp")
        print(f"  /mcp (unauthenticated) -> {r.status_code} (401 = protected OK)")


async def _full_oauth_flow() -> None:
    print("== Full OAuth flow ==")
    print("A browser will open for Google sign-in. Complete it to continue.\n")
    async with Client(f"{BASE_URL}/mcp", auth="oauth") as client:
        tools = await client.list_tools()
        print(f"Connected. Found {len(tools)} tools.")
        result = await client.call_tool("check_health")
        print("check_health ->", result)


async def main() -> None:
    _start_server()
    await asyncio.sleep(1.0)

    if not (os.getenv("GOOGLE_CLIENT_ID") and os.getenv("GOOGLE_CLIENT_SECRET")):
        print("Set GOOGLE_CLIENT_ID/GOOGLE_CLIENT_SECRET/MCP_PUBLIC_URL first.")
        return

    await _smoke_test_discovery()
    await _full_oauth_flow()


if __name__ == "__main__":
    asyncio.run(main())