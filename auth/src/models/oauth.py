import datetime
import uuid

from db.postgres.session_handler import session_handler
from sqlalchemy import Column, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class OAuthModel(session_handler.base):
    __tablename__ = "oauth"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    user_id = Column(
        UUID, ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    oauth_provider = Column(Text, unique=False, nullable=False)
    oauth_user_id = Column(Text, unique=False, nullable=False)
    created_at = Column(
        DateTime, default=datetime.datetime.now(datetime.UTC), nullable=False
    )
    user = relationship("User", back_populates="oauth", uselist=False)
