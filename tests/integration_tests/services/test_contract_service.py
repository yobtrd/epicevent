import pytest

from epicevent.exception import RolePermissionError
from epicevent.security.roles import UserRole
from tests.conftest import (
    create_contract_dto,
    create_persisted_client,
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
