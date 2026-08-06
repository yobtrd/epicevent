from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session, joinedload

from epicevent.models.contract import Contract
from epicevent.models.event import Event
from epicevent.security.roles import UserRole


class EventRepository:
    """Handle data access operations for events."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, event: Event) -> Event:
        self.session.add(event)
        self.session.flush()
        return event

    def find_by_id(self, event_id: int) -> Event | None:
        return self.session.get(Event, event_id)

    def _apply_filters(
        self,
        query: Select,
        user_id: int,
        user_role: int,
        upcoming: bool = False,
        is_assigned: bool | None = None,
        support_assigned: bool = False,
    ) -> Select:
        """Apply active status filters to the query."""
        if upcoming:
            query = query.where(Event.end > func.now())

        if is_assigned is True:
            query = query.where(Event.support_representative_id.is_not(None))
        elif is_assigned is False:
            query = query.where(Event.support_representative_id.is_(None))

        if support_assigned:
            if user_role == UserRole.SUPPORT:
                query = query.where(Event.support_representative_id == user_id)
            else:
                query = query.where(False)

        return query

    def list(
        self,
        user_id: int,
        user_role: int,
        upcoming: bool = False,
        is_assigned: bool | None = None,
        support_assigned: bool = False,
        limit: int = 10,
        offset: int = 0,
    ) -> list[Event]:
        """
        Retrieve a paginated list of events matching the active filter.

        Eagerly loads the contract (including client and sales representative)
        and the support representative to optimize performance.
        """
        query = select(Event).options(
            joinedload(Event.contract).joinedload(Contract.client),
            joinedload(Event.contract).joinedload(Contract.sales_representative),
            joinedload(Event.support_representative),
        )

        query = self._apply_filters(
            query,
            user_id=user_id,
            user_role=user_role,
            upcoming=upcoming,
            is_assigned=is_assigned,
            support_assigned=support_assigned,
        )

        query = query.limit(limit).offset(offset)

        return self.session.execute(query).scalars().all()

    def count(
        self,
        user_id: int,
        user_role: int,
        upcoming: bool = False,
        is_assigned: bool | None = None,
        support_assigned: bool = False,
    ) -> int:
        query = select(Event)

        query = self._apply_filters(
            query,
            user_id=user_id,
            user_role=user_role,
            upcoming=upcoming,
            is_assigned=is_assigned,
            support_assigned=support_assigned,
        )

        count_query = select(func.count()).select_from(query.subquery())
        return self.session.execute(count_query).scalar_one()
