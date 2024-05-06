import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from db.postgres.session_handler import session_handler


class UserHistoryModel(session_handler.base):
    __tablename__ = "user_history"

    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True
    )
    user_id = Column(
        UUID, ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    device_id = Column(
        UUID, ForeignKey("device.id", ondelete="SET NULL"), nullable=False
    )
    action = Column(String(50), default="login", nullable=False)
    ip = Column(String(39), default="", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="history", uselist=False)
    device = relationship("DeviceModel", uselist=False)
