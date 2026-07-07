from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.epicevent.database import Base

if TYPE_CHECKING:
    from .contract import Contract
    from .user import User


class Client(Base):
    __tablename__ = "client"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )
    last_name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    first_name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    email: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )
    phone: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )
    business_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    first_contact: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )
    last_contact: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )
    sales_representative_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="RESTRICT"),
        nullable=False,
    )

    sales_representative: Mapped["User"] = relationship(back_populates="clients")
    contracts: Mapped[list["Contract"]] = relationship(back_populates="client")
