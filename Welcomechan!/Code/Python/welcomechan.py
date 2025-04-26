#code written by @alexandrospanag on GitHub
# This bot is a simple Discord bot that includes various commands for fun and moderation.
# It includes a counting game, a pun generator, and the ability to kick members with certain permissions.
# The bot also has a command to send random cat gifs and a command to roll dice.
# It uses JSON to persist the counting game state across bot restarts.
# The bot is designed to be user-friendly and includes error handling for various commands.  
# Copyright (c) 2025 @alexandrospanag
# LICENSE: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# This means you can share and adapt the work, but not for commercial purposes, and you must give appropriate credit.


import discord
from discord.ext import commands
import json
import os

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Counting game state persistence
COUNTING_FILE = "counting_state.json"

def load_counting_state():
    if os.path.exists(COUNTING_FILE):
        with open(COUNTING_FILE, "r") as f:
            return json.load(f)
    return {"channel_id": None, "current": 0, "last_user": None}

def save_counting_state(state):
    with open(COUNTING_FILE, "w") as f:
        json.dump(state, f)

counting_state = load_counting_state()

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}!")

@bot.command()
async def cat(ctx):
    cat_gifs = [
        "https://media.giphy.com/media/JIX9t2j0ZTN9S/giphy.gif",
        "https://media.giphy.com/media/mlvseq9yvZhba/giphy.gif",
        "https://media.giphy.com/media/13borq7Zo2kulO/giphy.gif",
        "https://media.giphy.com/media/v6aOjy0Qo1fIA/giphy.gif",
        "https://media.giphy.com/media/3oriO0OEd9QIDdllqo/giphy.gif",
    ]
    import random
    await ctx.send(random.choice(cat_gifs))

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason: str = "No reason provided"):
    """Kick a member from the server. Usage: !kick @user [reason]"""
    # Prevent kicking yourself or the bot
    if member == ctx.author:
        await ctx.send("You can't kick yourself!")
        return
    if member == ctx.guild.me:
        await ctx.send("I can't kick myself!")
        return
    # Prevent kicking mods/admins
    if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
        await ctx.send("You can't kick this user because they have a role equal to or higher than yours.")
        return
    if member.guild_permissions.kick_members or member.guild_permissions.administrator:
        await ctx.send("You can't kick another moderator or admin!")
        return
    try:
        await member.kick(reason=reason)
        await ctx.send(f"{member.mention} has been kicked. Reason: {reason}")
    except Exception as e:
        await ctx.send(f"Failed to kick {member.mention}: {e}")
        
@bot.command()
async def skipcount(ctx, number: int):
    """
    Skip the counting to a specific number. The bot will announce the skipped numbers,
    and the next user must say number+1 to continue.
    Usage: !skipcount 20
    """
    if number < 1:
        await ctx.send("Please provide a number greater than 0.")
        return

    if counting_state["channel_id"] != ctx.channel.id:
        await ctx.send("Counting is not set up in this channel. Use !counting to set it up.")
        return

    # Announce the skipped numbers
    skipped_numbers = ', '.join(str(i) for i in range(counting_state["current"] + 1, number + 1))
    if skipped_numbers:
        await ctx.send(f"Skipping numbers: {skipped_numbers}")

    counting_state["current"] = number
    counting_state["last_user"] = None
    save_counting_state(counting_state)
    await ctx.send(f"Counting has been skipped to {number}. The next number is {number + 1}!")

@bot.command()
async def hi(ctx):
    await ctx.send(f"Hi, {ctx.author.display_name}! UwU!")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def purge(ctx, amount: int):
    if amount < 1 or amount > 100:
        await ctx.send("Please specify an amount between 1 and 100.")
        return
    deleted = await ctx.channel.purge(limit=amount + 1)  # +1 to include the command message
    await ctx.send(f"Deleted {len(deleted)-1} messages.", delete_after=3)

@bot.command()
@commands.has_permissions(manage_messages=True)
async def modpost(ctx, channel_id: int, *, message: str):
    """Post a message as the bot in any channel by ID (mods and above only)."""
    channel = bot.get_channel(channel_id)
    if channel is None:
        await ctx.send("Channel not found. Please provide a valid channel ID.")
        return
    await channel.send(message)
    await ctx.send(f"Message sent to <#{channel_id}>.")


@bot.command()
async def pun(ctx):
    puns = [
        "I'm reading a book on anti-gravity. It's impossible to put down!",
        "Did you hear about the mathematician who’s afraid of negative numbers? He’ll stop at nothing to avoid them.",
        "Why don’t skeletons fight each other? They don’t have the guts.",
        "I would tell you a joke about construction, but I’m still working on it.",
        "Why did the scarecrow win an award? Because he was outstanding in his field!",
        "I used to play piano by ear, but now I use my hands.",
        "What do you call fake spaghetti? An impasta!",
        "Why did the bicycle fall over? Because it was two-tired!",
        "I’m on a seafood diet. I see food and I eat it.",
        "Why can’t you hear a pterodactyl go to the bathroom? Because the ‘P’ is silent.",
    ]
    import random
    await ctx.send(random.choice(puns))

@bot.command()
async def dice(ctx):
    import random
    roll = random.randint(1, 6)
    await ctx.send(f"You rolled a {roll}!")

@bot.command()
async def credits(ctx):
    await ctx.send("Bot credits: Made by @alexandrospanag on GitHub!")


@bot.command()
async def doubledice(ctx):
    import random
    roll1 = random.randint(1, 6)
    roll2 = random.randint(1, 6)
    await ctx.send(f"You rolled: {roll1} and {roll2}!")



@bot.command(name="helpwelcomechan")
async def helpwelcomechan(ctx):
    help_text = (
        "**WelcomeChan Bot Commands:**\n"
        "`!cat` - Sends a random cat gif.\n"
        "`!hi` - The bot greets you back.\n"
        "`!purge <amount>` - Deletes the specified number of recent messages in this channel (requires Manage Messages permission).\n"
        "`!modpost <channel_id> <message>` - Post a message as the bot in any channel by ID (requires Manage Messages permission).\n"
        "`!pun` - Sends a random pun.\n"
        "`!dice` - Rolls a six-sided dice (1-6).\n"
        "`!counting` - Sets up a counting game in the current channel. The bot will keep track of the count even if it restarts.\n"
        "`!bonk [@user]` - Bonk a user with a funny gif. If no user is mentioned, bonks the channel.\n"
        "\n"
        "To use `!modpost`, you need the channel ID. Enable Developer Mode in Discord settings to copy channel IDs."
    )
    await ctx.send(help_text)

@bot.event
async def on_message(message):
    await bot.process_commands(message)
    if (
        counting_state["channel_id"] == message.channel.id
        and not message.author.bot
    ):
        expected = counting_state["current"] + 1
        try:
            number = int(message.content.strip())
        except ValueError:
            return
        if number == expected and message.author.id != counting_state["last_user"]:
            counting_state["current"] += 1
            counting_state["last_user"] = message.author.id
            save_counting_state(counting_state)
            await message.add_reaction("✅")
        else:
            await message.channel.send(
                f"❌ {message.author.mention} ruined the count at {counting_state['current']}. The next number is 1."
            )
            counting_state["current"] = 0
            counting_state["last_user"] = None
            save_counting_state(counting_state)

# Replace 'YOUR_TOKEN_HERE' with your bot token
bot.run('')