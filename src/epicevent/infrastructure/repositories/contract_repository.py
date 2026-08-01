from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from epicevent.models.contract import Contract
from epicevent.security.roles import UserRole


class ContractRepository:
    def __init__(self, session: Session):
        self.session = session

    def save(self, contract):
        self.session.add(contract)
        self.session.flush()
        return contract

    def find_by_id(self, contract_id: int) -> Contract | None:
        return self.session.query(Contract).filter_by(id=contract_id).first()

    def _apply_filters(
        self,
        query,
        user_id: int,
        user_role: int,
        is_signed: bool | None = None,
        is_paid: bool | None = None,
    ):
        if user_role != UserRole.MANAGEMENT:
            query = query.where(Contract.sales_representative_id == user_id)

        if is_signed is not None:
            query = query.where(Contract.is_signed == is_signed)

        if is_paid is True:
            query = query.where(Contract.remaining_amount == 0)

        elif is_paid is False:
            query = query.where(Contract.remaining_amount > 0)

        return query

    def list(
        self,
        user_id: int,
        user_role: int,
        is_signed: bool | None = None,
        is_paid: bool | None = None,
        limit: int = 10,
        offset: int = 0,
    ):
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
        )

        query = query.limit(limit).offset(offset)

        return self.session.execute(query).scalars().all()

    def count(
        self,
        user_id: int,
        user_role: int,
        is_signed: bool | None = None,
        is_paid: bool | None = None,
    ) -> int:
        query = select(Contract)

        query = self._apply_filters(
            query,
            user_id=user_id,
            user_role=user_role,
            is_signed=is_signed,
            is_paid=is_paid,
        )

        count_query = select(func.count()).select_from(query.subquery())

        return self.session.execute(count_query).scalar_one()
