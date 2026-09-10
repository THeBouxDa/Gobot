from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from discord import Interaction
from discord import app_commands as apc
from discord.ext.commands import Cog
from requests import HTTPError
from sqlalchemy import text

from modules.scraper import scraper
from modules.utils.check_utils import CommandChecks
from modules.utils.logging_utils import get_logger
from modules.views.frame_data_embed import frame_data_builder

if TYPE_CHECKING:
    from modules.bot import BussyBot

logger = get_logger(__name__)


class DustloopCog(Cog):
    def __init__(self, bot: BussyBot) -> None:
        super().__init__()
        self.bot = bot

    @apc.command(name="update_database", description="Updates the dustloop database")
    @apc.checks.cooldown(1, 120)
    @apc.check(CommandChecks.is_db_unblocked)
    @apc.check(CommandChecks.is_update_authorized)
    async def _update_database(
        self,
        interaction: Interaction,
        download: bool = True,
    ) -> None:
        """Starts a database update."""

        try:
            # block any further attempts at updates or requests
            CommandChecks.lock_database()

            scrape_task = asyncio.create_task(
                scraper.launch(self.bot.db, scrape=download)
            )

            await interaction.response.send_message("Update started, please wait.")
            await scrape_task
            await interaction.edit_original_response(content="Update complete!")
        finally:
            CommandChecks.unlock_database()

    @apc.command(name="frame_data", description="Get frame data for any specific move")
    @apc.allowed_installs(guilds=True, users=True)
    @apc.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @apc.check(predicate=CommandChecks.is_not_updating)
    async def _frame_data(
        self,
        interaction: Interaction,
        character: str,
        move: str,
        invisible: bool = False,
    ) -> None:
        """Searches for move in database and sends an embed."""
        async with self.bot.db.engine.connect() as conn:
            result = await conn.execute(
                text(
                    """
                        SELECT * FROM moves
                        WHERE LOWER(char_name) = LOWER(:char)
                        AND
                        LOWER(input) = LOWER(:move)
                        ORDER BY move_id ASC;
                    """
                ),
                {"char": character, "move": move},
            )

            move_data = result.fetchone()

        if move_data is None:
            await interaction.response.send_message("Move not found...", ephemeral=True)
        else:
            await interaction.response.send_message(
                embeds=frame_data_builder(move_data._asdict()), ephemeral=invisible
            )

    @_frame_data.autocomplete("character")
    async def _character_autocomplete(
        self, _: Interaction, current: str
    ) -> list[apc.Choice[str]]:

        suggestions: list[str]
        # logger.checkpoint("Autocomplete in action.")
        async with self.bot.db.engine.connect() as conn:
            if current == "":
                result = await conn.execute(
                    text("SELECT name FROM characters ORDER BY name ASC LIMIT 25;")
                )

                rows = result.all()
                suggestions = [row.tuple()[0] for row in rows]
            else:
                result = await conn.execute(
                    text(
                        """
                            SELECT name FROM characters
                            WHERE LOWER(name) LIKE CONCAT('%', LOWER(:cur), '%')
                            ORDER BY name ASC
                            LIMIT 25;
                        """
                    ),
                    {"cur": current},
                )

                rows = result.all()
                suggestions = [row.tuple()[0] for row in rows]

        # print(names)
        return [apc.Choice(name=auto, value=auto) for auto in suggestions]

    @_frame_data.autocomplete("move")
    async def _move_autocomplete(
        self, interaction: Interaction, current: str
    ) -> list[apc.Choice[str]]:
        suggestions: list[str] = []
        character: str = interaction.namespace.character

        async with self.bot.db.engine.connect() as conn:
            if character is None:
                ...
            elif current == "":
                result = await conn.execute(
                    text(
                        """
                            SELECT input FROM moves
                            WHERE LOWER(char_name) = LOWER(:char)
                            ORDER BY move_id ASC
                            LIMIT 25;
                        """
                    ),
                    {"char": character},
                )

                rows = result.all()
                suggestions = [row.tuple()[0] for row in rows]
            else:
                result = await conn.execute(
                    text(
                        """
                            SELECT input FROM moves
                            WHERE LOWER(char_name) = LOWER(:char)
                            AND LOWER(input) LIKE CONCAT('%', LOWER(:cur), '%')
                            ORDER BY move_id ASC
                            LIMIT 25;
                        """
                    ),
                    {"char": character, "cur": current},
                )

                rows = result.all()
                suggestions = [row.tuple()[0] for row in rows]

        return [apc.Choice(name=auto, value=auto) for auto in suggestions]

    @_update_database.error
    async def _on_update_database_error(
        self, interaction: Interaction, error: apc.AppCommandError
    ) -> None:
        if isinstance(error, apc.CheckFailure):
            # logger.error("Check failure, check error: %s", error)
            await interaction.response.send_message(str(error), ephemeral=True)
        elif isinstance(error, apc.CommandOnCooldown):
            # logger.error("Command on cooldown: %s", error)
            await interaction.response.send_message(
                "Command is currently on cooldown!", ephemeral=True
            )
        elif isinstance(error, HTTPError):
            logger.error("Update failed, check error: %s", error)
            await interaction.response.send_message(
                "Update failed, contact the dev!", ephemeral=True
            )
        else:
            logger.error("Frame Data command unhandled exception!%s", error)
            await interaction.response.send_message(
                "Unhandled exception, please contact the developer!", ephemeral=True
            )

    @_frame_data.error
    async def _on_frame_data_error(
        self, interaction: Interaction, error: apc.AppCommandError
    ) -> None:
        if isinstance(error, apc.CheckFailure):
            await interaction.response.send_message(
                "Frame data is not available during an update, please try later!",
                ephemeral=True,
            )
        else:
            logger.error("Frame Data command unhandled exception!%s", error)
            await interaction.response.send_message(
                "Unhandled exception, please contact the developer!", ephemeral=True
            )
