from typing import TYPE_CHECKING

from discord.app_commands import CheckFailure

from modules.resources.configs import secrets_config

if TYPE_CHECKING:
    from discord import Interaction


class CommandChecks:
    _block_db_access = False
    _authorized_users: dict[str, int] = secrets_config["authorized_users"]

    @classmethod
    def lock_database(cls) -> None:
        cls._block_db_access = True

    @classmethod
    def unlock_database(cls) -> None:
        cls._block_db_access = False

    @classmethod
    def is_db_unblocked(cls, _: Interaction | None = None) -> bool:
        if cls._block_db_access:
            raise CheckFailure("Database is locked due to an update.")
        return True

    @classmethod
    def is_not_updating(cls, _: Interaction | None = None) -> bool:
        if cls._block_db_access:
            raise CheckFailure("An update is under way.")

        return True

    @classmethod
    def is_update_authorized(cls, interaction: Interaction) -> bool:
        if interaction.user.id not in cls._authorized_users.values():
            raise CheckFailure("Unauthorized user.")
        return True
