import unittest

from auth.api_key import ApiKeyOrBearerAuthBackend


class _Connection:
    def __init__(self, headers: dict[str, str]):
        self.headers = headers


class _Verifier:
    async def verify_token(self, token: str):
        return None


class ApiKeyAuthTests(unittest.IsolatedAsyncioTestCase):
    async def test_api_key_header_authenticates_without_bearer_token(self):
        backend = ApiKeyOrBearerAuthBackend(_Verifier(), ["openid", "email"])

        result = await backend.authenticate(
            _Connection({"x-api-key": "fna_test_key"})
        )

        self.assertIsNotNone(result)
        credentials, user = result
        self.assertEqual(credentials.scopes, ["openid", "email"])
        self.assertEqual(user.access_token.claims["api_key"], "fna_test_key")

    async def test_api_key_header_takes_precedence_over_cached_bearer_token(self):
        backend = ApiKeyOrBearerAuthBackend(_Verifier(), ["openid"])

        result = await backend.authenticate(
            _Connection(
                {
                    "authorization": "Bearer cached-oauth-token",
                    "x-api-key": "fna_configured_key",
                }
            )
        )

        self.assertEqual(result[1].access_token.claims["api_key"], "fna_configured_key")

    async def test_missing_credentials_are_rejected(self):
        backend = ApiKeyOrBearerAuthBackend(_Verifier(), [])

        result = await backend.authenticate(_Connection({}))

        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
