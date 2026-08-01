from sqlalchemy import func, select
from sqlalchemy.orm import Session

from epicevent.models.event import Event
from epicevent.security.roles import UserRole


class EventRepository:
    def __init__(self, session: Session):
        self.session = session

    def save(self, event: Event) -> Event:
        self.session.add(event)
        self.session.flush()
        return event

    def _build_query(
        self,
        user_id: int,
        user_role: int,
        is_assigned: bool | None = None,
    ):
        query = select(Event)

        if user_role != UserRole.MANAGEMENT:
            query = query.where(Event.support_representative_id == user_id)

        if is_assigned is not None:
            if is_assigned:
                query = query.where(Event.support_representative_id.is_not(None))
            else:
                query = query.where(Event.support_representative_id.is_(None))

        return query

    def list(
        self,
        user_id: int,
        user_role: int,
        is_assigned: bool | None = None,
        limit=10,
        offset=0,
    ):
        query = self._build_query(
            user_id=user_id,
            user_role=user_role,
            is_assigned=is_assigned,
        )
        query = query.limit(limit).offset(offset)
        return self.session.execute(query).scalars().all()

    def count(
        self,
        user_id: int,
        user_role: int,
        is_assigned: bool | None = None,
    ) -> int:
        query = self._build_query(
            user_id=user_id,
            user_role=user_role,
            is_assigned=is_assigned,
        )

        count_query = select(func.count()).select_from(query.subquery())
        return self.session.execute(count_query).scalar_one()
