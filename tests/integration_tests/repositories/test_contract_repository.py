from decimal import Decimal

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
    sales_rep = create_persisted_user(session, role_id=UserRole.SALES)
    client = create_persisted_client(session, sales_representative_id=sales_rep.id)

    contract = create_contract(
        client_id=client.id, sales_representative_id=sales_rep.id
    )
    created = repository.save(contract)

    assert created.id is not None
    assert created.created_at is not None
    assert created.total_amount == contract.total_amount
    assert created.client_id == client.id
    assert created.sales_representative_id == sales_rep.id


# find_by_id
################
def test_find_by_id_success(session):
    repository = ContractRepository(session)

    sales_rep = create_persisted_user(session, role_id=UserRole.SALES)
    client = create_persisted_client(
        session,
        sales_representative_id=sales_rep.id,
    )

    contract = create_persisted_contract(
        session,
        client_id=client.id,
        sales_representative_id=sales_rep.id,
    )

    found = repository.find_by_id(contract.id)

    assert found is not None
    assert found.id == contract.id
    assert found.client_id == client.id
    assert found.sales_representative_id == sales_rep.id


def test_find_by_id_not_found(session):
    repository = ContractRepository(session)

    found = repository.find_by_id(999)

    assert found is None


# list
############################
def test_list_contract_returns_contract_list(session):
    repository = ContractRepository(session)

    sales_rep = create_persisted_user(session, role_id=UserRole.SALES)
    client = create_persisted_client(
        session,
        sales_representative_id=sales_rep.id,
    )

    for _ in range(3):
        create_persisted_contract(
            session,
            client_id=client.id,
            sales_representative_id=sales_rep.id,
        )

    contracts = repository.list(
        user_id=sales_rep.id,
        user_role=UserRole.MANAGEMENT,
    )

    assert len(contracts) == 3


def test_list_contract_pagination(session):
    repository = ContractRepository(session)

    sales_rep = create_persisted_user(session, role_id=UserRole.SALES)
    client = create_persisted_client(
        session,
        sales_representative_id=sales_rep.id,
    )

    for _ in range(15):
        create_persisted_contract(
            session,
            client_id=client.id,
            sales_representative_id=sales_rep.id,
        )

    page1 = repository.list(
        user_id=sales_rep.id,
        user_role=UserRole.MANAGEMENT,
        limit=10,
        offset=0,
    )
    assert len(page1) == 10

    page2 = repository.list(
        user_id=sales_rep.id,
        user_role=UserRole.MANAGEMENT,
        limit=10,
        offset=10,
    )
    assert len(page2) == 5


def test_list_contract_filters_sales_representative(session):
    repository = ContractRepository(session)

    sales_rep_1 = create_persisted_user(session, role_id=UserRole.SALES)
    sales_rep_2 = create_persisted_user(
        session,
        employee_number="003",
        email="sales2@test.com",
        role_id=UserRole.SALES,
    )

    client_1 = create_persisted_client(
        session,
        email="client1@test.com",
        sales_representative_id=sales_rep_1.id,
    )
    client_2 = create_persisted_client(
        session,
        email="client2@test.com",
        sales_representative_id=sales_rep_2.id,
    )

    create_persisted_contract(
        session,
        client_id=client_1.id,
        sales_representative_id=sales_rep_1.id,
    )
    create_persisted_contract(
        session,
        client_id=client_2.id,
        sales_representative_id=sales_rep_2.id,
    )

    contracts = repository.list(
        user_id=sales_rep_1.id, user_role=UserRole.SALES, sales_assigned=True
    )

    assert len(contracts) == 1
    assert contracts[0].sales_representative_id == sales_rep_1.id


def test_list_contract_filters_signed(session):
    repository = ContractRepository(session)

    sales_rep = create_persisted_user(session, role_id=UserRole.SALES)
    client = create_persisted_client(
        session,
        sales_representative_id=sales_rep.id,
    )

    create_persisted_contract(
        session,
        client_id=client.id,
        sales_representative_id=sales_rep.id,
        is_signed=True,
    )
    create_persisted_contract(
        session,
        client_id=client.id,
        sales_representative_id=sales_rep.id,
        is_signed=False,
    )

    contracts = repository.list(
        user_id=sales_rep.id,
        user_role=UserRole.MANAGEMENT,
        is_signed=True,
    )

    assert len(contracts) == 1
    assert contracts[0].is_signed is True


def test_list_contract_filters_paid(session):
    repository = ContractRepository(session)

    sales_rep = create_persisted_user(session, role_id=UserRole.SALES)
    client = create_persisted_client(
        session,
        sales_representative_id=sales_rep.id,
    )

    create_persisted_contract(
        session,
        client_id=client.id,
        sales_representative_id=sales_rep.id,
        remaining_amount=Decimal("0"),
    )
    create_persisted_contract(
        session,
        client_id=client.id,
        sales_representative_id=sales_rep.id,
        remaining_amount=Decimal("100"),
    )

    contracts = repository.list(
        user_id=sales_rep.id,
        user_role=UserRole.MANAGEMENT,
        is_paid=True,
    )

    assert len(contracts) == 1
    assert contracts[0].remaining_amount == 0


# count
############################
def test_count_returns_correct_length(session):
    repository = ContractRepository(session)

    sales_rep = create_persisted_user(session, role_id=UserRole.SALES)
    client = create_persisted_client(
        session,
        sales_representative_id=sales_rep.id,
    )

    for _ in range(15):
        create_persisted_contract(
            session,
            client_id=client.id,
            sales_representative_id=sales_rep.id,
        )

    length = repository.count(
        user_id=sales_rep.id,
        user_role=UserRole.MANAGEMENT,
    )

    assert length == 15


def test_count_filters_signed(session):
    repository = ContractRepository(session)

    sales_rep = create_persisted_user(session, role_id=UserRole.SALES)
    client = create_persisted_client(
        session,
        sales_representative_id=sales_rep.id,
    )

    create_persisted_contract(
        session,
        client_id=client.id,
        sales_representative_id=sales_rep.id,
        is_signed=True,
    )
    create_persisted_contract(
        session,
        client_id=client.id,
        sales_representative_id=sales_rep.id,
        is_signed=False,
    )

    length = repository.count(
        user_id=sales_rep.id,
        user_role=UserRole.MANAGEMENT,
        is_signed=True,
    )

    assert length == 1
