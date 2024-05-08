from uuid import UUID

from core.config import get_settings
from pydantic import BaseModel, ConfigDict, EmailStr, Field, computed_field
from schemas.mixins import CreatedMixinSchema
from schemas.oauth import OAuthUserSchema


class UserSelf(BaseModel):
    login: str = Field(
        min_length=get_settings().LOGIN_MIN_LENGTH,
        max_length=get_settings().LOGIN_MAX_LENGTH,
    )
    email: EmailStr = Field(
        min_length=get_settings().EMAIL_MIN_LENGTH,
        max_length=get_settings().EMAIL_MAX_LENGTH,
    )
    first_name: str = Field(
        min_length=get_settings().FIRST_NAME_MIN_LENGTH,
        max_length=get_settings().FIRST_NAME_MAX_LENGTH,
    )
    last_name: str = Field(
        min_length=get_settings().LAST_NAME_MIN_LENGTH,
        max_length=get_settings().LAST_NAME_MAX_LENGTH,
    )
    password: str = Field(
        min_length=get_settings().PASSWORD_MIN_LENGTH,
        max_length=get_settings().PASSWORD_MAX_LENGTH,
    )


class UserInDB(CreatedMixinSchema):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    login: str
    email: EmailStr
    first_name: str
    last_name: str
    is_active: bool
    hashed_password: str
    oauth_accounts: list[OAuthUserSchema] = []

    @computed_field
    @property
    def oauth_accounts_compact(self) -> list[str]:
        return [account.provider for account in self.oauth_accounts]


class UserInDBAccess(UserInDB):
    model_config = ConfigDict(from_attributes=True)
    access: list = []


class UserSaveToDB(BaseModel):
    login: str
    email: EmailStr
    first_name: str
    last_name: str
    hashed_password: str


class UserBase(BaseModel):
    login: str
    password: str


class UserLogin(BaseModel):
    login: str
    acess_token: str


class UserSelfResponse(BaseModel):
    login: str
    email: EmailStr
    first_name: str
    last_name: str
    oauth_accounts_compact: list[str] = []


class UserLoginSchema(BaseModel):
    login: str
