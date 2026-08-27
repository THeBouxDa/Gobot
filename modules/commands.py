from typing import Final, Literal

import asyncio


import discord
from discord import app_commands as apc
from discord import Member, Interaction
from discord.ext import commands
# from client import BussyClient
from random import random, randint


RPS_OPTIONS = Literal['Rock', 'Paper', 'Scissors']
ENG_BOOL = Literal['No', 'Yes']


# TODO: Implement this later to not spam dustloop.
def is_update_authorized(interaction: Interaction) -> bool:
    return False



class CommandsCog(commands.Cog):
    # decide_group = apc.Group(name='decide', description='Commands that make the choice for you')
    
    @apc.command(name='coinflip', description='Flips a coin')
    @apc.describe(invisible='Makes the reply invisible to everyone else')
    async def _coin_flip(self, interaction: Interaction, invisible: ENG_BOOL = 'No') -> None:
        is_heads: bool = random() < 0.5
        reply: str = "heads" if is_heads else "tails"
        reply = f"You got {reply}!"
        flag = invisible == 'Yes'
        await interaction.response.send_message()


    @apc.command(name='rps', description='Play Rock Paper Scissors against another member')
    @apc.describe(choice='Your choice to use', target='The member to play against')
    async def _rps(self, interaction: Interaction, choice: RPS_OPTIONS, target: Member | None = None) -> None:
        await interaction.response.send_message(f'You chose {choice}')
    
    
    @apc.command(name='diceroll', description='Roll a die of any number of sides')
    @apc.describe(sides='The number of sides')
    async def _dice_roll(self, interaction: Interaction, sides: int) -> None:
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
    
    
   