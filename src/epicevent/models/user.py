from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from epicevent.database import Base

if TYPE_CHECKING:
    from .client import Client
    from .contract import Contract
    from .event import Event


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )
    employee_number: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False,
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
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    role_id: Mapped[int] = mapped_column(
        ForeignKey("role.id"),
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        default=True,
        nullable=False,
    )

    role: Mapped["Role"] = relationship(back_populates="users")
    clients: Mapped[list["Client"]] = relationship(
        back_populates="sales_representative"
    )
    contracts: Mapped[list["Contract"]] = relationship(
        back_populates="sales_representative"
    )
    supported_events: Mapped[list["Event"]] = relationship(
        back_populates="support_representative"
    )


class Role(Base):
    __tablename__ = "role"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )
    name: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False,
    )

    users: Mapped[list["User"]] = relationship(back_populates="role")
