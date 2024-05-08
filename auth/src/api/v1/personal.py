from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Security, Header
from sqlalchemy.ext.asyncio import AsyncSession

from db.postgres.session_handler import session_handler
from schemas.pagination import PaginationData
from schemas.token import TokenCheckResponse
from schemas.user import UserLoginSchema, UserSelf, UserSelfResponse
from schemas.user_history import UserHistoryResponseSchema
from services.user_service import UserService, get_user_service
from util.JWT_helper import token_check

router = APIRouter()


@router.post(
    "/register",
    response_model=UserSelfResponse,
    status_code=HTTPStatus.CREATED,
    description="Register a new user.",
)
async def create_user(
    user_service: Annotated[UserService, Depends(get_user_service)],
    session: Annotated[AsyncSession, Depends(session_handler.create_session)],
    user: UserSelf,
    request_id: Annotated[str, Header(alias="X-Request-Id")] = "",
) -> UserSelfResponse:
    """Register a user in the authentication service."""
    new_user = await user_service.create_user(session=session, user=user)
    return new_user


@router.get(
    "/personal",
    response_model=UserSelfResponse,
    status_code=HTTPStatus.OK,
    description="Get personal user information.",
)
async def get_current_user_data(
    user_service: Annotated[UserService, Depends(get_user_service)],
    session: Annotated[AsyncSession, Depends(session_handler.create_session)],
    token_check_data: Annotated[TokenCheckResponse, Security(token_check)],
    request_id: Annotated[str, Header(alias="X-Request-Id")] = "",
) -> UserSelfResponse:
    """Get data about current user."""
    user_login = UserLoginSchema(login=token_check_data.sub)
    user = await user_service.get_user(session=session, user_login=user_login)
    return UserSelfResponse(**user.model_dump())


@router.patch(
    "/personal",
    response_model=UserSelfResponse,
    description="Change personal user information.",
)
async def update_user_data(
    user_service: Annotated[UserService, Depends(get_user_service)],
    session: Annotated[AsyncSession, Depends(session_handler.create_session)],
    token_check_data: Annotated[TokenCheckResponse, Security(token_check)],
    update_user_data: UserSelf,
    request_id: Annotated[str, Header(alias="X-Request-Id")] = "",
) -> UserSelfResponse:
    """Change personal user information."""
    user_login = UserLoginSchema(login=token_check_data.sub)
    updated_user = await user_service.update_user(
        session=session, user=user_login, update_user_data=update_user_data
    )
    return UserSelfResponse(**updated_user.model_dump())


@router.delete("/personal", description="Delete personal data.")
async def delete_user_data(
    user_service: Annotated[UserService, Depends(get_user_service)],
    session: Annotated[AsyncSession, Depends(session_handler.create_session)],
    token_check_data: Annotated[TokenCheckResponse, Security(token_check)],
    request_id: Annotated[str, Header(alias="X-Request-Id")] = "",
) -> dict[str, str]:
    """Delete personal information."""
    user_login = UserLoginSchema(login=token_check_data.sub)
    await user_service.delete_user(session=session, user=user_login)
    return {"status": "User has been successfully deleted."}


@router.get(
    "/personal/history",
    response_model=list[UserHistoryResponseSchema],
    description="Get history data.",
)
async def get_current_user_history(
    user_service: Annotated[UserService, Depends(get_user_service)],
    session: Annotated[AsyncSession, Depends(session_handler.create_session)],
    token_check_data: Annotated[TokenCheckResponse, Security(token_check)],
    page: Annotated[int, Query(description="Page number", ge=1)] = 1,
    size: Annotated[int, Query(description="Page size", ge=1)] = 1,
    request_id: Annotated[str, Header(alias="X-Request-Id")] = "",
) -> list[UserHistoryResponseSchema]:
    """Get data about user browsing history."""
    user_login = UserLoginSchema(login=token_check_data.sub)
    user_history = await user_service.get_user_history(
        session=session,
        user_login=user_login,
        pagination=PaginationData(page=page - 1, size=size),
    )
    return user_history
