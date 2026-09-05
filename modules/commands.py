from __future__ import annotations

import asyncio
import json
import logging
from random import choice, randint
from typing import TYPE_CHECKING, Literal

from discord import Interaction, Member
from discord import app_commands as apc
from discord.ext.commands import Cog
from requests import HTTPError

from modules import scraper
from modules.paths import secrets_path
from modules.views.rps_view import RPSView, rps_challenge_start

if TYPE_CHECKING:
    from modules.client import BussyClient
    from modules.json_types import Secrets

secrets: Secrets = json.loads(secrets_path.read_text(encoding="utf8"))
authorized_users: dict[str, int] = secrets["authorized_users"]
logger = logging.getLogger(__name__)

RPS_OPTIONS = Literal["Rock", "Paper", "Scissors"]
ENG_BOOL = Literal["No", "Yes"]

cookies = [
    "https://cdn.discordapp.com/attachments/904971585444786236/1543810880444174521/image.png?ex=6a96396c&is=6a94e7ec&hm=b7f0deb2ded9d92e5a17160a25f491aa9ece4746bdbffff54836d3eb3dfabc98&"
]


# TODO@me: Export this elsewhere
class CommandChecks:
    block_db_access = False

    @classmethod
    def lock_database(cls) -> None:
        cls.block_db_access = True

    @classmethod
    def unlock_database(cls) -> None:
        cls.block_db_access = False

    @classmethod
    async def is_db_unblocked(cls, _: Interaction | None = None) -> bool:
        if cls.block_db_access:
            raise apc.CheckFailure("Database is locked due to an update.")
        return True

    # TODO: Implement this later to not spam dustloop.
    @staticmethod
    def is_update_authorized(interaction: Interaction) -> bool:
        if interaction.user.id not in authorized_users.values():
            raise apc.CheckFailure("Unauthorized user.")
        return True


class CommandsCog(Cog):
    def __init__(self, bot: BussyClient) -> None:
        super().__init__()
        self.bot = bot

    # TODO: Implement visual elements
    @apc.command(name="coinflip", description="Flips a coin")
    @apc.describe(invisible="Makes the reply invisible to everyone else")
    async def _coin_flip(
        self, interaction: Interaction, invisible: ENG_BOOL = "No"
    ) -> None:

        is_heads: bool = choice((True, False))
        reply: str = "heads" if is_heads else "tails"
        reply = f"You got {reply}!"
        flag = invisible == "Yes"
        await interaction.response.send_message(reply, ephemeral=flag)

    @apc.command(
        name="rps", description="Play Rock Paper Scissors against another member"
    )
    @apc.describe(
        choice="Your choice to use", target="Optional: The member to play against"
    )
    @apc.guild_only  # static checkers still whine if you assume the guild exists
    async def _rps(
        self,
        interaction: Interaction,
        choice: RPS_OPTIONS,
        target: Member | None = None,
    ) -> None:

        # do preliminary checks
        if interaction.guild is None:
            await interaction.response.send_message(
                "This command is only designed for guilds."
            )
            return

        target_handle: str = "anyone"

        # handle targets without a nickname
        if target is not None:
            target_handle = target.nick or target.name

        sender: Member | None = interaction.guild.get_member(interaction.user.id)
        if sender is None:
            await interaction.response.send_message("Something went wrong")
            return

        sender_handle = sender.nick or sender.name

        # message creation
        rps_view = RPSView(
            original=interaction, target=target, sender=sender, choice_1=choice.lower()
        )

        embed = rps_challenge_start(sender_handle, target_handle)
        await interaction.response.send_message(embed=embed, view=rps_view)

    @apc.command(name="cookie", description="Gives a random cookie")
    async def _cookie(self, interaction: Interaction) -> None:
        chosen_cookie = choice(cookies)
        await interaction.response.send_message(chosen_cookie)

    @apc.command(name="diceroll", description="Roll a d20")
    async def _dice_roll(self, interaction: Interaction) -> None:
        await interaction.response.send_message(f"You rolled {randint(1, 20)}!")

    @apc.command(name="time", description="Notifies you after a set time")
    async def _time(self, interaction: Interaction, time_to_wait: int) -> None:
        await interaction.response.defer(ephemeral=True)
        await interaction.edit_original_response(
            content=f"I will notify you after {time_to_wait} seconds have passed!"
        )

        await asyncio.sleep(time_to_wait)

        await interaction.edit_original_response(
            content=f"{interaction.user.mention}, {time_to_wait} seconds have already passed!"
        )

    @apc.command(name="update_database", description="Updates the dustloop database")
    @apc.check(CommandChecks.is_db_unblocked)
    @apc.check(CommandChecks.is_update_authorized)
    async def _update_database(self, interaction: Interaction) -> None:
        # reject if an update is already occurring
        if not CommandChecks.is_db_unblocked():
            await interaction.response.send_message(
                "An update is already being done, command rejected.", ephemeral=True
            )
            return

        # block any further attempts at updates or requests
        CommandChecks.lock_database()
        scrape_task = asyncio.create_task(scraper.launch(self.bot.db, scrape=False))
        await interaction.response.send_message("Update started, please wait.")
        await scrape_task
        await interaction.edit_original_response(content="Update complete!")

        CommandChecks.unlock_database()

    @apc.command(
        name="frame_data", description="Receive frame data for a specific move"
    )
    @apc.check(predicate=CommandChecks.is_db_unblocked)
    async def _frame_data(
        self, interaction: Interaction, character: str, move: str
    ) -> None:
        await interaction.response.send_message(
            "Feature not implemented.", ephemeral=True
        )

    @_frame_data.autocomplete(name="character")
    async def character_autocomplete(
        self, interaction: Interaction, current: str
    ) -> list[apc.Choice[str]]:
        names: list[str] = [""]
        return [apc.Choice(name="character", value=name) for name in names]

    @_frame_data.autocomplete(name="move")
    async def move_autocomplete(
        self, interaction: Interaction, current: str
    ) -> list[apc.Choice[str]]:
        names: list[str] = [""]
        return [apc.Choice(name="move", value=name) for name in names]

    @_update_database.error
    async def _on_update_database_error(
        self, interaction: Interaction, error: apc.AppCommandError
    ) -> None:
        if isinstance(error, apc.CheckFailure):
            await interaction.response.send_message(str(error))
        if isinstance(error, HTTPError):
            logger.error("Update failed, check error: %s", error)
            await interaction.response.send_message("Update failed, contact the dev!")
        else:
            logger.error("Frame Data command unhandled exception!")
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
            logger.error("Frame Data command unhandled exception!")
            await interaction.response.send_message(
                "Unhandled exception, please contact the developer!", ephemeral=True
            )

    # @apc.command(name='modal', description='Sends a modal')
    # async def _modal(self, interaction: Interaction) -> None:
    #     await interaction.response.send_modal()
