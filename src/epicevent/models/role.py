from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from epicevent.infrastructure.base import Base

if TYPE_CHECKING:
    from .user import User


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
