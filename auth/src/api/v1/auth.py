import re
from http import HTTPStatus
from typing import Annotated

from core.config import get_settings
from core.exceptions import InvalidUserOrPassword
from db.postgres.session_handler import session_handler
from fastapi import APIRouter, Body, Depends, Header, Query
from fastapi.params import Security
from fastapi.security import OAuth2PasswordRequestForm
from schemas.token import TokenCheckResponse, UserTokenPair
from schemas.user import UserBase
from services.auth_service import AuthService, get_auth_service
from sqlalchemy.ext.asyncio import AsyncSession
from util.JWT_helper import strict_token_checker

router = APIRouter()


@router.post(
    "/login",
    response_model=UserTokenPair,
    status_code=HTTPStatus.OK,
    description="Form to login the user in the service and generate the token pair.",
)
async def login(
    session: Annotated[AsyncSession, Depends(session_handler.create_session)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    user_agent: Annotated[str, Header()] = "",
    real_ip: Annotated[str, Header(alias="X-Real-IP")] = "",
) -> UserTokenPair:
    if not re.match(get_settings().LOGIN_PATTERN, form_data.username):
        raise InvalidUserOrPassword
    credentials = UserBase(
        login=form_data.username, password=form_data.password
    )
    tokens = await auth_service.login(
        session=session,
        user=credentials,
        user_agent=user_agent,
        ip=real_ip,
    )
    return tokens


@router.post(
    "/refresh",
    response_model=UserTokenPair,
    status_code=HTTPStatus.OK,
    description="Generate a new token pair.",
)
async def refresh(
    session: Annotated[AsyncSession, Depends(session_handler.create_session)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    refresh_token: Annotated[str, Body()],
) -> UserTokenPair:
    """Generates the new token pair and returns it to the user."""
    tokens = await auth_service.refresh(
        refresh_token=refresh_token, session=session
    )
    return tokens


@router.post(
    "/logout",
    status_code=HTTPStatus.OK,
    description="Logout the user and delete session.",
)
async def logout(
    session: Annotated[AsyncSession, Depends(session_handler.create_session)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    token_check_data: Annotated[
        TokenCheckResponse, Security(strict_token_checker)
    ],
    logout_everywhere: Annotated[bool, Query()] = False,
) -> dict[str, str]:
    """Logout the user from from service."""
    await auth_service.logout(
        access_token=token_check_data.token,
        session=session,
        logout_everywhere=logout_everywhere,
    )
    return {"status": "User has been successfully logouted."}
