"""Allow hosted clients to authenticate with a FinAPI API key header."""

from __future__ import annotations

from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware

from fastmcp.server.auth.auth import AccessToken
from fastmcp.server.auth.providers.google import GoogleProvider
from mcp.server.auth.middleware.bearer_auth import (
    AuthCredentials,
    AuthenticatedUser,
    BearerAuthBackend,
)
from mcp.server.auth.middleware.auth_context import AuthContextMiddleware
from starlette.requests import HTTPConnection


API_KEY_HEADER = "x-api-key"


class ApiKeyOrBearerAuthBackend(BearerAuthBackend):
    """Accept a FinAPI API key or a valid OAuth bearer token.

    The API-key path is deliberately checked first so a client can override a
    previously cached OAuth token by explicitly supplying its own key.
    """

    def __init__(self, token_verifier, required_scopes: list[str]):
        super().__init__(token_verifier)
        self.required_scopes = required_scopes

    async def authenticate(self, conn: HTTPConnection):
        api_key = conn.headers.get(API_KEY_HEADER, "").strip()
        if api_key:
            access_token = AccessToken(
                token="",
                client_id="finapi-api-key",
                scopes=self.required_scopes,
                claims={"api_key": api_key},
            )
            return AuthCredentials(self.required_scopes), AuthenticatedUser(
                access_token
            )

        return await super().authenticate(conn)


class GoogleProviderWithApiKey(GoogleProvider):
    """Google OAuth with API-key-header authentication for hosted clients."""

    def get_middleware(self) -> list[Middleware]:
        return [
            Middleware(
                AuthenticationMiddleware,
                backend=ApiKeyOrBearerAuthBackend(self, self.required_scopes),
            ),
            Middleware(AuthContextMiddleware),
        ]
