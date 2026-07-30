import pytest

from epicevent.exception import (
    ClientOwnershipError,
    ContractNotFoundError,
    RolePermissionError,
)
from epicevent.schemas.contract_schema import ContractUpdate
from epicevent.security.roles import UserRole
from tests.conftest import (
    create_contract_dto,
    create_persisted_client,
    create_persisted_contract,
    create_persisted_user,
)


# create_contract
###################
def test_create_contract_by_management_success(session, contract_service):
    current_user = create_persisted_user(session, role_id=UserRole.MANAGEMENT)
    client = create_persisted_client(session, sales_representative_id=current_user.id)
    contract_dto = create_contract_dto()

    created = contract_service.create_contract(current_user, client, contract_dto)

    session.refresh(created)
    assert created.id is not None
    assert created.total_amount == contract_dto.total_amount
    assert created.sales_representative_id == current_user.id
    assert created.client_id == client.id


@pytest.mark.parametrize("role", [UserRole.SALES, UserRole.SUPPORT])
def test_unauthorized_user_cannot_create_contract(session, contract_service, role):
    current_user = create_persisted_user(session, role_id=role)
    client = create_persisted_client(session, sales_representative_id=current_user.id)
    contract_dto = create_contract_dto()

    with pytest.raises(RolePermissionError):
        contract_service.create_contract(current_user, client, contract_dto)


# update_contract
###################
def test_sales_can_update_owned_contract(contract_service, session):
    current_user = create_persisted_user(session, role_id=UserRole.SALES)
    client = create_persisted_client(session, sales_representative_id=current_user.id)

    persisted_contract = create_persisted_contract(
        session,
        client_id=client.id,
        sales_representative_id=current_user.id,
        total_amount=1000,
        remaining_amount=500,
        is_signed=False,
    )

    new_data = ContractUpdate(
        total_amount=2000,
        remaining_amount=1000,
        is_signed=True,
    )

    contract_service.update_contract(
        current_user,
        persisted_contract.id,
        new_data,
    )

    session.refresh(persisted_contract)

    assert persisted_contract.total_amount == 2000
    assert persisted_contract.remaining_amount == 1000
    assert persisted_contract.is_signed is True


def test_update_contract_sales_not_owned_contract_raises_error(
    contract_service, session
):
    current_user = create_persisted_user(
        session,
        employee_number="001",
        role_id=UserRole.SALES,
    )

    other_sales = create_persisted_user(
        session,
        employee_number="002",
        email="sales@email.com",
        role_id=UserRole.SALES,
    )

    client = create_persisted_client(
        session,
        sales_representative_id=other_sales.id,
    )

    persisted_contract = create_persisted_contract(
        session,
        client_id=client.id,
        sales_representative_id=other_sales.id,
    )

    new_data = ContractUpdate(
        is_signed=False,
    )

    with pytest.raises(ClientOwnershipError):
        contract_service.update_contract(
            current_user,
            persisted_contract.id,
            new_data,
        )


def test_update_contract_with_invalid_contract_returns_error(contract_service, session):
    current_user = create_persisted_user(session, role_id=UserRole.SALES)

    new_data = ContractUpdate(is_signed=False)

    with pytest.raises(ContractNotFoundError):
        contract_service.update_contract(
            current_user,
            999,
            new_data,
        )


def test_update_contract_unauthorized_user_raises_error(contract_service, session):
    current_user = create_persisted_user(session, role_id=UserRole.SUPPORT)

    client = create_persisted_client(session, sales_representative_id=current_user.id)

    persisted_contract = create_persisted_contract(
        session,
        client_id=client.id,
        sales_representative_id=current_user.id,
    )

    new_data = ContractUpdate(is_signed=False)

    from epicevent.exception import RolePermissionError

    with pytest.raises(RolePermissionError):
        contract_service.update_contract(
            current_user,
            persisted_contract.id,
            new_data,
        )


def test_management_can_update_any_contract(contract_service, session):
    management = create_persisted_user(
        session,
        email="management@email.com",
        role_id=UserRole.MANAGEMENT,
    )

    sales_user = create_persisted_user(
        session, employee_number="002", role_id=UserRole.SALES
    )

    client = create_persisted_client(
        session,
        sales_representative_id=sales_user.id,
    )

    persisted_contract = create_persisted_contract(
        session,
        client_id=client.id,
        sales_representative_id=sales_user.id,
        is_signed=False,
    )

    new_data = ContractUpdate(
        is_signed=True,
    )

    contract_service.update_contract(
        management,
        persisted_contract.id,
        new_data,
    )

    session.refresh(persisted_contract)

    assert persisted_contract.is_signed is True
