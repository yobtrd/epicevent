from sqlalchemy.orm import Session

from epicevent.models.contract import Contract


class ContractRepository:
    def __init__(self, session: Session):
        self.session = session

    def save(self, contract):
        self.session.add(contract)
        self.session.flush()
        return contract

    def find_by_id(self, contract_id: int) -> Contract | None:
        return self.session.query(Contract).filter_by(id=contract_id).first()
