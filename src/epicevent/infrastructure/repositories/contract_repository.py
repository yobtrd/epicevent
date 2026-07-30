from sqlalchemy.orm import Session


class ContractRepository:
    def __init__(self, session: Session):
        self.session = session

    def save(self, contract):
        self.session.add(contract)
        self.session.flush()
        return contract
