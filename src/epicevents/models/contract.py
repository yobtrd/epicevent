from datetime import UTC, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from epicevents.infrastructure.base import Base

if TYPE_CHECKING:
    from .client import Client
    from .event import Event
    from .user import User


class Contract(Base):
    __tablename__ = "contract"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )
    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )
    remaining_amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.now(UTC),
    )
    is_signed: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
    )
    client_id: Mapped[int] = mapped_column(
        ForeignKey("client.id", ondelete="CASCADE"),
        nullable=False,
    )
    sales_representative_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="RESTRICT"), nullable=False
    )

    client: Mapped["Client"] = relationship(back_populates="contracts")
    sales_representative: Mapped["User"] = relationship(back_populates="contracts")
    events: Mapped[list["Event"]] = relationship(back_populates="contract")
