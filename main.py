import logging
import os
import platform
import random

import aiosqlite
import discord
from discord.ext import commands, tasks
from discord.ext.commands import Context
from discord import app_commands
from dotenv import load_dotenv
from constants import *

from config import app_config
from logFormat import setup_logger

load_dotenv()

log = logging.getLogger() 
setup_logger(log)
log.info("Initializing...")

intents = discord.Intents.default()

class DiscordBot(commands.Bot):
    def __init__(self) -> None:
        super().__init__(
            command_prefix=commands.when_mentioned_or(app_config.bot_prefix),
            intents=intents,
            help_command=None,
        )
        self.log = log
        self.database = None
        self.bot_prefix = app_config.bot_prefix

    async def init_db(self) -> None:
        self.log.debug("Using database file: %s", DB_FILE)
        async with aiosqlite.connect(DB_FILE) as db:
            with open(SCHEMA_FILE, encoding="utf-8") as file:
                await db.executescript(file.read())
            await db.commit()

    async def load_cogs(self) -> None:
        for file in os.listdir(f"{os.path.realpath(os.path.dirname(__file__))}/cogs"):
            if file.endswith(".py"):
                extension = file[:-3]
                try:
                    await self.load_extension(f"cogs.{extension}")
                    self.log.info(f"Loaded extension '{extension}'")
                except Exception as e:
                    self.log.error(f"Failed to load extension {extension}\n{type(e).__name__}: {e}")

    @tasks.loop(minutes=1.0)
    async def status_task(self) -> None:
        statuses = ["On the moon", "In the amazon rainforest", "If I fall I feel I might fly"]
        await self.change_presence(activity=discord.Game(random.choice(statuses)))

    @status_task.before_loop
    async def before_status_task(self) -> None:
        await self.wait_until_ready()

    async def setup_hook(self) -> None:
        self.log.info(f"Logged in as {self.user.name}")
        self.log.info(f"discord.py API version: {discord.__version__}")
        self.log.info(f"Python version: {platform.python_version()}")
        self.log.info(f"Running on: {platform.system()} {platform.release()} ({os.name})")
        self.log.info("-"*25)
        
        await self.init_db()
        await self.load_cogs()
        
        self.log.info("Syncing slash commands globally...")
        try:
            synced = await self.tree.sync()
            self.log.info(f"Successfully synced {len(synced)} application command(s).")
        except Exception as e:
            self.log.error(f"Failed to sync application commands: {e}")

        self.tree.on_error = self.on_tree_error
        self.status_task.start()

    async def on_message(self, message: discord.Message) -> None:
        if message.author == self.user or message.author.bot:
            return
        await self.process_commands(message)

    async def on_tree_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError) -> None:
        if isinstance(error, app_commands.CommandOnCooldown):
            minutes, seconds = divmod(error.retry_after, 60)
            embed = discord.Embed(
                description=f"**Please slow down** - Retry in {round(minutes)}m {round(seconds)}s.",
                color=0xE02B2B,
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        elif isinstance(error, app_commands.MissingPermissions):
            embed = discord.Embed(
                description=f"You lack permissions: {', '.join(error.missing_permissions)}",
                color=0xE02B2B,
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            self.log.error(f"Unhandled tree error: {error}")

    async def on_command_completion(self, context: Context) -> None:
        full_command_name = context.command.qualified_name
        split = full_command_name.split(" ")
        executed_command = str(split[0])
        if context.guild is not None:
            self.log.info(f"Executed {executed_command} command in {context.guild.name} (ID: {context.guild.id}) by {context.author} (ID: {context.author.id})")
        else:
            self.log.info(f"Executed {executed_command} command by {context.author} (ID: {context.author.id}) in DMs")

    async def on_command_error(self, context: Context, error) -> None:
        if isinstance(error, commands.CommandOnCooldown):
            minutes, seconds = divmod(error.retry_after, 60)
            hours, minutes = divmod(minutes, 60)
            hours = hours % 24
            embed = discord.Embed(
                description=f"**Please slow down** - You can use this command again in {f'{round(hours)} hours' if round(hours) > 0 else ''} {f'{round(minutes)} minutes' if round(minutes) > 0 else ''} {f'{round(seconds)} seconds' if round(seconds) > 0 else ''}.",
                color=0xE02B2B,
            )
            await context.send(embed=embed)
        elif isinstance(error, commands.NotOwner):
            embed = discord.Embed(description="You are not the owner of the bot!", color=0xE02B2B)
            await context.send(embed=embed)
            if context.guild:
                self.log.warning(f"{context.author} (ID: {context.author.id}) tried to execute an owner only command in the guild {context.guild.name} (ID: {context.guild.id}), but the user is not an owner of the bot.")
            else:
                self.log.warning(f"{context.author} (ID: {context.author.id}) tried to execute an owner only command in the bot's DMs, but the user is not an owner of the bot.")
        elif isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                description="You are missing the permission(s) `" + ", ".join(error.missing_permissions) + "` to execute this command!",
                color=0xE02B2B,
            )
            await context.send(embed=embed)
        elif isinstance(error, commands.BotMissingPermissions):
            embed = discord.Embed(
                description="I am missing the permission(s) `" + ", ".join(error.missing_permissions) + "` to fully perform this command!",
                color=0xE02B2B,
            )
            await context.send(embed=embed)
        elif isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(
                title="Error!",
                description=str(error).capitalize(),
                color=0xE02B2B,
            )
            await context.send(embed=embed)
        else:
            raise error

bot = DiscordBot()

# log_handler=None protects custom logger settings from being overridden
bot.run(os.getenv("BOT_TOKEN"), log_handler=None)
