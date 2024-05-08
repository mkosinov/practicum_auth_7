import uuid
from datetime import datetime

from core.config import get_settings
from db.postgres.session_handler import session_handler
from sqlalchemy import Boolean, Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy_utils import EmailType


class User(session_handler.base):
    __tablename__ = "user"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    login = Column(
        String(get_settings().LOGIN_MAX_LENGTH), unique=True, nullable=False
    )
    email = Column(EmailType, unique=True, nullable=False)
    hashed_password = Column(
        String(get_settings().HASHED_PASSWORD_MAX_LENGTH), nullable=False
    )
    first_name = Column(String(get_settings().FIRST_NAME_MAX_LENGTH))
    last_name = Column(String(get_settings().LAST_NAME_MAX_LENGTH))
    created_at = Column(DateTime, default=datetime.now(), nullable=False)
    modified_at = Column(DateTime, default=datetime.now(), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    access = relationship(
        "UserRoleModel",
        back_populates="user",
        uselist=True,
    )
    devices = relationship("DeviceModel", back_populates="user", uselist=True)
    history = relationship(
        "UserHistoryModel", back_populates="user", uselist=True
    )
    oauth_accounts = relationship(
        "OAuthUserModel", back_populates="user", uselist=True
    )

    def __repr__(self) -> str:
        return f"<User {self.login}>"
