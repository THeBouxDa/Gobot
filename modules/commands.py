from typing import Final, Literal, Any
from collections.abc import Callable

import asyncio

import discord
from discord import app_commands as apc
from discord import Member, Interaction
from discord.ext import commands
from random import random, randint

from views.rps_view import RPSView, rps_challenge_start


RPS_OPTIONS = Literal['Rock', 'Paper', 'Scissors']
ENG_BOOL = Literal['No', 'Yes']


# TODO: Implement this later to not spam dustloop.
def is_update_authorized(interaction: Interaction) -> bool:
    return False


class CommandsCog(commands.Cog):

    # TODO: Implement visual elements
    @apc.command(name='coinflip', description='Flips a coin')
    @apc.describe(invisible='Makes the reply invisible to everyone else')
    async def _coin_flip(self, interaction: Interaction, invisible: ENG_BOOL = 'No') -> None:
        
        is_heads: bool = random() < 0.5
        reply: str = "heads" if is_heads else "tails"
        reply = f"You got {reply}!"
        flag = invisible == 'Yes'
        await interaction.response.send_message(reply, ephemeral=flag)


    @apc.command(name='rps', description='Play Rock Paper Scissors against another member')
    @apc.describe(choice='Your choice to use', target='The member to play against')
    @apc.guild_only # static checkers still whine if you assume the guild exists
    async def _rps(self, interaction: Interaction, choice: RPS_OPTIONS, target: Member | None = None) -> Any:
        
        # preliminary checks 
        if interaction.guild is None:
            return await interaction.response.send_message("This command is only designed for guilds.")
        
        target_handle: str = target.nick if target and target.nick else "anyone"
        sender: Member | None = interaction.guild.get_member(interaction.user.id)
        
        if sender is None:
            return await interaction.response.send_message("Something went wrong")
        
        # message creation
        rps_view = RPSView(original=interaction, target=target, sender=sender, choice_1=choice.lower())
        embed = rps_challenge_start(sender.nick, target_handle)
        
        await interaction.response.send_message(embed=embed, view=rps_view)
    
    def _rps_engine(self, original: Interaction) -> Callable:
        
        async def result():
            pass
        
        return result
        
    
    
    @apc.command(name='diceroll', description='Roll a die of any number of sides')
    @apc.describe(sides='The number of sides')
    async def _dice_roll(self, interaction: Interaction, sides: apc.Range[int, 1, 2147483647]) -> None:
        try:
            await interaction.response.defer()
            await interaction.response.send_message(f'You rolled {randint(1, sides)}!')
        except Exception as e:
            await interaction.response.send_message('Something went wrong.')
    
    
    @apc.command(name='time', description='Notifies you after a set time')
    async def _time(self, interaction: discord.Interaction, time_to_wait: int):
        await interaction.response.defer(ephemeral=True)
        await interaction.edit_original_response(content=f"I will notify you after {time_to_wait} seconds have passed!")
        await asyncio.sleep(time_to_wait)

        await interaction.edit_original_response(content=f"{interaction.user.mention}, {time_to_wait} seconds have already passed!")


    @apc.command(name='update_database', description='Updates the dustloop database')
    @apc.check(is_update_authorized)
    async def _update_database(self, interaction: Interaction) -> None:
        pass
    
    
    async def _frame_data(self, interaction: Interaction, character: str, move: str) -> None:
        pass

        
    # @apc.command(name='modal', description='Sends a modal')
    # async def _modal(self, interaction: Interaction) -> None:
    #     await interaction.response.send_modal()
    
    
