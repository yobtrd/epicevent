from epicevent.infrastructure.repositories.contract_repository import ContractRepository
from epicevent.security.roles import UserRole
from tests.conftest import (
    create_contract,
    create_persisted_client,
    create_persisted_contract,
    create_persisted_user,
)


# save
################
def test_save_contract_success(session):
    repository = ContractRepository(session)
    sales_representative = create_persisted_user(session, role_id=UserRole.SALES)
    client = create_persisted_client(
        session, sales_representative_id=sales_representative.id
    )

    contract = create_contract(
        client_id=client.id, sales_representative_id=sales_representative.id
    )
    created = repository.save(contract)

    assert created.id is not None
    assert created.created_at is not None
    assert created.total_amount == contract.total_amount
    assert created.client_id == client.id
    assert created.sales_representative_id == sales_representative.id


# find_by_id
################
def test_find_by_id_success(session):
    repository = ContractRepository(session)

    sales_representative = create_persisted_user(session, role_id=UserRole.SALES)
    client = create_persisted_client(
        session,
        sales_representative_id=sales_representative.id,
    )

    contract = create_persisted_contract(
        session,
        client_id=client.id,
        sales_representative_id=sales_representative.id,
    )

    found = repository.find_by_id(contract.id)

    assert found is not None
    assert found.id == contract.id
    assert found.client_id == client.id
    assert found.sales_representative_id == sales_representative.id


def test_find_by_id_not_found(session):
    repository = ContractRepository(session)

    found = repository.find_by_id(999)

    assert found is None
