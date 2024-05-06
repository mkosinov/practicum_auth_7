from uuid import UUID
from pydantic import Field
from core.config import get_settings

from pydantic import BaseModel, ConfigDict, EmailStr

from schemas.mixins import CreatedMixinSchema


class UserSelf(BaseModel):
    login: str = Field(min_length=get_settings().LOGIN_MIN_LENGTH,
                       max_length=get_settings().LOGIN_MAX_LENGTH)
    email: EmailStr = Field(min_length=get_settings().EMAIL_MIN_LENGTH,
                            max_length=get_settings().EMAIL_MAX_LENGTH)
    first_name: str = Field(min_length=get_settings().FIRST_NAME_MIN_LENGTH,
                            max_length=get_settings().FIRST_NAME_MAX_LENGTH)
    last_name: str = Field(min_length=get_settings().LAST_NAME_MIN_LENGTH,
                           max_length=get_settings().LAST_NAME_MAX_LENGTH)
    password: str = Field(min_length=get_settings().PASSWORD_MIN_LENGTH,
                          max_length=get_settings().PASSWORD_MAX_LENGTH)


class UserInDB(CreatedMixinSchema):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    login: str
    email: EmailStr
    first_name: str
    last_name: str
    is_active: bool
    hashed_password: str


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


class UserLoginSchema(BaseModel):
    login: str