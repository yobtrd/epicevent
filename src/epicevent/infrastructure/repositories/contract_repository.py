from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session, joinedload

from epicevent.models.contract import Contract
from epicevent.security.roles import UserRole


class ContractRepository:
    """Handle data access operations for contracts."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, contract: Contract) -> Contract:
        self.session.add(contract)
        self.session.flush()
        return contract

    def find_by_id(self, contract_id: int) -> Contract | None:
        return self.session.get(Contract, contract_id)

    def _apply_filters(
        self,
        query: Select,
        user_id: int,
        user_role: int,
        is_signed: bool | None = None,
        is_paid: bool | None = None,
        sales_assigned: bool = False,
    ) -> Select:
        """Apply active status filters to the query."""
        if is_signed is not None:
            query = query.where(Contract.is_signed == is_signed)

        if is_paid is True:
            query = query.where(Contract.remaining_amount == 0)

        elif is_paid is False:
            query = query.where(Contract.remaining_amount > 0)

        if sales_assigned:
            if user_role == UserRole.SALES:
                query = query.where(Contract.sales_representative_id == user_id)
            else:
                query = query.where(False)

        return query

    def list(
        self,
        user_id: int,
        user_role: int,
        is_signed: bool | None = None,
        is_paid: bool | None = None,
        sales_assigned: bool = False,
        limit: int = 10,
        offset: int = 0,
    ) -> list[Contract]:
        """
        Retrieve a paginated list of contracts matching the active filter.

        Eagerly loads the client and sales representative to optimize performance.
        """
        query = select(Contract).options(
            joinedload(Contract.client),
            joinedload(Contract.sales_representative),
        )

        query = self._apply_filters(
            query,
            user_id=user_id,
            user_role=user_role,
            is_signed=is_signed,
            is_paid=is_paid,
            sales_assigned=sales_assigned,
        )

        query = query.limit(limit).offset(offset)

        return self.session.execute(query).scalars().all()

    def count(
        self,
        user_id: int,
        user_role: int,
        is_signed: bool | None = None,
        is_paid: bool | None = None,
        sales_assigned: bool = False,
    ) -> int:
        """Return the total count of contracts matching the active filter."""
        query = select(Contract)

        query = self._apply_filters(
            query,
            user_id=user_id,
            user_role=user_role,
            is_signed=is_signed,
            is_paid=is_paid,
            sales_assigned=sales_assigned,
        )

        count_query = select(func.count()).select_from(query.subquery())
        return self.session.execute(count_query).scalar_one()
