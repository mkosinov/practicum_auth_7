import base64
import hashlib
import random
import secrets
import uuid
from typing import Annotated

from core.config import get_settings
from db.postgres.session_handler import session_handler
from db.redis.redis_storage import RedisStorage, get_redis_storage
from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request
from fastapi.responses import JSONResponse, RedirectResponse
from services.auth_service import AuthService, get_auth_service
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


# @router.post(
#     "/register",
#     response_model=UserSelfResponse,
#     status_code=HTTPStatus.CREATED,
#     description="Register a new user via OAuth2.0.",
# )
# async def create_oauth_user(
#     user_service: Annotated[UserService, Depends(get_user_service)],
#     session: Annotated[AsyncSession, Depends(session_handler.create_session)],
#     user: UserSelf,
# ) -> UserSelfResponse:
#     """Register a user in the authentication service with data from oauth2.0 provider."""
#     new_user = await user_service.create_user(session=session, user=user)
#     return new_user


@router.get("/yandex")
async def oauth_yandex_page(
    cache_service: Annotated[RedisStorage, Depends(get_redis_storage)],
):
    yandex_redirect_uri = "http://localhost:8000/api/v1/oauth/yandex/code"
    # Строка состояния, которую Яндекс OAuth возвращает без изменения. Максимальная допустимая длина строки — 1024 символа. Можно использовать, например, для защиты от CSRF-атак или идентификации пользователя, для которого запрашивается токен.
    # добавить сохранение state в redis ???
    # code_verifier = "".join(
    #     [
    #         random.choice(ascii_letters + digits + "-._~")
    #         for _ in range(random.randint(43, 128))
    #     ]
    # )

    code_verifier = secrets.token_urlsafe(random.randint(43, 128))
    hash = hashlib.sha256(code_verifier.encode("ascii")).digest()
    encoded = base64.urlsafe_b64encode(hash)
    code_challenge = encoded.decode("ascii")[:-1]
    code_challenge_method = "S256"
    state = str(uuid.uuid4())
    await cache_service.put_to_cache(
        key=state, value=code_verifier, lifetime=600
    )
    device_id = ""
    device_name = ""
    oauth_yandex_url = f"https://oauth.yandex.ru/authorize?response_type=code&client_id={get_settings().OAUTH_YANDEX_CLIENT_ID}&redirect_uri={yandex_redirect_uri}&state={state}&code_challenge={code_challenge}&code_challenge_method={code_challenge_method}"
    return RedirectResponse(oauth_yandex_url, status_code=307)


@router.get("/yandex/code")
async def oauth_yandex_code(
    session: Annotated[AsyncSession, Depends(session_handler.create_session)],
    cache_service: Annotated[RedisStorage, Depends(get_redis_storage)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    user_agent: Annotated[str, Header()] = "",
    real_ip: Annotated[str, Header(alias="X-Real-IP")] = "",
    code: Annotated[str | None, Query()] = None,
    error: Annotated[str | None, Query()] = None,
    error_description: Annotated[str | None, Query()] = None,
    state: Annotated[str | None, Query()] = None,
):
    if error:
        raise HTTPException(status_code=400, detail=error_description)
    if not code:
        raise HTTPException(
            status_code=400, detail="No authorization code provided"
        )
    if state:
        code_verifier = await cache_service.get_from_cache(key=state)
    else:
        code_verifier = ""
    user_info = await auth_service.oauth_login(
        session=session,
        code=code,
        code_verifier=code_verifier,
        user_agent=user_agent,
        ip=real_ip,
    )
    return JSONResponse({"status": "ok", "response": user_info})


"""{
"status": "ok",
"response": {
"id": "20639427",
"login": "mkosinov",
"client_id": "1e37a457766f40e1b6ba70ff072a7819",
"display_name": "mkosinov",
"real_name": "Максим Косинов",
"first_name": "Максим",
"last_name": "Косинов",
"sex": "male",
"default_email": "mkosinov@yandex.ru",
"emails": [
"mkosinov@yandex.ru"
],
"birthday": "1984-03-18",
"default_avatar_id": "21377/enc-41ef8dab0ce2bbd16b60669e405f83ae",
"is_avatar_empty": false,
"default_phone": {
"id": 183155583,
"number": "+79996531803"
},
"psuid": "1.AAu7yA.OaSLPGHvWuuOuCvzCByvHA.0AEVp5QwRgn_TIaRHEJbdA"
}
}    """


@router.get("/vk")
async def oauth_vk_request():
    redirect_state = "sidhgw"
    appId = "51918377"
    redirect_vk_url = "http://localhost/api/v1/oauth/vk/token"
    oauth_vk_url = f"https://id.vk.com/auth?uuid={str(uuid.uuid4())}&appId={appId}&response_type=silent_token&redirect_uri={redirect_vk_url}"
    # oauth_vk_url = f"https://id.vk.com/auth?uuid={str(uuid.uuid4())}&appId={appId}&response_type=silent_token&redirect_uri={redirect_vk_url}&redirect_state={redirect_state}"
    return RedirectResponse(oauth_vk_url, status_code=307)


"https://id.vk.com/auth?uuid=2bca55c9-ef38-451f-bf0c-94ea999ed97f&appId=51918377&response_type=silent_token&redirect_uri=http://localhost/api/v1/oauth/vk/token&redirect_state=sidhgw"


@router.get("/vk/token")
async def oauth_vk_token(request: Request):
    print("headers:")
    print(request.headers)
    print("body:")
    print(await request.body())
    return JSONResponse({"status": "ok", "response": await request.json()})
