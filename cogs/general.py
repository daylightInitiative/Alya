import platform
import random
import discord
from discord import app_commands
from discord.ext import commands
from logFormat import getMainLogger
from timer import TimeConverter, duration_to_string

log = getMainLogger()

class FeedbackForm(discord.ui.Modal, title="Feedback"):
    feedback = discord.ui.TextInput(
        label="What do you think about this bot?",
        style=discord.TextStyle.long,
        placeholder="Type your answer here...",
        required=True,
        max_length=256,
    )

    async def on_submit(self, interaction: discord.Interaction):
        self.interaction = interaction
        self.answer = str(self.feedback)
        self.stop()

class General(commands.Cog, name="general"):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.db = bot.db
        
        self.remove_spoilers_menu = app_commands.ContextMenu(
            name="Remove spoilers",
            callback=self.remove_spoilers
        )
        self.grab_id_menu = app_commands.ContextMenu(
            name="Grab ID",
            callback=self.grab_id
        )
        
        self.bot.tree.add_command(self.remove_spoilers_menu)
        self.bot.tree.add_command(self.grab_id_menu)

    async def remove_spoilers(self, interaction: discord.Interaction, message: discord.Message) -> None:
        spoiler_attachment = None
        for attachment in message.attachments:
            if attachment.is_spoiler():
                spoiler_attachment = attachment
                break
        embed = discord.Embed(
            title="Message without spoilers",
            description=message.content.replace("||", ""),
            color=0xBEBEFE,
        )
        if spoiler_attachment is not None:
            embed.set_image(url=attachment.url)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def grab_id(self, interaction: discord.Interaction, user: discord.User) -> None:
        embed = discord.Embed(
            description=f"The ID of {user.mention} is `{user.id}`.",
            color=0xBEBEFE,
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    def cog_unload(self) -> None:
        self.bot.tree.remove_command(self.remove_spoilers_menu.name, type=self.remove_spoilers_menu.type)
        self.bot.tree.remove_command(self.grab_id_menu.name, type=self.grab_id_menu.type)

    # @commands.hybrid_command(
    #     name="Shutdown", description="Internal command for shutting down the bot."
    # )
    # @commands.is_owner()
    # async def shutdown(self, context) -> None:
    #     await context.send("Shutting down...")
    #     await bot.close() need to implement this correctly, maybe even a restart functionality with cog status streams

    @commands.hybrid_command(
        name="help", description="List all commands the bot has loaded."
    )
    async def help(self, context) -> None:
        embed = discord.Embed(
            title="Help", description="List of available commands:", color=0xBEBEFE
        )
        for i in self.bot.cogs:
            if i == "owner" and not (await self.bot.is_owner(context.author)):
                continue
            cog = self.bot.get_cog(i.lower())
            commands_list = cog.get_commands()
            data = []
            for command in commands_list:
                description = command.description.partition("\n")
                data.append(f"{command.name} - {description}")
            help_text = "\n".join(data)
            embed.add_field(
                name=i.capitalize(), value=f"```{help_text}```", inline=False
            )
        await context.send(embed=embed)

    @commands.hybrid_command(
        name="botinfo",
        description="Get some useful (or not) information about the bot.",
    )
    async def botinfo(self, context) -> None:
        embed = discord.Embed(
            description="Alya Bot",
            color=0xBEBEFE,
        )
        embed.set_author(name="Bot Information")
        embed.add_field(name="Owner:", value="https://github.com/daylightInitiative", inline=True)
        embed.add_field(
            name="Python Version:", value=f"{platform.python_version()}", inline=True
        )
        embed.add_field(
            name="Prefix:",
            value=f"/ (Slash Commands) or {self.bot.bot_prefix} for normal commands",
            inline=False,
        )
        embed.set_footer(text=f"Requested by {context.author}")
        await context.send(embed=embed)

    @commands.hybrid_command(
        name="serverinfo",
        description="Get some useful information about the server.",
    )
    async def serverinfo(self, context) -> None:
        if context.guild is None:
            await context.send("This command can only be used inside a server!", ephemeral=True)
            return

        roles = [role.name for role in context.guild.roles]
        num_roles = len(roles)
        if num_roles > 50:
            roles = roles[:50]
            roles.append(f">>>> Displaying [50/{num_roles}] Roles")
        roles = ", ".join(roles)

        embed = discord.Embed(
            title="**Server Name:**", description=f"{context.guild}", color=0xBEBEFE
        )
        if context.guild.icon is not None:
            embed.set_thumbnail(url=context.guild.icon.url)
        embed.add_field(name="Server ID", value=context.guild.id)
        embed.add_field(name="Member Count", value=context.guild.member_count)
        embed.add_field(
            name="Text/Voice Channels", value=f"{len(context.guild.channels)}"
        )
        embed.add_field(name=f"Roles ({len(context.guild.roles)})", value=roles)
        embed.set_footer(text=f"Created at: {context.guild.created_at}")
        await context.send(embed=embed)

    @commands.hybrid_command(
        name="ping",
        description="Check if the bot is alive.",
    )
    async def ping(self, context) -> None:
        embed = discord.Embed(
            title="Pong!",
            description=f"The bot latency is {round(self.bot.latency * 1000)}ms.",
            color=0xBEBEFE,
        )
        await context.send(embed=embed)

    @commands.hybrid_command(
        name="timer",
        description="Creates a timer given a duration, you will be mentioned after the timer has expired.",
    )
    async def timer(self, context, duration: TimeConverter) -> None:
        display_time = duration_to_string(total_seconds=duration)
        embed = discord.Embed(
            title="Timer set",
            description=f"Set a timer for {display_time}. We will mention you when it has concluded.",
            color=0xBEBEFE,
        )
        await context.send(embed=embed)


    @commands.hybrid_command(
        name="server",
        description="Get the invite link of the discord server of the bot for some support.",
    )
    async def server(self, context) -> None:
        embed = discord.Embed(
            description=f"Join the support server for the bot, and request an invite.",
            color=0xD75BF4,
        )
        try:
            await context.author.send(embed=embed)
            await context.send("I sent you a private message!")
        except discord.Forbidden:
            await context.send(embed=embed)



async def setup(bot) -> None:
    await bot.add_cog(General(bot))
