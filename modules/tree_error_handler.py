from discord import Interaction
from discord import app_commands as apc


async def on_tree_error(interaction: Interaction, error: apc.AppCommandError):
    if isinstance(error, apc.CommandOnCooldown):
        await interaction.response.send_message(f"Command is currently on cooldown! Try again in **{error.retry_after:.2f}** seconds!")
    elif isinstance(error, apc.MissingPermissions):
        await interaction.response.send_message(f"You don't have the permissions required to use this command.")
    elif isinstance(error, apc.BotMissingPermissions):
        await interaction.response.send_message(f"I don't have the permissions required to execute this command.")
    else:
        raise error