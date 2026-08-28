from typing import Literal, Any

import discord
from discord import Interaction, Member, ButtonStyle
from discord.ui import View, Button

from config import emoji_list, rps_match
# from private.config import rps_challenge_end

def rps_challenge_start(sender, target) -> discord.Embed:
    return discord.Embed(
        color=10040886,
        title=f"{sender} is challenging {target} to Rock Paper Scissors!",
        description="Click one of the buttons below to play!",
    )

def rps_challenge_end(name_1, name_2, state) -> discord.Embed:
    return discord.Embed(
        color=10040886,
        title=f"{name_1} challenged {name_2} to Rock Paper Scissors!",
        description=state
    )

class RPSView(View):

    def __init__(
        self,
        *,
        original: Interaction,
        target: Member | None = None,
        sender: Member,
        choice_1: str,
        timeout: float | None = 180
        ) -> None:

        super().__init__(timeout=timeout)
        self.original = original
        self.sender = sender
        self.target = target
        self.choice_1 = choice_1
        self.enabled: bool = True
    
    
    @discord.ui.button(style=ButtonStyle.red, emoji=emoji_list['rock'])
    async def _rock(self, interaction: Interaction, button: Button) -> None:
        await self._handle_choice(interaction, button, 'rock')
    

    @discord.ui.button(style=ButtonStyle.green, emoji=emoji_list['paper'])
    async def _paper(self, interaction: Interaction, button: Button) -> None:
        await self._handle_choice(interaction, button, 'paper')


    @discord.ui.button(style=ButtonStyle.blurple, emoji=emoji_list['scissors'])
    async def _scissors(self, interaction: Interaction, button: Button) -> None:
        await self._handle_choice(interaction, button, 'scissors')
    
    
    def _rps_evaluate(self, p1: str, p2: str) -> Literal[0, 1, 2]:
        result: int

        if p1 == p2: result = 0
        elif (p1, p2) in rps_match['win']: result = 1
        else: result = 2
        
        return result


    async def _handle_choice(self, interaction: Interaction, button: Button, choice_2: str) -> Any:
        if self.target is not None and interaction.user != self.target:
            return await interaction.response.send_message("The challenge is not for you!", ephemeral=True)

        # TODO: UNCOMMENT THIS BY THE END
        # if self.sender == interaction.user:
        #     return await interaction.response.send_message("You can't play with yourself!", ephemeral=True)
        
        if not self.enabled:
            return await interaction.response.send_message("Somebody else played first.", ephemeral=True)
        
        self.enabled = False
        
        for btn in (item for item in self.children if isinstance(item, Button)):
            btn.disabled = True
        
        
        p1, p2 = self.original, interaction
        # interaction.user.nick is never None inside of guilds, which this command requires.
        names: dict[str, str] = dict([("name_1", p1.user.nick), ("name_2", p2.user.nick)]) # type: ignore
        result = self._rps_evaluate(self.choice_1, choice_2)
        
        part_1 = f"{names['name_1']} {emoji_list[f'hand_{self.choice_1}']} - {emoji_list[f'hand_{choice_2}']} {names['name_2']}"
        part_2 = "They drew!" if result == 0 else f"{names[f'name_{result}']} won!" 
        
        embed = rps_challenge_end(names['name_1'], names['name_2'], f"{part_1}\n{part_2}")
        
        await interaction.response.edit_message(view=self, embed=embed)
        # await p1.followup.send(result["p1"], ephemeral=True)
        # await p2.followup.send(result["p2"], ephemeral=True)
