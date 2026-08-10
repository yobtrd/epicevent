from epicevent.exception import (
    SuperuserAlreadyExistsError,
    UserAlreadyDeactivatedError,
    UserNotFoundError,
)
from epicevent.infrastructure import monitoring
from epicevent.infrastructure.unit_of_work import UnitOfWork
from epicevent.models.user import User
from epicevent.schemas.user_schema import (
    SuperuserCreate,
    UserCreate,
    UserResponse,
    UserUpdateManagement,
    UserUpdateSelf,
    normalize_employee_number,
)
from epicevent.security.decorators import require_permission
from epicevent.security.permission import Permission
from epicevent.security.roles import UserRole
from epicevent.services.password_service import PasswordService


class UserService:
    """Handle user management operations."""

    def __init__(
        self,
        uow: UnitOfWork,
        password_service: PasswordService,
    ) -> None:
        self.uow = uow
        self.password_service = password_service

    def get_user_by_employee_number(self, employee_number: str) -> User:
        """
        Retrieve a user by employee number.

        Raises:
            UserNotFoundError: If no user matches the employee number.
        """
        employee_number = normalize_employee_number(employee_number)
        user = self.uow.users.find_by_employee_number(employee_number)
        if user is None:
            raise UserNotFoundError()
        return user

    def ensure_can_create_superuser(self) -> None:
        """
        Ensure that a superuser can be created.

        Raises:
            SuperuserAlreadyExistsError: If a superuser already exists.
        """
        if self.uow.users.superuser_exists():
            raise SuperuserAlreadyExistsError()

    def create_superuser(self, user_data: SuperuserCreate) -> User:
        """Create a user with the management role and a hashed password."""
        self.ensure_can_create_superuser()

        with self.uow:
            hashed_password = self.password_service.hash(user_data.password)

            data = user_data.model_dump(exclude={"password"})
            data["password_hash"] = hashed_password
            data["role_id"] = UserRole.MANAGEMENT

            user = User(**data)
            self.uow.users.save(user)

        return user

    @require_permission(Permission.CREATE_USER)
    def create_user(
        self,
        current_user: UserResponse,
        user_data: UserCreate,
    ) -> User:
        """Create a user with a hashed password."""
        with self.uow:
            hashed_password = self.password_service.hash(user_data.password)

            data = user_data.model_dump(exclude={"password"})
            data["password_hash"] = hashed_password

            user = User(**data)
            self.uow.users.save(user)

        monitoring.capture_event(
            "user_created",
            user_id=user.id,
            actor_id=current_user.id,
        )

        return user

    def _apply_user_updates(self, user: User, user_data: dict) -> None:
        """
        Apply user updates to an entity.

        Password updates are hashed before being stored.
        """
        for field, value in user_data.items():
            if field == "password":
                user.password_hash = self.password_service.hash(value)
            else:
                setattr(user, field, value)
        self.uow.users.save(user)

    def update_self(
        self,
        current_user: UserResponse,
        user_data: UserUpdateSelf,
    ) -> User:
        with self.uow:
            user = self.get_user_by_employee_number(current_user.employee_number)
            self._apply_user_updates(user, user_data.model_dump(exclude_unset=True))

        monitoring.capture_event(
            "user_profile_updated",
            user_id=user.id,
        )

        return user

    @require_permission(Permission.UPDATE_USER)
    def update_user(
        self,
        current_user: UserResponse,
        employee_number: str,
        user_data: UserUpdateManagement,
    ) -> User:
        with self.uow:
            user = self.get_user_by_employee_number(employee_number)
            self._apply_user_updates(user, user_data.model_dump(exclude_unset=True))

        monitoring.capture_event(
            "user_updated_management",
            user_id=user.id,
            actor_id=current_user.id,
        )

        return user

    @require_permission(Permission.LIST_USER)
    def list_users(
        self,
        current_user: UserResponse,
        include_inactive: bool = False,
        limit: int = 10,
        offset: int = 0,
    ) -> tuple[list[User], int]:
        """
        Retrieve users with pagination.

        Returns the paginated users and the total matching count.
        """
        with self.uow:
            users = self.uow.users.list(
                include_inactive=include_inactive,
                limit=limit,
                offset=offset,
            )
            total_count = self.uow.users.count(include_inactive=include_inactive)
        return users, total_count

    @require_permission(Permission.DEACTIVATE_USER)
    def deactivate(
        self,
        current_user: UserResponse,
        employee_number: str,
    ) -> User:
        """
        Deactivate a user account.

        Raises:
            UserNotFoundError: If the user does not exist.
            UserAlreadyDeactivatedError: If the account is already inactive.
        """
        with self.uow:
            user = self.get_user_by_employee_number(employee_number)
            if not user.is_active:
                raise UserAlreadyDeactivatedError()
            user.is_active = False
            self.uow.users.save(user)
        return user
