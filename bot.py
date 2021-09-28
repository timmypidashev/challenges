import discord
from discord.ext import commands
from pyfiglet import Figlet
import psutil
import os
from discord_slash import SlashCommand
from termcolor import colored
import asyncio
import statcord

# tokens!
bot_token="ODc4MDc1OTI3ODYxNTU1MjAx.YR757w.pz0ntPdmwXWEm1dzh20lvizH1r0"
statcord_token="statcord.com-zO5ROpxYMgvP0tv35NbI"

# User defines
my_twitch_url="PUT_TWITCH_URL_HERE!"

# --- Statuses ---
# Playing
client_status_playing = {
    "type": "discord.Game",
    "activiy": ["a game", "something", "a board game :)"],
    "switch": False
}

# Streaming
client_status_streaming = {
    "type": "discord.Streaming",
    "activity": ["a game", "something", "netflix :)"],
    "url": my_twitch_url,
    "switch": False
}

# Listening
client_status_listening = {
    "type": "discord.ActivityType.listening",
    "activity": ["to Spotify", "to myself", "to the rain :D"],
    "switch": False
}

# Watching
client_status_watching = {
    "type": "discord.ActivityType.watching",
    "activity": ["a movie", "dis server", "a game"],
    "switch": False
}

# Online
client_status_online = {
    "type": "discord.Status.online",
    "switch": False
}

# Idle
client_status_idle = {
    "activity": "discord.Status.idle",
    "switch": False
}

# Do Not Disturb
client_status_dnd = {
    "activity": "discord.Status.dnd",
    "switch": False
}


# client setup
client = commands.Bot(
    command_prefix="$",
    description="A bot made for a youtube challenge: make the best discord bot in one file!",
    intents=discord.Intents.all(),
    case_insensitive=True,
    help_command=None
)

# psutil proess tracking
client.process = psutil.Process(os.getpid())

# slash command support
slash = SlashCommand(client, sync_commands=True)

# Statcord support
api = statcord.Client(client, token=statcord_token)


# change_presence(status)
async def change_presence():
    await client.wait_until_ready()

    while not client.is_closed():
        for status in client_status_playing, client_status_streaming, client_status_listening, client_status_watching, client_status_online, client_status_idle, client_status_dnd:
            if status["switch"]:
                await client.change_presence(status=status["type"], activity=status["activity"])
                status["switch"] = False
            else:
                await asyncio.sleep(1)

# on_ready 
@client.event
async def on_ready():
    logo = Figlet(font="slant")
    print(colored(logo.renderText("OneFileChallenge"), "green"))

# cog Admin
class Admin(commands.Cog):
    """ Admin Commands """

    # Shutdown
    @commands.check(commands.is_owner())
    @commands.command(
        name="shutdown",
        brief="Shuts down the bot.",
        help="use this command to shut down the bot.",
        aliases=["sh", "s"]
    )
    async def _shutdown(self, context):
        await context.send("Shutting down...")
        await client.close()

    # Restart
    @commands.check(commands.is_owner())
    @commands.command(
        name="restart",
        brief="Restarts the bot.",
        help="Use this command to restart the bot.",
        aliases=["r", "re"]
    )
    async def _restart(self, context):
        await context.send("Restarting...")
        os.execl(sys.executable, sys.executable, *sys.argv)

    # Status
    @commands.check(commands.is_owner())
    @commands.command(
        name="status",
        brief="Change the bot status, or turn it off entirely",
        help="use this command to change bot status or turn it off entirely.",
        aliases=["stat", "st"]
    )
    async def _status(self, context):
        pass


def run():
    client.add_cog(Admin(client))
    client.run(token)