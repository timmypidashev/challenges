import discord
from discord.ext import commands
from pyfiglet import Figlet
import psutil
import os
import sys
from discord_slash import SlashCommand
from termcolor import colored
import asyncio
import statcord
import logging
import random
import time
from datetime import datetime, timedelta

# start_time
start_time = time.time()

# tokens!
bot_token="ODc4MDc1OTI3ODYxNTU1MjAx.YR757w.bqDsy2YjAT13dVWPt41UZk-LHpE"
statcord_token="statcord.com-zO5ROpxYMgvP0tv35NbI"

# User defines
my_twitch_url="PUT_TWITCH_URL_HERE!"

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

    # statuses
    statuses = [f"{len(client.guilds)} servers", f"{len(client.users)} members"]

    while not client.is_closed():
        status=random.choice(statuses)
        await client.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.watching, name=status))
        await asyncio.sleep(10)


# on_ready 
@client.event
async def on_ready():
    logo = Figlet(font="slant")
    print(colored(logo.renderText("OneFileChallenge"), "green"))

    # logging to console! :)
    logging.basicConfig(level=logging.INFO)
    logging.info(f"Logged in as {client.user}")

    # eh uhm yea ill see what i can add l8r

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

    # Help
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
            ("$poll", "Create a poll.", False),
            ("$nitro", "Create a nitro giveaway!", False),
            ("$timer", "Create a timer.", False),
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
            ("$play", "Play a song.", False),
            ("$skip", "Skip the current song.", False),
            ("$pause", "Pause the current song.", False),
            ("$resume", "Resume the current song.", False),
            ("$queue", "Show the current queue.", False),
            ("$volume", "Change the volume.", False),
            ("$np", "Show the current song.", False),
            ("$leave", "Leave the voice channel.", False),
            ("$join", "Join the voice channel.", False),
            ("$loop", "Toggle looping.", False),
            ("$shuffle", "Shuffle the queue.", False),
            ("$search", "Search for a song.", False)
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

        # PAGE 5
        page_5 = discord.Embed(
            name="Levelling",
            description="Discord exp system.",
            colour=discord.Colour.greyple()
        )
        fields=[
            ("$rank", "Show your current rank.", False),
            ("$leaderboard", "Show the top users", False),
        ]
        page_5.set_footer(
            text="Page 5 of 5"
        )
        for name, value, inline in fields:
            page_5.add_field(
                name=name,
                value=value,
                inline=inline
            )

        # pagination stuff
        message = await context.send(embed=page_1)
        await message.add_reaction("◀️")
        await message.add_reaction("▶️")
        await message.add_reaction("❌")
        pages = 5
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

                    elif current_page == 5:
                        await message.edit(embed=page_5)
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

# run function
def run():
    client.add_cog(Admin(client))
    client.add_cog(General(client))
    client.loop.create_task(change_presence())
    client.run(bot_token)

if __name__ == "__main__":
    run()