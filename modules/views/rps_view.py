from typing import Literal

import discord
from discord import ButtonStyle, Interaction, Member
from discord.ui import Button, View

from modules.resources.configs import rps_config

emoji = rps_config["emoji_list"]


def rps_challenge_start(sender: str, target: str) -> discord.Embed:
    return discord.Embed(
        color=10040886,
        title=f"{sender} is challenging {target} to Rock Paper Scissors!",
        description="Click one of the buttons below to play!",
    )


def rps_challenge_end(name_1: str, name_2: str, state: str) -> discord.Embed:
    return discord.Embed(
        color=10040886,
        title=f"{name_1} challenged {name_2} to Rock Paper Scissors!",
        description=state,
    )


class RPSView(View):
    def __init__(
        self,
        *,
        original: Interaction,
        target: Member | None = None,
        sender: Member,
        choice_1: str,
        timeout: float | None = 180,
    ) -> None:

        super().__init__(timeout=timeout)
        self.original = original
        self.sender = sender
        self.target = target
        self.choice_1 = choice_1
        self.enabled: bool = True

    @discord.ui.button(style=ButtonStyle.red, emoji=emoji["rock"])
    async def _rock(self, interaction: Interaction, _: Button) -> None:
        await self._handle_choice(interaction, "rock")

    @discord.ui.button(style=ButtonStyle.green, emoji=emoji["paper"])
    async def _paper(self, interaction: Interaction, _: Button) -> None:
        await self._handle_choice(interaction, "paper")

    @discord.ui.button(style=ButtonStyle.blurple, emoji=emoji["scissors"])
    async def _scissors(self, interaction: Interaction, _: Button) -> None:
        await self._handle_choice(interaction, "scissors")

    def _rps_evaluate(self, p1: str, p2: str) -> Literal[0, 1, 2]:
        result: int

        if p1 == p2:
            result = 0
        elif (p1, p2) in rps_config["rps_match"]["win"]:
            result = 1
        else:
            result = 2

        return result

    async def _handle_choice(self, interaction: Interaction, choice_2: str) -> None:
        if self.target is not None and interaction.user != self.target:
            await interaction.response.send_message(
                "The challenge is not for you!", ephemeral=True
            )
            return

        if self.sender == interaction.user:
            await interaction.response.send_message(
                "You can't play with yourself!", ephemeral=True
            )
            return

        if not self.enabled:
            await interaction.response.send_message(
                "Somebody else played first.", ephemeral=True
            )
            return

        self.enabled = False

        for btn in (item for item in self.children if isinstance(item, Button)):
            btn.disabled = True

        p1, p2 = self.sender, interaction.user

        p1_name = p1.nick or p1.name
        p2_name = p2.nick or p2.name if isinstance(p2, Member) else p2.name

        names: dict[str, str] = {"name_1": p1_name, "name_2": p2_name}
        result = self._rps_evaluate(self.choice_1, choice_2)

        part_1 = f"{names['name_1']} {emoji[f'hand_{self.choice_1}']} - {emoji[f'hand_{choice_2}']} {names['name_2']}"
        part_2 = "They drew!" if result == 0 else f"{names[f'name_{result}']} won!"

        embed = rps_challenge_end(
            names["name_1"], names["name_2"], f"{part_1}\n{part_2}"
        )

        await interaction.response.edit_message(view=self, embed=embed)
