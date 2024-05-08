import uuid
from http import HTTPStatus
from typing import Annotated

from core.config import get_settings
from db.postgres.session_handler import session_handler
from db.redis.redis_storage import RedisStorage, get_redis_storage
from fastapi import (
    APIRouter,
    Depends,
    Header,
    HTTPException,
    Path,
    Query,
    Request,
    Security,
)
from fastapi.responses import RedirectResponse
from schemas.oauth import OAuthProviderDataSchema
from schemas.token import TokenCheckResponse, UserTokenPair
from services.oauth_service import OAuthService, get_oauth_service
from sqlalchemy.ext.asyncio import AsyncSession
from util.JWT_helper import silent_token_checker, strict_token_checker

router = APIRouter()


@router.get("/unlink/{provider}")
async def unlink_oauth_account(
    provider: Annotated[str, Path()],
    token_check_data: Annotated[
        TokenCheckResponse, Security(strict_token_checker)
    ],
    session: Annotated[AsyncSession, Depends(session_handler.create_session)],
    oauth_service: Annotated[OAuthService, Depends(get_oauth_service)],
):
    oauth_account = await oauth_service.unlink(
        session=session, provider=provider, user_login=token_check_data.sub
    )
    return {
        "status": f"{oauth_account.provider} account has been successfully detached."
    }


@router.get(
    "/page/{provider}",
    description="URL to redirect users to Authorization provider page.",
)
async def oauth_redirect_page(
    provider: Annotated[str, Path()],
    oauth_service: Annotated[OAuthService, Depends(get_oauth_service)],
    state: Annotated[str | None, Query()] = None,
):
    code_url_path = router.url_path_for("oauth_code", provider=provider)
    redirect_uri = get_settings().OAUTH_BASE_URL + str(code_url_path)
    if not state:
        state = str(uuid.uuid4())
    if str.lower(provider) == "yandex":
        code_challenge_method = "S256"
        code_challenge = await oauth_service.create_code_challenge(
            state=state, code_challenge_method=code_challenge_method
        )
        oauth_provider_url = f"https://oauth.yandex.ru/authorize?client_id={get_settings().OAUTH_YANDEX_CLIENT_ID}&response_type=code&redirect_uri={redirect_uri}&state={state}&code_challenge={code_challenge}&code_challenge_method={code_challenge_method}"
    if str.lower(provider) == "vk":
        oauth_provider_url = f"https://oauth.vk.com/authorize?client_id={get_settings().OAUTH_VK_CLIENT_ID}&display=page&redirect_uri={redirect_uri}&response_type=code&scope=email&v=5.131"
    return RedirectResponse(oauth_provider_url, status_code=307)


@router.get(
    "/code/{provider}",
    status_code=HTTPStatus.OK,
    description="URL to get authorization code from Authorization provider and login/register user.",
)
async def oauth_code(
    request: Request,
    session: Annotated[AsyncSession, Depends(session_handler.create_session)],
    cache_service: Annotated[RedisStorage, Depends(get_redis_storage)],
    oauth_service: Annotated[OAuthService, Depends(get_oauth_service)],
    provider: Annotated[str, Path()],
    token_check_data: Annotated[
        TokenCheckResponse | None, Security(silent_token_checker)
    ] = None,
    user_agent: Annotated[str, Header()] = "",
    real_ip: Annotated[str, Header(alias="X-Real-IP")] = "",
    code: Annotated[str | None, Query()] = None,
    error: Annotated[str | None, Query()] = None,
    error_description: Annotated[str | None, Query()] = None,
    state: Annotated[str | None, Query()] = None,
) -> UserTokenPair | OAuthProviderDataSchema:
    if provider not in ["vk", "yandex"]:
        raise HTTPException(
            status_code=400, detail="Not supported auth provider"
        )
    if error:
        raise HTTPException(status_code=400, detail=error_description)
    if not code:
        raise HTTPException(
            status_code=400, detail="No authorization code provided"
        )
    if state:
        code_verifier = await cache_service.get_from_cache(key=state)
    else:
        code_verifier = str(request.url).split("?")[0]
    if token_check_data:
        await oauth_service.link(
            session=session,
            provider=provider,
            code=code,
            code_verifier=code_verifier,
            ip=real_ip,
            token_check_data=token_check_data,
        )
    else:
        tokens = await oauth_service.oauth_login(
            session=session,
            provider=provider,
            code=code,
            code_verifier=code_verifier,
            user_agent=user_agent,
            ip=real_ip,
        )
    return tokens
