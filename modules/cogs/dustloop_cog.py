from __future__ import annotations

import asyncio
from collections.abc import Sequence
from typing import TYPE_CHECKING, Any

from discord import Interaction
from discord import app_commands as apc
from discord.ext.commands import Cog
from requests import HTTPError
from sqlalchemy import Row, text
from sqlalchemy.exc import IntegrityError

from modules.resources.queries import get_query
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

    @apc.command(name="update_database", description="Updates the dustloop database.")
    @apc.describe(download="Whether downloading from dustloop is necessary.")
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
            await interaction.response.defer(ephemeral=True)
            # block any further attempts at updates or requests
            CommandChecks.lock_database()

            scrape_task = asyncio.create_task(
                scraper.launch(self.bot.db, scrape=download)
            )

            await interaction.followup.send("Update started, please wait.")
            await scrape_task
            await interaction.edit_original_response(content="Update complete!")
        finally:
            CommandChecks.unlock_database()

    @apc.command(name="frame_data", description="Get frame data for any specific move")
    @apc.describe(
        character="The character to get the move from.",
        move="The move to get data about; inserting a character is required for autocompletion.",
        invisible="Whether the reply is invisible to others or not.",
    )
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

        await interaction.response.defer()

        query = get_query("dustloop.select_move")
        if TYPE_CHECKING:
            assert isinstance(query, str)

        async with self.bot.db.engine.connect() as conn:
            result = await conn.execute(text(query), {"char": character, "move": move})

            move_data = result.fetchone()

        if move_data is None:
            await interaction.followup.send("Move not found...", ephemeral=True)
        else:
            await interaction.followup.send(
                embeds=frame_data_builder(move_data._asdict()), ephemeral=invisible
            )

    @apc.command(
        name="character_alias",
        description="Creates an alias for a character",
    )
    @apc.describe(
        character="The character the alias is for.",
        alias="The alias to which you refer the character by.",
    )
    @apc.checks.cooldown(2, 10)
    async def _add_character_alias(
        self, interaction: Interaction, character: str, alias: str
    ) -> None:

        await interaction.response.defer(ephemeral=True)

        try:
            async with self.bot.db.engine.begin() as conn:
                await conn.execute(
                    text(get_query("dustloop.insert_character_alias")),
                    {"char": character, "alias": alias},
                )

                logger.success(
                    'Character alias "%s" for "%s" has been added by user [%s@%s].',
                    alias,
                    character,
                    interaction.user.name,
                    interaction.user.id,
                )
                await interaction.followup.send("Alias added!")
        except IntegrityError as e:
            logger.exception("Error during character alias insertion:")
            error_msg = str(e.orig)

            if "UNIQUE constraint failed" in error_msg:
                await interaction.followup.send("This character alias already exists.")
            elif "NOT NULL constraint failed" in error_msg:
                await interaction.followup.send("Some information is missing!")
            else:
                await interaction.followup.send(
                    "Something went wrong, go bother the dev."
                )

        except Exception:
            logger.exception(
                "Exceptional unspecified error during character alias creation!"
            )
            await interaction.followup.send(
                "Something went exceptionally wrong, go bother the dev."
            )

    @apc.command(name="move_alias", description="Create an alias for a move")
    @apc.checks.cooldown(2, 10)
    @apc.describe(
        move="The move the alias is for.",
        character="The character the move is from.",
        alias="The alias to which you refer the character by.",
    )
    async def _add_move_alias(
        self, interaction: Interaction, character: str, move: str, alias: str
    ) -> None:
        await interaction.response.defer(ephemeral=True)

        try:
            async with self.bot.db.engine.begin() as conn:
                cursor = await conn.execute(
                    text(get_query("dustloop.insert_move_alias")),
                    {"char": character, "move": move, "alias": alias},
                )
                await conn.commit()
                row_count = cursor.rowcount

        except IntegrityError as e:
            logger.exception("IntegrityError during move alias insertion:")
            error_msg = str(e.orig)

            if "UNIQUE constraint failed" in error_msg:
                await interaction.followup.send(
                    f"This move alias already exists for {character}."
                )
            elif "NOT NULL constraint failed" in error_msg:
                await interaction.followup.send("Some information is missing!")
            else:
                await interaction.followup.send(
                    "Something went wrong, go bother the dev."
                )
        except Exception:
            logger.exception("Unspecified error during move alias creation:")
            await interaction.followup.send(
                "Something went exceptionally wrong, go bother the dev."
            )
        else:
            if row_count == 0:
                await interaction.followup.send("Move not found...")
            else:
                await interaction.followup.send("Alias added!")
                logger.success(
                    'Move alias "%s" for move "%s" of "%s" has been added by user [%s@%s].',
                    alias,
                    move,
                    character,
                    interaction.user.name,
                    interaction.user.id,
                )

    @_frame_data.autocomplete("character")
    @_add_character_alias.autocomplete("character")
    @_add_move_alias.autocomplete("character")
    async def _character_autocomplete(
        self, _: Interaction, current: str
    ) -> list[apc.Choice[str]]:

        suggestions: list[str]
        # logger.checkpoint("Autocomplete in action.")
        async with self.bot.db.engine.connect() as conn:
            if current == "":
                result = await conn.execute(
                    text(get_query("dustloop.autocomplete_character_default"))
                )

                rows = result.all()
                suggestions = [row.tuple()[0] for row in rows]
            else:
                result = await conn.execute(
                    text(get_query("dustloop.autocomplete_character")),
                    {"cur": current},
                )

                rows = result.all()
                suggestions = [row.tuple()[0] for row in rows]

        # print(names)
        return [apc.Choice(name=auto, value=auto) for auto in suggestions]

    @_frame_data.autocomplete("move")
    @_add_move_alias.autocomplete("move")
    async def _move_autocomplete(
        self, interaction: Interaction, current: str
    ) -> list[apc.Choice[str]]:
        suggestions: dict[str, str] = {}
        character: str = interaction.namespace.character

        async with self.bot.db.engine.connect() as conn:
            rows: Sequence[Row[Any]]
            if character is None:
                rows = []
            elif current == "":
                result = await conn.execute(
                    text(get_query("dustloop.autocomplete_move_default")),
                    {"char": character},
                )

                rows = result.all()
                # suggestions = [row.tuple()[0] for row in rows]
            else:
                result = await conn.execute(
                    text(get_query("dustloop.autocomplete_move")),
                    {"char": character, "cur": current},
                )

                rows: Sequence[Row[Any]] = result.all()

        for row in rows:
            data_dict = row._asdict()
            move_input = key = data_dict.get("input")
            move_name = data_dict.get("name")

            if TYPE_CHECKING:
                assert isinstance(key, str)
                assert isinstance(move_name, str)
                assert isinstance(move_input, str)

            move_input = move_input.replace(";", "/")

            if move_name:
                suggestions[key] = f"{move_name} ({move_input})"
            else:
                suggestions[key] = move_input

        return [apc.Choice(name=value, value=key) for key, value in suggestions.items()]

    @_update_database.error
    async def _on_update_database_error(
        self, interaction: Interaction, error: apc.AppCommandError
    ) -> None:
        if isinstance(error, apc.CheckFailure):
            await interaction.response.send_message(str(error), ephemeral=True)
        elif isinstance(error, apc.CommandOnCooldown):
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
            # await interaction.response.send_message(
            #     "Unhandled exception, please contact the developer!", ephemeral=True
            # )

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

    @_add_character_alias.error
    async def _on_add_character_alias_error(
        self, interaction: Interaction, error: apc.AppCommandError
    ) -> None:
        if isinstance(error, apc.CommandOnCooldown):
            await interaction.response.send_message(
                "Command is currently on cooldown!", ephemeral=True
            )

    @_add_move_alias.error
    async def _on_add_move_alias_error(
        self, interaction: Interaction, error: apc.AppCommandError
    ) -> None:
        if isinstance(error, apc.CommandOnCooldown):
            await interaction.response.send_message(
                "Command is currently on cooldown!", ephemeral=True
            )
