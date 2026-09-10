import asyncio
from random import choice, randint
from typing import TYPE_CHECKING, Literal

from discord import Interaction, Member
from discord import app_commands as apc
from discord.ext.commands import Cog

from modules.resources.configs import commands_config
from modules.views.rps_view import RPSView, rps_challenge_start

if TYPE_CHECKING:
    from modules.bot import BussyBot


RPS_OPTIONS = Literal["Rock", "Paper", "Scissors"]
EN_BOOL = Literal["No", "Yes"]


class MiscCog(Cog):
    def __init__(self, bot: BussyBot) -> None:
        super().__init__()
        self.bot = bot

    # TODO: Implement visual elements
    @apc.command(name="coinflip", description="Flips a coin")
    @apc.describe(invisible="Makes the command invisible to everyone else")
    async def _coin_flip(
        self, interaction: Interaction, invisible: EN_BOOL = "No"
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
        chosen_cookie = choice(commands_config["cookies"])
        await interaction.response.send_message(chosen_cookie)

    @apc.command(name="diceroll", description="Roll a d20")
    async def _dice_roll(self, interaction: Interaction) -> None:
        await interaction.response.defer()
        await interaction.followup.send(f"You rolled {randint(1, 20)}!")

    @apc.command(name="time", description="Notifies you after a set time")
    async def _time(self, interaction: Interaction, time_to_wait: int) -> None:
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send(
            content=f"I will notify you after {time_to_wait} seconds have passed!"
        )

        await asyncio.sleep(time_to_wait)

        await interaction.edit_original_response(
            content=f"{interaction.user.mention}, {time_to_wait} seconds have already passed!"
        )
