from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from epicevents.infrastructure.base import Base
from epicevents.security.encryption import EncryptedString

if TYPE_CHECKING:
    from .contract import Contract
    from .user import User


class Event(Base):
    __tablename__ = "event"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )
    name: Mapped[str] = mapped_column(
        EncryptedString(),
        nullable=False,
    )
    start: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )
    end: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )
    location: Mapped[str] = mapped_column(
        EncryptedString(),
        nullable=False,
    )
    attendees: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    notes: Mapped[str | None] = mapped_column(
        EncryptedString(),
        nullable=True,
    )
    contract_id: Mapped[int] = mapped_column(
        ForeignKey("contract.id", ondelete="CASCADE"),
        nullable=False,
    )
    support_representative_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="RESTRICT"),
        nullable=True,
    )

    contract: Mapped["Contract"] = relationship(back_populates="events")
    support_representative: Mapped["User | None"] = relationship(
        back_populates="supported_events"
    )
