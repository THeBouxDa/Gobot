from logging import getLogger
import sys
import traceback
import requests

from discord import Interaction
from discord import app_commands as apc

# logger = getLogger(__name__)


# async def on_tree_error(interaction: Interaction, error: apc.AppCommandError):
#     if isinstance(error, apc.CommandOnCooldown):
#         await interaction.response.send_message(f"Command is currently on cooldown! Try again in **{error.retry_after:.2f}** seconds!", ephemeral=True)
#     elif isinstance(error, apc.MissingPermissions):
#         await interaction.response.send_message(f"You don't have the permissions required to use this command.", ephemeral=True)
#     elif isinstance(error, apc.BotMissingPermissions):
#         await interaction.response.send_message(f"I don't have the permissions required to execute this command.", ephemeral=True)
#     elif isinstance(error, apc.CommandInvokeError):
#         await interaction.response.send_message(f"The command failed.", ephemeral=True)
    # else:
    #     logger.exception("Ignoring exception in command %s:", interaction.command)
        # traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)