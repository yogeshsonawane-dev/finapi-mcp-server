"""Resolve the FinAPI analytics API key for a user from the FinAPI platform.

The FinAPI server owns the subscription data in its Postgres DB. Instead of
giving this MCP server DB access, we call a small internal API on the FinAPI
platform that resolves a Google email to the user's latest active FinAPI API
key.

A key is required to use this MCP server, so the lookup distinguishes:
- user not found (HTTP 404) -> tell the user to create a FinAPI profile
- user found but no key (HTTP 200 + null) -> tell the user to create a key
- user found with key -> return the key for all subsequent analytics calls

Successful keys are cached per email; negative lookups are cached briefly so a
user's next attempt reflects the action they just took on FinAPI.
"""

from __future__ import annotations

import logging
import os
import time
from dataclasses import dataclass

import httpx

logger = logging.getLogger(__name__)

DEFAULT_HEADER = "X-API-Key"
DEFAULT_CACHE_TTL = 300
DEFAULT_NEGATIVE_CACHE_TTL = 60
DEFAULT_TIMEOUT = 5.0

_KEY_FIELDS = ("api_key", "key", "finapi_api_key", "x_api_key")


@dataclass
class SubscriptionResult:
    """Outcome of a subscription lookup for a user email.

    ``user_found`` is True when the user exists on FinAPI, False when the API
    reports the user does not exist (HTTP 404), and None when the lookup itself
    failed (transient error). ``api_key`` is the active key when one exists.
    """

    user_found: bool | None
    api_key: str | None

    @property
    def ok(self) -> bool:
        return self.user_found is True and bool(self.api_key)


class TierClient:
    """Async client for resolving a user email to an active FinAPI API key."""

    def __init__(
        self,
        url: str,
        api_key: str,
        header: str = DEFAULT_HEADER,
        timeout: float = DEFAULT_TIMEOUT,
        cache_ttl: int = DEFAULT_CACHE_TTL,
        negative_cache_ttl: int = DEFAULT_NEGATIVE_CACHE_TTL,
    ) -> None:
        self.url = url
        self.api_key = api_key
        self.header = header
        self.timeout = timeout
        self.cache_ttl = cache_ttl
        self.negative_cache_ttl = negative_cache_ttl
        self._cache: dict[str, tuple[float, SubscriptionResult]] = {}
        self._client = httpx.AsyncClient(timeout=timeout)

    async def aclose(self) -> None:
        await self._client.aclose()

    @staticmethod
    def _parse_key(payload: dict) -> str | None:
        for field in _KEY_FIELDS:
            value = payload.get(field)
            if isinstance(value, str) and value.strip():
                return value.strip()
        return None

    async def get_api_key(self, email: str) -> SubscriptionResult:
        """Resolve an email to the active FinAPI API key.

        Successes are cached for ``cache_ttl`` seconds; user-not-found and
        no-key results are cached for ``negative_cache_ttl`` seconds so the
        user's next attempt picks up the action they took on FinAPI quickly.
        """
        cached = self._cache.get(email)
        if cached:
            age = time.time() - cached[0]
            cached_result = cached[1]
            ttl = (
                self.cache_ttl
                if cached_result.ok
                else self.negative_cache_ttl
            )
            if age < ttl:
                return cached_result

        result = await self._lookup(email)
        # Transient failures are not cached, so a later call retries.
        if result.user_found is not None:
            self._cache[email] = (time.time(), result)
        return result

    async def _lookup(self, email: str) -> SubscriptionResult:
        try:
            response = await self._client.get(
                self.url,
                params={"email": email},
                headers={self.header: self.api_key},
            )
            if response.status_code == 404:
                return SubscriptionResult(user_found=False, api_key=None)
            if response.status_code == 200:
                return SubscriptionResult(
                    user_found=True, api_key=self._parse_key(response.json())
                )
            logger.warning(
                "Subscription lookup for %s returned HTTP %d",
                email,
                response.status_code,
            )
            return SubscriptionResult(user_found=None, api_key=None)
        except httpx.HTTPError as e:
            logger.warning("Subscription lookup for %s failed: %s", email, e)
            return SubscriptionResult(user_found=None, api_key=None)


def tier_client_from_env() -> TierClient | None:
    """Build a TierClient from environment variables, or None if not configured."""
    url = os.getenv("FINAPI_SUBSCRIPTION_API_URL")
    api_key = os.getenv("FINAPI_SUBSCRIPTION_API_KEY")
    if not (url and api_key):
        return None
    return TierClient(
        url=url,
        api_key=api_key,
        header=os.getenv("FINAPI_SUBSCRIPTION_API_HEADER", DEFAULT_HEADER),
        timeout=float(os.getenv("FINAPI_SUBSCRIPTION_API_TIMEOUT", DEFAULT_TIMEOUT)),
        cache_ttl=int(os.getenv("FINAPI_SUBSCRIPTION_CACHE_TTL", DEFAULT_CACHE_TTL)),
        negative_cache_ttl=int(
            os.getenv("FINAPI_SUBSCRIPTION_NEGATIVE_CACHE_TTL", DEFAULT_NEGATIVE_CACHE_TTL)
        ),
    )