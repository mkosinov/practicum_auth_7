import base64
import hashlib
import random
import secrets
import string
from functools import lru_cache
from typing import Annotated
from uuid import UUID

import httpx
from core.config import get_settings
from core.exceptions import (
    CommonExistsException,
    OauthAccountNotExistsException,
)
from db.postgres.postgres import PostgresStorage, get_postgers_storage
from db.redis.redis_storage import get_redis_storage
from fastapi import Depends, HTTPException
from models.device import DeviceModel
from models.oauth import OAuthUserModel
from models.role import Role
from models.token import RefreshToken
from models.user import User
from models.user_history import UserHistoryModel
from models.user_role import UserRoleModel
from redis.asyncio import Redis
from schemas.oauth import OAuthProviderDataSchema
from schemas.token import TokenCheckResponse
from schemas.user import UserBase, UserSelf
from schemas.user_history import UserHistoryCreateSchema
from services.auth_service import AuthService, get_auth_service
from services.user_service import UserService, get_user_service
from sqlalchemy import and_, delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload


class OAuthService:
    def __init__(
        self,
        cache,
        database: PostgresStorage,
        user_service: UserService,
        auth_service: AuthService,
    ):
        self.cache = cache
        self.database = database
        self.user_service = user_service
        self.auth_service = auth_service
        self.refresh_token_table = RefreshToken
        self.access_table = UserRoleModel
        self.role_table = Role
        self.user_table = User
        self.device_table = DeviceModel
        self.user_history_table = UserHistoryModel
        self.oauth_table = OAuthUserModel

    async def unlink(
        self, session: AsyncSession, provider: str, user_login: str
    ):
        """Delete oauth account."""
        stmt = (
            delete(self.oauth_table)
            .where(
                and_(
                    self.oauth_table.provider == provider,
                    self.oauth_table.user_id
                    == select(self.user_table.id)
                    .where(self.user_table.login == user_login)
                    .scalar_subquery(),
                )
            )
            .returning(self.oauth_table)
        )
        result = await session.execute(stmt)
        oauth_account = result.scalar_one_or_none()
        if not oauth_account:
            raise OauthAccountNotExistsException()
        await session.commit()
        return oauth_account

    async def link(
        self,
        session: AsyncSession,
        provider: str,
        code: str,
        code_verifier: str,
        ip: str,
        token_check_data: TokenCheckResponse,
    ) -> OAuthProviderDataSchema:
        """Create oauth account linked to access token user."""
        oauth_provider_data = await self.get_provider_data(
            provider=provider, code=code, code_verifier=code_verifier
        )
        stmt = (
            select(self.oauth_table, self.user_table)
            .where(
                and_(
                    self.oauth_table.provider_user_id
                    == oauth_provider_data.user_id,
                    self.oauth_table.provider == oauth_provider_data.provider,
                )
            )
            .join(self.oauth_table.user)
            .options(joinedload(self.oauth_table.user))
        )
        oauth_user = await session.scalar(stmt)
        if oauth_user:
            raise CommonExistsException(info=oauth_user)
        stmt = select(self.user_table).where(
            self.user_table.login == token_check_data.sub
        )
        result = await session.execute(stmt)
        user = result.scalar_one()
        oauth_user = OAuthUserModel(
            user_id=user.id,
            provider=oauth_provider_data.provider,
            provider_user_id=oauth_provider_data.user_id,
        )
        session.add(oauth_user)
        await session.commit()
        user_history_obj = UserHistoryCreateSchema(
            user_id=UUID(str(user.id)),
            device_id=token_check_data.device_id,
            action="link {provider} account",
            ip=ip,
        )
        await self.auth_service.write_user_history(
            session=session, user_history_obj=user_history_obj
        )
        return oauth_provider_data

    async def oauth_login(
        self,
        session: AsyncSession,
        provider: str,
        code: str,
        code_verifier: str,
        user_agent: str,
        ip: str,
    ):
        """Login using oauth provider email"""
        oauth_provider_data = await self.get_provider_data(
            provider=provider, code=code, code_verifier=code_verifier
        )
        user = await self.get_or_create_oauth_user(
            session=session,
            oauth_provider_data=oauth_provider_data,
        )
        user_login = UserBase(login=str(user.login), password="")
        tokens = await self.auth_service.login(
            session=session,
            user=user_login,
            user_agent=user_agent,
            ip=ip,
            oauth_provider=provider,
        )
        return tokens

    async def get_or_create_oauth_user(
        self, session, oauth_provider_data: OAuthProviderDataSchema
    ):
        """Create oauth account and user account if not exists"""
        stmt = (
            select(self.oauth_table, self.user_table)
            .where(
                and_(
                    self.oauth_table.provider_user_id
                    == oauth_provider_data.user_id,
                    self.oauth_table.provider == oauth_provider_data.provider,
                )
            )
            .join(self.oauth_table.user)
            .options(joinedload(self.oauth_table.user))
        )
        oauth_user = await session.scalar(stmt)
        if oauth_user:
            return oauth_user.user
        stmt = select(self.user_table).where(
            self.user_table.email == oauth_provider_data.email
        )
        user = await session.scalar(stmt)
        if not user:
            new_user = UserSelf(
                login=oauth_provider_data.email,
                email=oauth_provider_data.email,
                first_name=oauth_provider_data.first_name,
                last_name=oauth_provider_data.last_name,
                password="".join(
                    [
                        secrets.choice(string.ascii_letters + string.digits)
                        for _ in range(20)
                    ]
                ),
            )
            user = await self.user_service.create_user(
                session=session, user=new_user
            )
        oauth_user = OAuthUserModel(
            user_id=user.id,
            provider=oauth_provider_data.provider,
            provider_user_id=oauth_provider_data.user_id,
        )
        session.add(oauth_user)
        await session.commit()
        return oauth_user.user

    async def get_provider_data(
        self, provider, code, code_verifier
    ) -> OAuthProviderDataSchema:
        """Request user info from oauth provider"""
        if provider == "yandex":
            tokens = await self._make_yandex_token_request(
                code=code, code_verifier=code_verifier
            )
            user_info = await self._get_yandex_user_info(
                access_token=tokens["access_token"]
            )
            return OAuthProviderDataSchema(
                provider=provider,
                email=user_info["default_email"],
                user_id=int(user_info["id"]),
                first_name=user_info["first_name"],
                last_name=user_info["last_name"],
            )
        if provider == "vk":
            token_data = await self._make_vk_token_request(
                code=code, oauth_code_url=code_verifier
            )
            user_info = await self._get_vk_user_info(
                access_token=token_data["access_token"]
            )
            return OAuthProviderDataSchema(
                provider=provider,
                email=token_data["email"],
                user_id=token_data["user_id"],
                first_name=user_info["response"]["first_name"],
                last_name=user_info["response"]["last_name"],
            )

    async def _make_vk_token_request(self, code: str, oauth_code_url: str):
        url = f"https://oauth.vk.com/access_token?client_id={get_settings().OAUTH_VK_CLIENT_ID}&client_secret={get_settings().OAUTH_VK_CLIENT_SECRET}&redirect_uri={oauth_code_url}&code={code}"
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url=url,
            )
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code, detail=response.json()
            )
        return response.json()

    async def _make_yandex_token_request(self, code: str, code_verifier: str):
        headers = {
            "Content-type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {get_settings().OAUTH_YANDEX_BASIC_BASE64.decode()}",
        }
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "code_verifier": code_verifier,
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url="https://oauth.yandex.ru/token",
                headers=headers,
                data=data,
            )
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code, detail=response.json()
            )
        return response.json()

    async def _get_vk_user_info(self, access_token):
        headers = {"Authorization": f"Bearer {access_token}"}
        url = "https://api.vk.com/method/account.getProfileInfo?v=5.199"
        async with httpx.AsyncClient() as client:
            response = await client.post(url=url, headers=headers)
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code, detail=response.json()
            )
        return response.json()

    async def _get_yandex_user_info(self, access_token):
        headers = {"Authorization": f"OAuth {access_token}"}
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url="https://login.yandex.ru/info?", headers=headers
            )
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code, detail=response.json()
            )
        return response.json()

    async def create_code_challenge(
        self, state: str, code_challenge_method: str
    ):
        code_verifier = secrets.token_urlsafe(random.randint(43, 128))
        if code_challenge_method == "S256":
            hash = hashlib.sha256(code_verifier.encode("ascii")).digest()
            encoded = base64.urlsafe_b64encode(hash)
            code_challenge = encoded.decode("ascii")[:-1]
        else:
            code_challenge = code_verifier
        await self.cache.put_to_cache(
            key=state, value=code_verifier, lifetime=600
        )
        return code_challenge


@lru_cache()
def get_oauth_service(
    redis: Annotated[Redis, Depends(get_redis_storage)],
    postgres: Annotated[PostgresStorage, Depends(get_postgers_storage)],
    user_service: Annotated[UserService, Depends(get_user_service)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> OAuthService:
    return OAuthService(
        cache=redis,
        database=postgres,
        user_service=user_service,
        auth_service=auth_service,
    )
