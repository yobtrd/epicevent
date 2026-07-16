from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from epicevent.database import Base

if TYPE_CHECKING:
    from .contract import Contract
    from .user import User


class Event(Base):
    __tablename__ = "event"

    id: Mapped[int] = mapped_column(
        primary_key=True,
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
        String(100),
        nullable=False,
    )
    attendees: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    contract_id: Mapped[int] = mapped_column(
        ForeignKey("contract.id", ondelete="CASCADE"),
        nullable=False,
    )
    support_representative_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="RESTRICT"),
        nullable=False,
    )

    contract: Mapped["Contract"] = relationship(back_populates="events")
    support_representative: Mapped["User"] = relationship(
        back_populates="supported_events"
    )
