import discord
from discord.ext import commands, menus
from pyfiglet import Figlet
import psutil
import os
import sys
from termcolor import colored
import asyncio
import statcord
import logging
import random
import time
from datetime import datetime, timedelta
import wavelink
import re
import math
import copy
import async_timeout
import typing

# start_time
start_time = time.time()

# tokens!
bot_token="TOKEN_GOES_HERE"
statcord_token="TOKE_GOES_HERE"

# User defines
my_twitch_url="PUT_TWITCH_URL_HERE!"

# music stuff related
RURL = re.compile("https?:\/\/(?:www\.)?.+")

# client setup
class Bot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    # on_ready
    async def on_ready(self):
        logo = Figlet(font="slant")
        print(colored(logo.renderText("OneFileChallenge"), "green"))

        # logging to console! :)
        logging.basicConfig(level=logging.INFO)
        logging.info(f"Logged in as {client.user}")

client = Bot(
    command_prefix=commands.when_mentioned_or("$"),
    description="A bot made for a youtube challenge: make the best discord bot in one file!",
    intents=discord.Intents.all(),
    case_insensitive=True,
    help_command=None
)

# psutil proess tracking
client.process = psutil.Process(os.getpid())

# Statcord support
api = statcord.Client(client, token=statcord_token)


# change_presence(status)
async def change_presence():
    await client.wait_until_ready()

    # statuses
    statuses = [f"{len(client.guilds)} servers", f"{len(client.users)} members"]

    while not client.is_closed():
        status=random.choice(statuses)
        await client.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.watching, name=status))
        await asyncio.sleep(10)

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

# Cog General
class General(commands.Cog):
    """General Commands"""

    # Ping
    @commands.command(
        name="ping",
        brief="Shows client latency",
        help="use this command to see how fast ur internnnnnet can go brrrrr!",
        aliases=["p"]
    )
    async def _ping(self, context):
        embed=discord.Embed(
            title="Pong!",
            description=f"Pong! `{round(client.latency * 1000)}ms`",
            colour=discord.Colour.greyple()
        )
        await context.reply(
            embed=embed,
            mention_author=False
        )

    # Invite
    @commands.command(
        name="invite",
        brief="Invite the bot to your server!",
        help="Use this command to invite the bot to your server :)",
        aliases=["inv"]
    )
    async def _invite(self, context):
        await context.reply(
            f"https://discordapp.com/api/oauth2/authorize?client_id={client.user.id}&permissions=8&scope=bot", 
            mention_author=False
        )
    

    # Uptime
    @commands.command(
        name="uptime",
        brief="Shows the bot's uptime",
        help="Use this command to see the bot's uptime :)",
        aliases=["upt", "u"]
    )
    async def _uptime(self, context):
        current_time = time.time()
        difference = int(round(current_time - start_time))
        uptime = str(timedelta(seconds=difference))

        embed = discord.Embed(
            title="Uptime",
            description=f"Uptime: `{uptime}`",
            colour=discord.Colour.greyple()
        )
        
        await context.reply(
            embed=embed,
            mention_author=False
        )

    # Info
    @commands.command(
        name="info",
        brief="Shows everything about the bot in a nice embed.",
        help="Use this command to see everything about the bot :)",
        aliases=["inf", "i"]
    )
    async def _info(self, context):
        before = time.monotonic()
        before_ws = int(round(client.latency * 1000, 1))
        ping = (time.monotonic() - before) * 1000
        ram_usage = client.process.memory_full_info().rss / 1024**2
        current_time = time.time()
        difference = int(round(current_time - start_time))
        uptime = str(timedelta(seconds=difference))
        users = len(client.users)

        info = discord.Embed(
        title="Bot Info",
        description="Everything about me!",
        colour=discord.Colour.greyple()
        )
        info.set_thumbnail(
            url=context.bot.user.avatar_url
        )
        fields = [
            ("Developer", "Timmy", True), 
            ("Users", f"{users}", True),
            ("Latency", f"{before_ws}ms", True),
            ("RAM Usage", f"{ram_usage:.2f} MB", True), 
            ("Uptime", uptime, True), 
        ]

        info.set_footer(
            text="View my statistics :)"
        )

        for name, value, inline in fields:
            info.add_field(name=name, value=value, inline=inline)

        await context.reply(
            embed=info,
            mention_author=False
        )

    # userinfo
    @commands.command(
        name="userinfo",
        brief="displays info about a user.",
        help="use this command to display some info about a user :)",
        aliases=["ui", "usrinf"]
    )
    async def userinfo(self, context, user: discord.Member=None):

        if isinstance(context.channel, discord.DMChannel):
            return

        if user is None:
            user = context.author 

        embed = discord.Embed(
            colour=discord.Colour.greyple()
        )
        embed.set_author(
            name=str(user), 
            icon_url=user.avatar_url
        )
        
        perm_string = ', '.join([str(p[0]).replace("_", " ").title() for p in user.guild_permissions if p[1]])
        members = sorted(context.guild.members, key=lambda m: m.joined_at)
        date_format = "%a, %d %b %Y at %I:%M %p"

        top_role = user.top_role
        
        fields = [("Joined this server at", user.joined_at.strftime(date_format), True),
                  ("Registered this account at", user.created_at.strftime(date_format), False),
                  ("Server join position", str(members.index(user)+1), True),
                  ("Roles [{}]".format(len(user.roles)-1), top_role.mention, True)]
        
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)

        embed.set_footer(
            text="ID: " + str(user.id)
        )
        await context.reply(
            embed=embed,
            mention_author=False
        )

    # Serverinfo
    @commands.command(
        name="serverinfo",
        brief="Displays server info.",
        help="Use this command to display info about a server :)",
        aliases=["si", "srvrinf"]
    )
    async def serverinfo(self, context):

        embed = discord.Embed(
        title="Server Info",
        colour=discord.Colour.greyple()
        )
        embed.set_thumbnail(
            url=context.guild.icon_url
        )

        fields = [("Owner", context.guild.owner, False),
                  ("Created At", context.guild.created_at.strftime("%d/%m/%Y %H:%M:%S"), True),
                  ("Region", context.guild.region, False),
                  ("Members", len(context.guild.members), False)]

        for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)

        embed.set_footer(
            text=f"ID: {context.guild.id}"
        )

        await context.reply(
            embed=embed,
            mention_author=False
        )

class Help(commands.Cog):
    """ Help Command """

    # The actual help command lul
    @commands.command(
        name="help",
        brief="Shows client latency",
        help="Use this command to see all the other commands :)",
        aliases=["h", "hlp"]
    )
    async def _help(self, context):

        # PAGE 1
        page_1 = discord.Embed(
            title="General Commands!",
            description="Help for everyday commands.",
            colour=discord.Colour.greyple()
        )
        fields=[
            ("$help", "Shows this help message.", False),
            ("$ping", "Shows client latency.", False),
            ("$invite", "Invite the bot to your server.", False),
            ("$uptime", "Shows the bot's uptime.", False), 
            ("$info", "Shows the bot's stats in one nice embed", False)
        ]
        page_1.set_footer(
            text="Page 1 of 5"
        )
        for name, value, inline in fields:
            page_1.add_field(
                name=name,
                value=value,
                inline=inline
            )

        # PAGE 2
        page_2 = discord.Embed(
            title="Moderation",
            description="Help for moderation commands.",
            colour=discord.Colour.greyple()
        )
        fields=[
            ("$kick", "Kicks a user from the server.", False),
            ("$ban", "Bans a user from the server.", False),
            ("$mute", "Mutes a user.", False),
            ("$unmute", "Unmutes a user.", False),
            ("$clear", "Deletes a number of messages.", False)
        ]
        page_2.set_footer(
            text="Page 2 of 5"
        )
        for name, value, inline in fields:
            page_2.add_field(
                name=name,
                value=value,
                inline=inline
            )

        # PAGE 3
        page_3 = discord.Embed(
            title="Fun",
            description="Help for fun commands.",
            colour=discord.Colour.greyple()
        )
        fields=[
            ("$8ball", "Ask the magic 8ball a question.", False),
            ("$coinflip", "Flip a coin.", False),
            ("$roll", "Roll a dice.", False),
            ("$slots", "Play slots.", False),
            ("$poll", "Create a poll.", False)
        ]   
        page_3.set_footer(
            text="Page 3 of 5"
        )
        for name, value, inline in fields:
            page_3.add_field(
                name=name,
                value=value,
                inline=inline
            )

        # PAGE 4
        page_4 = discord.Embed(
            name="Music",
            description="Help for music commands.",
            colour=discord.Colour.greyple()
        )
        fields=[
            ("$connect", "Connects to a voice channel.", False),
            ("$disconnect", "Disconnects from the voice channel.", False),
            ("$play", "Play a song.", False),
            ("$pause", "Pause the current song.", False),
            ("$resume", "Resume the current song.", False)
        ]
        page_4.set_footer(
            text="Page 4 of 5"
        )
        for name, value, inline in fields:
            page_4.add_field(
                name=name,
                value=value,
                inline=inline
            )

        # pagination stuff
        message = await context.send(embed=page_1)
        await message.add_reaction("◀️")
        await message.add_reaction("▶️")
        await message.add_reaction("❌")
        pages = 4
        current_page = 1

        def check(reaction, user):
            return user == context.author and str(reaction.emoji) in ["◀️", "▶️", "❌"]

        while True:
            try:
                reaction, user = await context.bot.wait_for("reaction_add", timeout=60, check=check)

                if str(reaction.emoji) == "▶️" and current_page != pages:
                    current_page += 1

                    if current_page == 2:
                        await message.edit(embed=page_2)
                        await message.remove_reaction(reaction, user)
                    
                    elif current_page == 3:
                        await message.edit(embed=page_3)
                        await message.remove_reaction(reaction, user)

                    elif current_page == 4:
                        await message.edit(embed=page_4)
                        await message.remove_reaction(reaction, user)
                
                if str(reaction.emoji) == "◀️" and current_page > 1:
                    current_page -= 1
                    
                    if current_page == 1:
                        await message.edit(embed=page_1)
                        await message.remove_reaction(reaction, user)

                    elif current_page == 2:
                        await message.edit(embed=page_2)
                        await message.remove_reaction(reaction, user)
                    
                    elif current_page == 3:
                        await message.edit(embed=page_3)
                        await message.remove_reaction(reaction, user)

                    elif current_page == 4:
                        await message.edit(embed=page_4)
                        await message.remove_reaction(reaction, user)

                    elif current_page == 5:
                        await message.edit(embed=page_5)
                        await message.remove_reaction(reaction, user)

                if str(reaction.emoji) == "❌":
                    await message.delete()
                    break

                else:
                    await message.remove_reaction(reaction, user)
                    
            except asyncio.TimeoutError:
                await message.delete()
                break

class Moderation(commands.Cog):
    """ Moderation """

    # clear
    @commands.has_permissions(manage_messages=True)
    @commands.command(
        name="clear",
        brief="Clear an amount of messages in a channel",
        help="Use this command to clear a specific amount of messages.",
        aliases=["clr", "c"]
    )
    async def _clear(self, context, amount: int):
        await context.message.delete()
        await context.channel.purge(limit=amount)   

    # kick
    @commands.has_permissions(kick_members=True)
    @commands.command(
        name="kick",
        brief="Kick a user from the server",
        help="Use this command to kick a user from the server.",
        aliases=["k"]
    )
    async def _kick(self, context, member: discord.Member, *, reason=None):
        kick_server= discord.Embed(
            colour = discord.Colour.greyple(),
            title = f"{context.author} kicked {member.name}!",
            description = f"**Reason:** {reason}\n**By:** {context.author.mention}",
        )
        kick_private = discord.Embed(
            colour = discord.Colour.greyple(),
            title = f"Oh no! You were kicked by {context.author}!",
            description = f"**Reason:** {reason}\n"
        )
    
        await context.channel.send(embed=kick_server)
        await member.send(embed=kick_private)
        await member.kick(reason=reason)
    
    # ban
    @commands.has_permissions(ban_members=True)
    @commands.command(
        name="ban",
        brief="Ban a user from the server",
        help="Use this command to ban a user from the server.",
        aliases=["b"]
    )
    async def _ban(self, context, member: discord.Member, *, reason=None):
        ban_server= discord.Embed(
            colour = discord.Colour.greyple(),
            title = f"{context.author} banned {member.name}!",
            description = f"**Reason:** {reason}\n**By:** {context.author.mention}",
        )
        ban_private = discord.Embed(
            colour = discord.Colour.greyple(),
            title = f"Oh no! You were banned by {context.author}!",
            description = f"**Reason:** {reason}\n"
        )
    
        await context.channel.send(embed=ban_server)
        await member.send(embed=ban_private)
        await member.ban(reason=reason)

    # unban
    @commands.has_permissions(ban_members=True)
    @commands.command(
        name="unban",
        brief="Unban a user from the server",
        help="Use this command to unban a member from the server",
        aliases=["ub"]
    )
    async def _unban(self, context, *, member):
        banned_users = await context.guild.bans()
        member_name, member_discriminator = member.split("#")

        for ban_entry in banned_users:
            user = ban_entry.user

            if (user.name, user.discriminator) == (member_name, member_discriminator):
                await context.guild.unban(user)
                embed = discord.Embed(
                    title = f"{context.author} unbanned {user.name}#{user.discriminator}!",
                    colour = discord.Colour.greyple()
                )
                await context.reply(
                    embed=embed,
                    mention_author=False
                )
    # mute
    @commands.has_permissions(manage_roles=True)
    @commands.command(
        name="mute",
        brief="Mute a member for reasons...",
        help="Use this command to mute someone for some reason.",
        aliases=["m", "mt"]
    )
    async def _mute(self, context, member: discord.Member, *, reason=None):
        mute_role = discord.utils.get(context.guild.roles, name="Muted")
        mute_server= discord.Embed(
            colour = discord.Colour.greyple(),
            title = f"{context.author} muted {member.name}!",
            description = f"**Reason:** {reason}\n**By:** {context.author.mention}",
        )
        mute_private = discord.Embed(
            colour = discord.Colour.greyple(),
            title = f"Oh no! You were muted by {context.author}!",
            description = f"**Reason:** {reason}\n"
        )
    
        await context.channel.send(embed=mute_server)
        await member.send(embed=mute_private)
        await member.add_roles(mute_role)

    # unmute
    @commands.has_permissions(manage_roles=True)
    @commands.command(
        name="unmute",
        brief="Unmute a member for reasons",
        help="Use this command to unumte someone for some reason.",
        aliases=["um", "umt"]
    )
    async def _unmute(self, context, member: discord.Member):
        mute_role = discord.utils.get(context.guild.roles, name="Muted")
        unmute_server= discord.Embed(
            colour = discord.Colour.greyple(),
            title = f"{context.author} unmuted {member.name}!",
            description = f"**By:** {context.author.mention}",
        )
        unmute_private = discord.Embed(
            colour = discord.Colour.greyple(),
            title = f"Oh no! You were unmuted by {context.author}!",
            description = f""
        )
    
        await context.channel.send(embed=unmute_server)
        await member.send(embed=unmute_private)
        await member.remove_roles(mute_role)

class Fun(commands.Cog):
    """ MUCH FUN!!! """

    #8ball
    @commands.command(
        name="8ball",
        brief="Ask the magic 8ball a question!",
        help="Use this command to have some fun!",
        aliases=["8", "8b"]
    )
    async def _8ball(self, context, *, question):
        responses = [
            "It is certain.",
            "It is decidedly so.",
            "Without a doubt.",
            "Yes - definitely.",
            "You may rely on it.",
            "As I see it, yes.",
            "Most likely.",
            "Outlook good.",
            "Yes.",
            "Signs point to yes.",
            "Reply hazy, try again.",
            "Ask again later.",
            "Better not tell you now.",
            "Cannot predict now.",
            "Concentrate and ask again.",
            "Don't count on it.",
            "My reply is no.",
            "My sources say no.",
            "Outlook not so good.",
            "Very doubtful.",
        ]
        embed = discord.Embed(
            title = ":8ball: 8ball",
            description = f"Question: {question}\nAnswer: {random.choice(responses)}",
            colour = discord.Colour.greyple()
        )
        await context.reply(
            embed=embed,
            mention_author=False
        )

    # coinflip
    @commands.command(
        name="coinflip",
        brief="heads or tails?",
        help="use this command to have some fun",
        aliases=["cf", "flip"]
    )
    async def _coinflip(self, context):
        responses = [
            "heads",
            "tails"
        ]
        embed = discord.Embed(
            title = ":coin: Coinflip",
            description = f"You got {random.choice(responses)}!",
            colour = discord.Colour.greyple()
        )
        await context.reply(
            embed=embed,
            mention_author=False
        )

    # roll
    @commands.command(
        name="roll",
        brief="Roll a dice",
        help="Use this command to roll a dice",
        aliases=["rll"]
    )
    async def _roll(self, context):
        responses = [
            "1",
            "2",
            "3",
            "4",
            "5",
            "6"
        ]
        embed = discord.Embed(
            title = ":game_die: Roll",
            description = f"You got {random.choice(responses)}!",
            colour = discord.Colour.greyple()
        )
        await context.reply(
            embed=embed,
            mention_author=False
        )

    # slots
    @commands.command(
        name="slots",
        brief="Play slots",
        help="Use this command to play slots",
        aliases=["slt"]
    )
    async def _slots(self, context):
        responses = [
            ":cherries:",
            ":banana:",
            ":apple:",
            ":lemon:",
            ":grapes:",
            ":watermelon:",
            ":tangerine:",
            ":peach:",
            ":pineapple:",
            ":strawberry:",
            ":tomato:",
            ":eggplant:",
            ":corn:"
        ]
        embed = discord.Embed(
            title = ":slot_machine: Slots",
            description = f"{random.choice(responses)} {random.choice(responses)} {random.choice(responses)}",
            colour = discord.Colour.greyple()
        )
        await context.reply(
            embed=embed,
            mention_author=False
        )

    # poll
    @commands.command(
        name="poll",
        brief="Create a poll",
        help="Use this command to create a poll",
        aliases=["pl"]
    )
    async def _poll(self, context, question):
        
        embed = discord.Embed(
            title = ":pencil: Poll",
            description = f"{question}",
            colour = discord.Colour.greyple()
        )
        message = await context.reply(
            embed=embed,
            mention_author=False
        )
        await message.add_reaction("👍")
        await message.add_reaction("👎")

# cheeky copypaste for music :)
class Music(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        if not hasattr(bot, 'wavelink'):
            self.bot.wavelink = wavelink.Client(bot=client)

        self.bot.loop.create_task(self.start_nodes())

    async def start_nodes(self):
        await self.bot.wait_until_ready()

        # Initiate our nodes. For this example we will use one server.
        # Region should be a discord.py guild.region e.g sydney or us_central (Though this is not technically required)
        await self.bot.wavelink.initiate_node(
            host="ip_here",
            port=2333,
            rest_uri="uri_here",
            password="passwd_here",
            identifier="TEST",
            region="us_central"
        )

    # connect
    @commands.command(
        name="connect",
        brief="Connect to a voice channel",
        help="Use this command to connect to a voice channel",
        aliases=["cnct"]
    )
    async def connect_(self, context, *, channel: discord.VoiceChannel = None):
        if not channel:
            try:
                channel = context.author.voice.channel
            except AttributeError:
                raise discord.DiscordException("No channel to join. Please either specify a valid channel or join one.")

        player = self.bot.wavelink.get_player(context.guild.id)
        await context.reply(
            f"Connecting to **`{channel.name}`**",
            mention_author=False
        )
        await player.connect(channel.id)

    # disconnect
    @commands.command(
        name="disconnect",
        brief="Disconnect from a voice channel",
        help="Use this command to disconnect from a voice channel",
        aliases=["dscnct"]
    )
    async def disconnect_(self, context):
        player = self.bot.wavelink.get_player(context.guild.id)
        await context.reply(
            f"Disconnecting from **`{player.channel_id}`**",
            mention_author=False
        )
        await player.disconnect()

    # play
    @commands.command(
        name="play",
        brief="Play a song",
        help="Use this command to play a song",
        aliases=["yt"]
    )
    async def play(self, context, *, query: str):
        tracks = await self.bot.wavelink.get_tracks(f"ytsearch:{query}")

        if not tracks:
            return await context.send("Could not find any songs with that query.")

        player = self.bot.wavelink.get_player(context.guild.id)
        if not player.is_connected:
            await context.invoke(self.connect_)

        await context.send(f"Added {str(tracks[0])} to the queue.")
        await player.play(tracks[0])

    # pause
    @commands.command(
        name="pause",
        brief="Pause the current song",
        help="Use this command to pause the current song",
        aliases=["pauz"]
    )
    async def _pause(self, context):
        player = self.bot.wavelink.get_player(context.guild.id)
        await player.set_pause(True)

    # resume
    @commands.command(
        name="resume",
        brief="Resume the current song",
        help="Use this command to resume the current song",
        aliases=["rsme"]
    )
    async def _resume(self, context):
        player = self.bot.wavelink.get_player(context.guild.id)
        await player.set_pause(False)    

# run function
def run():
    client.add_cog(Admin(client))
    client.add_cog(General(client))
    client.add_cog(Help(client))
    client.add_cog(Fun(client))
    client.add_cog(Music(client))

    client.loop.create_task(change_presence())
    client.run(bot_token)

if __name__ == "__main__":
    run()