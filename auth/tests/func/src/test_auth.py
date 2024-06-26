from http import HTTPStatus

import pytest
from settings import get_settings
from testdata.auth import GET_REFRESH_TOKEN_REQUEST, TOKENS
from testdata.common import AUTH_HEADERS
from testdata.personal import SUPERUSER_DATA

from util.token_helpers import decode_payload_helper, generate_sign_helper

pytestmark = pytest.mark.authorization
pytestmark = pytest.mark.asyncio

URL = f"{get_settings().API_URL}/auth"


async def test_login_returns_correct_json(prepare_users, get_http_session):
    """Checks that a login API returns json with correct fields."""
    url = f"{URL}/login"
    data = (
        f"grant_type=&username={SUPERUSER_DATA["login"]}&"
        f"password={SUPERUSER_DATA["password"]}&scope=&client_id=&client_secret="
    )

    response = await get_http_session.post(
        url=url, headers=AUTH_HEADERS, data=data
    )
    body = await response.json()
    status = response.status

    # Checks if request is valid
    assert status == HTTPStatus.OK
    assert "access_token" in body
    assert "refresh_token" in body
    assert "token_type" in body


@pytest.mark.parametrize("token", TOKENS)
async def test_login_returns_correct_token_data(
    prepare_users, get_http_session, token
):
    """Checks that a login API returns correct access and refresh tokens."""
    url = f"{URL}/login"
    data = (
        f"grant_type=&username={SUPERUSER_DATA["login"]}&"
        f"password={SUPERUSER_DATA["password"]}&scope=&client_id=&client_secret="
    )

    response = await get_http_session.post(
        url=url, headers=AUTH_HEADERS, data=data
    )
    body = await response.json()
    status = response.status

    # Checks are tokens valid
    assert status == HTTPStatus.OK
    token_parts = body[token["type"]].split(".")

    assert len(token_parts) == 3

    # Checks that token headers are valid
    assert token_parts[0] == "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9"

    # Checks that token payloads are valid
    token_payload = await decode_payload_helper(token_parts[1])

    for field in token["payload_fields"]:
        assert field in token_payload


@pytest.mark.parametrize("token", TOKENS)
async def test_login_returns_correct_token_sign(
    prepare_users, get_http_session, token
):
    """Checks that an API returns correct header and payload sign."""
    url = f"{URL}/login"
    data = (
        f"grant_type=&username={SUPERUSER_DATA["login"]}&"
        f"password={SUPERUSER_DATA["password"]}&scope=&client_id=&client_secret="
    )

    response = await get_http_session.post(
        url=url, headers=AUTH_HEADERS, data=data
    )
    body = await response.json()
    status = response.status

    # Checks that tokens have correct signs
    assert status == HTTPStatus.OK
    token_parts = body[token["type"]].split(".")

    assert token_parts[2] == await generate_sign_helper(
        token_parts=token_parts
    )


async def test_login_saves_refresh_token(
    prepare_users, get_http_session, get_postgres_session
):
    """Checks that an API saves refresh token in the refresh_token table."""
    url = f"{URL}/login"
    data = (
        f"grant_type=&username={SUPERUSER_DATA["login"]}&"
        f"password={SUPERUSER_DATA["password"]}&scope=&client_id=&client_secret="
    )

    response = await get_http_session.post(
        url=url, headers=AUTH_HEADERS, data=data
    )
    body = await response.json()
    status = response.status

    assert status == HTTPStatus.OK

    row = await get_postgres_session.fetchrow(GET_REFRESH_TOKEN_REQUEST)

    # Checks does a token exist in the database
    assert body["refresh_token"] == row["refresh_token"]


async def test_refresh_returns_correct_json(
    get_superuser_refresh_token, get_http_session
):
    """Checks that a refresh API returns json with correct fields."""
    url = f"{URL}/refresh"
    data = get_superuser_refresh_token

    response = await get_http_session.post(
        url=url, headers=AUTH_HEADERS, data=data
    )
    body = await response.json()
    status = response.status

    # Checks if request is valid
    assert status == HTTPStatus.OK
    assert "access_token" in body
    assert "refresh_token" in body
    assert "token_type" in body


@pytest.mark.parametrize("token", TOKENS)
async def test_refresh_returns_correct_token_data(
    get_superuser_refresh_token, get_http_session, token
):
    """Checks that a refresh API returns correct access and refresh tokens."""
    url = f"{URL}/refresh"
    data = get_superuser_refresh_token

    response = await get_http_session.post(
        url=url, headers=AUTH_HEADERS, data=data
    )
    body = await response.json()
    status = response.status

    # Checks are tokens valid
    assert status == HTTPStatus.OK
    token_parts = body[token["type"]].split(".")

    assert len(token_parts) == 3

    # Checks that token headers are valid
    assert token_parts[0] == "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9"

    # Checks that token payloads are valid
    token_payload = await decode_payload_helper(token_parts[1])

    for field in token["payload_fields"]:
        assert field in token_payload


@pytest.mark.parametrize("token", TOKENS)
async def test_refresh_returns_correct_token_sign(
    get_superuser_refresh_token, get_http_session, token
):
    """Checks that a refresh API returns correct header and payload sign."""
    url = f"{URL}/refresh"
    data = get_superuser_refresh_token

    response = await get_http_session.post(
        url=url, headers=AUTH_HEADERS, data=data
    )
    body = await response.json()
    status = response.status

    # Checks that tokens have a correct sign
    assert status == HTTPStatus.OK
    token_parts = body[token["type"]].split(".")

    assert token_parts[2] == await generate_sign_helper(
        token_parts=token_parts
    )


async def test_refresh_deletes_token(
    get_superuser_refresh_token, get_http_session, get_postgres_session
):
    """Checks that a refresh API deletes the initial refresh_token."""
    url = f"{URL}/refresh"
    data = get_superuser_refresh_token

    response = await get_http_session.post(
        url=url, headers=AUTH_HEADERS, data=data
    )
    status = response.status

    assert status == HTTPStatus.OK

    row = await get_postgres_session.fetchrow(GET_REFRESH_TOKEN_REQUEST)

    # Checks does a token exist in the database
    assert data != row["refresh_token"]


async def test_refresh_saves_token(
    get_superuser_refresh_token, get_http_session, get_postgres_session
):
    """Checks that a refresh API saves a new token."""
    url = f"{URL}/refresh"
    data = get_superuser_refresh_token

    response = await get_http_session.post(
        url=url, headers=AUTH_HEADERS, data=data
    )
    body = await response.json()
    status = response.status

    assert status == HTTPStatus.OK

    row = await get_postgres_session.fetchrow(GET_REFRESH_TOKEN_REQUEST)

    # Checks does a token exist in the database
    assert body["refresh_token"] == row["refresh_token"]


async def test_logout_deletes_token(
    prepare_headers_with_superuser_token,
    insert_superuser_refresh_token,
    get_http_session,
    get_postgres_session,
):
    """Checks that a logout API deletes refresh_token."""
    url = f"{URL}/logout"

    response = await get_http_session.post(
        url=url, headers=prepare_headers_with_superuser_token
    )
    status = response.status

    assert status == HTTPStatus.OK

    row = await get_postgres_session.fetchrow(GET_REFRESH_TOKEN_REQUEST)

    # Checks that a token doesn't exist in the database
    assert not row


async def test_logout_emplaces_invalid_token_in_redis(
    prepare_headers_with_superuser_token,
    insert_superuser_refresh_token,
    redis_flush,
    redis_save_superuser_access_token,
    get_http_session,
    get_redis_session,
):
    """Checks that logout API put acces_token to redis."""

    url = f"{URL}/logout"

    response = await get_http_session.post(
        url=url, headers=prepare_headers_with_superuser_token
    )
    status = response.status

    assert status == HTTPStatus.OK

    # Checks that an access token exists in the cache
    assert "deleted" == await get_redis_session.get(
        prepare_headers_with_superuser_token["Authorization"].replace(
            "Bearer ", ""
        )
    )
