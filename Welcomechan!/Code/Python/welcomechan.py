#created by Alexandros Panagiotakopoulos - alexandrospanag.github.io

import discord
import asyncio
import random
from discord.ext import commands
from discord.ext.commands import CommandOnCooldown
from discord.ext.commands import cooldown, BucketType
import json
import os
import time
import collections

intents = discord.Intents.default()
intents.message_content = True
intents.members = True  
intents.presences = True  

bot = commands.Bot(command_prefix="!", intents=intents)
MAIN_SERVER_IDS = {1351673459545079949, 1363628187988529172}
BLACKLISTED_USER_ID = 1018898299421466674

@bot.check
async def globally_block_if_not_in_main_servers(ctx):
    # Block blacklisted user from all commands
    if ctx.author.id == BLACKLISTED_USER_ID:
        await ctx.send(f"{ctx.author.mention}, you have been blacklisted by the mod author.")
        return False
    # Only allow commands if the user is a member of at least one main server
    if ctx.guild and ctx.guild.id in MAIN_SERVER_IDS:
        return True
    # If in DM or another server, check if user is in any main server
    for guild in bot.guilds:
        if guild.id in MAIN_SERVER_IDS and guild.get_member(ctx.author.id):
            return True
    return False

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


CONTRIB_FILE = "contributions.json"

def load_contributions():
    if os.path.exists(CONTRIB_FILE):
        with open(CONTRIB_FILE, "r") as f:
            return json.load(f)
    return {}

def save_contributions(data):
    with open(CONTRIB_FILE, "w") as f:
        json.dump(data, f)

# Add at the top, after your other file constants:
LAST_ACTIVE_FILE = "last_active.json"

def load_last_active():
    if os.path.exists(LAST_ACTIVE_FILE):
        with open(LAST_ACTIVE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_last_active(data):
    with open(LAST_ACTIVE_FILE, "w") as f:
        json.dump(data, f)

@bot.command(name="devsetlevel")
async def devsetlevel(ctx, member: discord.Member = None, level: int = 1):
    """
    Developer-only: Test the level up embed for any user (default: yourself, level 1).
    Usage: !devsetlevel [@user] [level]
    Only works for the bot owner.
    """
    if ctx.author.id != 1342637991335821352:
        await ctx.send("You are not authorized to use this command.")
        return

    member = member or ctx.author
    await send_levelup_embed(ctx.channel, member, level)
    await ctx.send(f"[DEV] Level up embed sent for {member.display_name} at level {level}.")

@bot.command(name="devlevelup")
async def devlevelup(ctx, member: discord.Member = None, levels: int = 1):
    """
    Developer-only: Instantly level up any user by the specified number of levels.
    Usage: !devlevelup [@user] [levels]
    Only works for the bot owner.
    """
    if ctx.author.id != 1342637991335821352:
        await ctx.send("You are not authorized to use this command.")
        return

    member = member or ctx.author
    
    if levels < 1:
        await ctx.send("Please specify a positive number of levels to add.")
        return
    
    user_id = str(member.id)
    old_points = contributions.get(user_id, 0)
    old_level = get_level(old_points)
    
    # Calculate target level and required points
    target_level = old_level + levels
    required_points = (target_level ** 2) * 100
    
    # Add the points needed to reach the target level
    contributions[user_id] = required_points
    save_contributions(contributions)
    
    # Trigger level up messages for each level gained
    for lvl in range(old_level + 1, target_level + 1):
        await send_levelup_embed(ctx.channel, member, lvl)
    
    await ctx.send(f"[DEV] {member.display_name} has been leveled up by {levels} level(s)! "
                   f"Old level: {old_level}, New level: {target_level} ({required_points} points)")

# Initialize last_active from file
last_active = load_last_active()

contributions = load_contributions()

MAIN_SERVER_ID = 1351673459545079949  # Replace with your actual server ID

async def send_levelup_embed(channel, member, level):
    embed = discord.Embed(
        title="🎉 Level Up! 🎉",
        description=f"{member.mention} has reached **Level {level}**!",
        color=discord.Color.gold()
    )
    if member.avatar:
        embed.set_thumbnail(url=member.avatar.url)
    else:
        embed.set_thumbnail(url=member.default_avatar.url)
    embed.add_field(name="Congratulations!", value="Keep up the great work!", inline=False)
    embed.set_footer(text="WelcomeChan Level System")
    await channel.send(embed=embed)

    
# ...existing code...

def add_contribution(user_id, amount, channel=None):
    # Only increase contributions if the action is in the main server
    if channel and hasattr(channel, "guild") and channel.guild and channel.guild.id != MAIN_SERVER_ID:
        return
    user_id = str(user_id)
    amount = amount * 3  # x3 experience for every contribution
    old_points = contributions.get(user_id, 0)
    old_level = get_level(old_points)
    contributions[user_id] = old_points + amount
    save_contributions(contributions)
    new_level = get_level(contributions[user_id])
    if new_level > old_level:
        print(f"Level up! {user_id} from {old_level} to {new_level}")
        for lvl in range(old_level + 1, new_level + 1):
            for guild in bot.guilds:
                if guild.id != MAIN_SERVER_ID:
                    continue
                member = guild.get_member(int(user_id))
                if member:
                    target_channel = channel
                    if not target_channel:
                        for c in guild.text_channels:
                            if c.permissions_for(member).read_messages and c.permissions_for(guild.me).send_messages:
                                target_channel = c
                                break
                        if not target_channel:
                            target_channel = guild.system_channel or next((c for c in guild.text_channels if c.permissions_for(guild.me).send_messages), None)
                    if target_channel:
                        print(f"Sending congrats to {target_channel.name} for level {lvl}")
                        asyncio.create_task(send_levelup_embed(target_channel, member, lvl))
                    break

# Function to calculate level based on points 
def get_level(points):
    # Exponential level curve: Level = int((points / 100) ** 0.5)
    # Level 1: 100 pts, Level 2: 400 pts, Level 3: 900 pts, Level 4: 1600 pts, etc.
    return int((points / 100) ** 0.5)


@bot.command()
async def consolefunfact(ctx):
    """Send a random fun fact about retro consoles! Usage: !consolefunfact"""
    facts = [
        "🎮 The original PlayStation was originally planned as a collaboration between Sony and Nintendo!",
        "🕹️ The Sega Dreamcast was the first console to include a built-in modem for online play.",
        "📼 The Nintendo 64 was named after its 64-bit processor, which was a big deal at the time!",
        "💾 The original Xbox controller was nicknamed 'The Duke' because of its large size.",
        "🧃 The Game Boy could survive being run over by a military tank and still work!",
        "🦄 The SNES (Super Nintendo) had a special chip in some cartridges to boost graphics and performance.",
        "🌈 The Atari 2600 was originally called the Atari VCS (Video Computer System).",
        "🦩 The Sega Genesis was known as the Mega Drive outside North America.",
        "🌴 The NES Zapper (light gun) only works on CRT TVs, not modern flatscreens!",
        "💿 The GameCube used mini optical discs instead of standard DVDs."
    ]
    await ctx.send(random.choice(facts))

@bot.command()
@cooldown(1, 100, BucketType.user)  # 1 use per 100 seconds per user
async def hug(ctx, member: discord.Member = None):
    """Hug a user with a wholesome gif! Usage: !hug @user (100s cooldown)"""
    hug_gifs = [
        "https://media.giphy.com/media/l2QDM9Jnim1YVILXa/giphy.gif",
        "https://media.giphy.com/media/od5H3PmEG5EVq/giphy.gif",
        "https://media.giphy.com/media/143v0Z4767T15e/giphy.gif",
        "https://media.giphy.com/media/wnsgren9NtITS/giphy.gif",
        "https://media.giphy.com/media/PHZ7v9tfQu0o0/giphy.gif",
        "https://media.giphy.com/media/3ZnBrkqoaI2hq/giphy.gif",
        "https://media.giphy.com/media/5eyhBKLvYhafu/giphy.gif"
    ]
    gif = random.choice(hug_gifs)
    if member:
        await ctx.send(f"{member.mention} just got a hug from {ctx.author.mention}! 🤗\n{gif}")
    else:
        await ctx.send(f"{ctx.author.mention} sends a big hug to everyone! 🤗\n{gif}")      

RETROGAME_SCORE_FILE = "retrogame_scores.json"

def load_retrogame_scores():
    if os.path.exists(RETROGAME_SCORE_FILE):
        with open(RETROGAME_SCORE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_retrogame_scores(scores):
    with open(RETROGAME_SCORE_FILE, "w") as f:
        json.dump(scores, f)

retrogame_scores = load_retrogame_scores()


  
@bot.command()
@cooldown(1, 60, BucketType.user)
async def retrogamequiz(ctx):
    """
    Play a Retro Quiz! Usage: !retrogamequiz
    """
    questions = [
        {
            "question": "Which company created the original Game Boy?",
            "choices": ["A) Sega", "B) Nintendo", "C) Sony", "D) Atari"],
            "answer": "b"
        },
        {
            "question": "What was the first home video game console?",
            "choices": ["A) Atari 2600", "B) NES", "C) Magnavox Odyssey", "D) ColecoVision"],
            "answer": "c"
        },
        {
            "question": "Which console is famous for its 'Ring of Death' error?",
            "choices": ["A) PlayStation 2", "B) Xbox 360", "C) Dreamcast", "D) SNES"],
            "answer": "b"
        },
        {
            "question": "Which handheld console used interchangeable 'Game Paks'?",
            "choices": ["A) Game Gear", "B) Game Boy", "C) PSP", "D) Neo Geo Pocket"],
            "answer": "b"
        },
        {
            "question": "Which company made the Dreamcast?",
            "choices": ["A) Sony", "B) Sega", "C) Nintendo", "D) Atari"],
            "answer": "b"
        },
        {
            "question": "What was the name of the first PlayStation mascot?",
            "choices": ["A) Mario", "B) Crash Bandicoot", "C) Sonic", "D) Donkey Kong"],
            "answer": "b"
        },
        {
            "question": "Which console introduced the first analog stick on a controller?",
            "choices": ["A) PlayStation", "B) Nintendo 64", "C) Atari 2600", "D) Sega Genesis"],
            "answer": "b"
        },
        {
            "question": "Which console was known for its 'Mode 7' graphics?",
            "choices": ["A) SNES", "B) NES", "C) Sega Saturn", "D) PlayStation"],
            "answer": "a"
        },
        {
            "question": "Which company created the Atari 2600?",
            "choices": ["A) Atari", "B) Nintendo", "C) Sega", "D) Sony"],
            "answer": "a"
        },
        {
            "question": "What color was the original Game Boy?",
            "choices": ["A) Red", "B) Green", "C) Gray", "D) Blue"],
            "answer": "c"
        },
        {
            "question": "Which console was the first to use CDs as its primary media?",
            "choices": ["A) PlayStation", "B) Sega Saturn", "C) 3DO", "D) SNES"],
            "answer": "c"
        },
        {
            "question": "Which company developed the Neo Geo console?",
            "choices": ["A) SNK", "B) Sega", "C) Nintendo", "D) Sony"],
            "answer": "a"
        },
        {
            "question": "Which console had the game 'Sonic the Hedgehog' as its mascot?",
            "choices": ["A) SNES", "B) Sega Genesis", "C) NES", "D) PlayStation"],
            "answer": "b"
        },
        {
            "question": "What was the first Nintendo console to support online play?",
            "choices": ["A) GameCube", "B) Wii", "C) NES", "D) SNES"],
            "answer": "a"
        },
        {
            "question": "Which console featured the game 'GoldenEye 007'?",
            "choices": ["A) PlayStation", "B) Nintendo 64", "C) Sega Saturn", "D) Dreamcast"],
            "answer": "b"
        },
        {
            "question": "Which company created the TurboGrafx-16?",
            "choices": ["A) NEC", "B) Sega", "C) Nintendo", "D) Sony"],
            "answer": "a"
        },
        {
            "question": "Which console was known for its VMU (Visual Memory Unit)?",
            "choices": ["A) Dreamcast", "B) PlayStation", "C) GameCube", "D) Xbox"],
            "answer": "a"
        },
        {
            "question": "Which console had the 'Power Glove' accessory?",
            "choices": ["A) NES", "B) SNES", "C) Sega Genesis", "D) Atari 2600"],
            "answer": "a"
        },
        {
            "question": "Which company made the handheld 'Lynx' console?",
            "choices": ["A) Atari", "B) Sega", "C) Nintendo", "D) SNK"],
            "answer": "a"
        },
        {
            "question": "Which console was bundled with 'Super Mario World'?",
            "choices": ["A) NES", "B) SNES", "C) N64", "D) GameCube"],
            "answer": "b"
        },
           {
            "question": "Which rare NES game is considered the 'Holy Grail' for collectors, sometimes selling for over $100,000?",
            "choices": ["A) Stadium Events", "B) DuckTales 2", "C) Little Samson", "D) Bubble Bobble Part 2"],
            "answer": "a"
        },
        {
            "question": "What was the codename for the Nintendo 64 during its development?",
            "choices": ["A) Project Reality", "B) Ultra 64", "C) Dolphin", "D) Revolution"],
            "answer": "a"
        },
        {
            "question": "Which Sega console featured a built-in TV tuner as an official accessory (in Japan)?",
            "choices": ["A) Game Gear", "B) Master System", "C) Saturn", "D) Dreamcast"],
            "answer": "a"
        },
        {
            "question": "Which arcade game was the first to feature a 'continue' option after losing all lives?",
            "choices": ["A) Double Dragon", "B) Gauntlet", "C) Pac-Man", "D) Donkey Kong"],
            "answer": "b"
        },
        {
            "question": "What was the name of the failed add-on for the SNES that was later reworked into the original PlayStation?",
            "choices": ["A) Satellaview", "B) Super FX", "C) Play Station", "D) 32X"],
            "answer": "c"
        },
        
    ]
    score = 0
    for q in questions:
        await ctx.send(f"🕹️ **Retro Quiz!**\n{q['question']}\n" + "\n".join(q["choices"]) + "\nType A, B, C, or D.")
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel and not m.author.bot
        try:
            msg = await bot.wait_for('message', timeout=20.0, check=check)
            if msg.content.lower().strip() == q["answer"]:
                await ctx.send("✅ Correct!")
                score += 1
            else:
                await ctx.send(f"❌ Wrong! The correct answer was {q['answer'].upper()}.")
        except asyncio.TimeoutError:
            await ctx.send("⏰ Time's up for this question!")

    # Purge up to 999 messages before printing the high score
    try:
        await ctx.channel.purge(limit=999)
    except Exception as e:
        await ctx.send(f"Could not purge messages: {e}")

    # Now print only the score and high score messages
    await ctx.send(f"🏁 Quiz finished! Your score: {score}/{len(questions)}")

    # Save high score if it's higher than previous
    user_id = str(ctx.author.id)
    prev = retrogame_scores.get(user_id, 0)
    if score > prev:
        retrogame_scores[user_id] = score
        save_retrogame_scores(retrogame_scores)
        await ctx.send(f"🌟 New personal high score! ({score})")
    elif score == len(questions) and prev < len(questions):
        retrogame_scores[user_id] = score
        save_retrogame_scores(retrogame_scores)
        await ctx.send(f"🏆 Perfect score! Well done!")


 
@bot.command()
@cooldown(1, 3000, BucketType.user)
async def leaderboard(ctx):
    """
    Show the top 10 contributors by overall activity.
    Usage: !leaderboard
    Only works in the main server.
    """
    if ctx.author.id != 1342637991335821352:
        await ctx.send("This command is restricted to the bot owner due to spam.")
        return
    if ctx.guild.id != 1351673459545079949:
        await ctx.send("This command can only be used in the main server.")
        return

    data = contributions
    valid_ids = {str(member.id) for member in ctx.guild.members}
    removed = False
    for uid in list(data.keys()):
        if uid not in valid_ids:
            del data[uid]
            removed = True
    if removed:
        save_contributions(data)
    top = sorted(data.items(), key=lambda x: x[1], reverse=True)[:10]
    if not top:
        await ctx.send("No contributions yet!")
        return

    embed = discord.Embed(
        title="🏆 Top 10 Contributors",
        description="Here are the most active members!",
        color=discord.Color.blue()
    )
    for i, (uid, points) in enumerate(top, 1):
        member = ctx.guild.get_member(int(uid))
        name = member.display_name if member else f"User {uid}"
        level = get_level(points)
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"`#{i}`"
        embed.add_field(
            name=f"{medal} {name}",
            value=f"Points: **{points}** | Level: **{level}**",
            inline=False
        )
    await ctx.send(embed=embed)

@bot.command()
@cooldown(1, 7200, BucketType.user)
async def leaderboardmax(ctx):
    """
    Show the top 35 contributors by overall activity.
    Usage: !leaderboardmax
    """
    if ctx.author.id != 1342637991335821352:
        await ctx.send("This command is restricted to the bot owner due to spam. Use '!checkmylevel' instead.")
        return
    data = contributions
    valid_ids = {str(member.id) for member in ctx.guild.members}
    removed = False
    for uid in list(data.keys()):
        if uid not in valid_ids:
            del data[uid]
            removed = True
    if removed:
        save_contributions(data)
    top = sorted(data.items(), key=lambda x: x[1], reverse=True)[:35]
    if not top:
        await ctx.send("No contributions yet!")
        return

    embed = discord.Embed(
        title="🏆 Top 35 Contributors",
        description="The most dedicated members of all time!",
        color=discord.Color.purple()
    )
    for i, (uid, points) in enumerate(top, 1):
        member = ctx.guild.get_member(int(uid))
        name = member.display_name if member else f"User {uid}"
        level = get_level(points)
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"`#{i}`"
        embed.add_field(
            name=f"{medal} {name}",
            value=f"Points: **{points}** | Level: **{level}**",
            inline=False
        )
        # Discord embed field limit: 25 fields
        if (i % 25 == 0 or i == len(top)):
            await ctx.send(embed=embed)
            embed = discord.Embed(
                title="🏆 Top 35 Contributors (cont'd)",
                color=discord.Color.purple()
            )
    # If not sent in the loop, send the last chunk
    if len(top) % 25 != 0:
        await ctx.send(embed=embed)


# Check your own level command
@bot.command(name="checkmylevel")
async def checkmylevel(ctx):
    """
    Show your own contribution points and level.
    Usage: !checkmylevel
    """
    user_id = str(ctx.author.id)
    # Use the in-memory contributions variable instead of loading from disk
    points = contributions.get(user_id, 0)
    level = get_level(points)
    await ctx.send(f"{ctx.author.mention}, you have {points} contribution points (Level {level})!")


@bot.event
async def on_reaction_add(reaction, user):
    if not user.bot:
        add_contribution(user.id, 1)  # +1 point per reaction


# Keep these as your in-memory cache
contributions = load_contributions()


# PAT COMMAND ---------------------------------------------------
@bot.command()
async def pat(ctx, member: discord.Member):
    """Pat a user with a wholesome gif! Usage: !pat @user"""
    pat_gifs = [
        "https://media.giphy.com/media/ARSp9T7wwxNcs/giphy.gif",
        "https://media.giphy.com/media/109ltuoSQT212w/giphy.gif",
        "https://media.giphy.com/media/ye7OTQgwmVuVy/giphy.gif",
        "https://media.giphy.com/media/L2z7dnOduqEow/giphy.gif",
        "https://media.giphy.com/media/4HP0ddZnNVvKU/giphy.gif"
    ]
    gif = random.choice(pat_gifs)
    await ctx.send(f"{member.mention} has been patted by {ctx.author.mention}! 🤗\n{gif}")

# EASTER EGG COMMAND ---------------------------------------------------
@bot.command()
async def easteregg(ctx):
    """
    Sends a fun gif referencing a famous computer easter egg or bug.
    Usage: !easteregg
    """
    # "The first computer bug" - the moth in the relay
    gif_url = "https://media.giphy.com/media/3o7TKtnuHOHHUjR38Y/giphy.gif"
    await ctx.send(
        "Did you know? The first computer 'bug' was an actual moth found in a relay in 1947! 🪲\n"
        f"{gif_url}"
    )

# LICENSE COMMAND ---------------------------------------------------
@bot.command()
async def license(ctx):
    """
    Show the bot's license information.
    Usage: !license
    """
    await ctx.send(
        "📝 **License:**\n"
        "This bot is licensed under the [Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)](https://creativecommons.org/licenses/by-nc-sa/4.0/) license.\n"
        "You are free to share and adapt the bot for non-commercial purposes, as long as you give appropriate credit and share alike.\n"
        "For commercial use or to purchase rights, please contact the author via GitHub: @alexandrospanag"
    )

# DEBUGGING COMMAND ---------------------------------------------------
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}!")

# CAT COMMAND ---------------------------------------------------
@bot.command()
async def cat(ctx):
    cat_gifs = [
        "https://media.giphy.com/media/JIX9t2j0ZTN9S/giphy.gif",
        "https://media.giphy.com/media/mlvseq9yvZhba/giphy.gif",
        "https://media.giphy.com/media/13borq7Zo2kulO/giphy.gif",
        "https://media.giphy.com/media/v6aOjy0Qo1fIA/giphy.gif",
        "https://media.giphy.com/media/3oriO0OEd9QIDdllqo/giphy.gif",
    ]
    await ctx.send(random.choice(cat_gifs))

# DOGGO COMMANDS ---------------------------------------------------
@bot.command()
async def doggo(ctx):
    """Sends a random gif of a dog! Usage: !doggo"""
    doggo_gifs = [
       "https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExd2hwcHRqOG1sdzRyODBmdm5ra2d5d25pNHoyaGkxeng2cG1kdDNqeCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/FTJfA8RiHaOfS/giphy.gif",
       "https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExMTVhZnNtam9saWQ3MHZ6ZmJ5cGE4bWo4ZGdlNDVqdDdncmttNXQyYyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/nQ8XtX3ctBCkE/giphy.gif",
        "https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExNzNpajB3dnQ4b21jMmR5c25xcnQ1YzBmeWpzMXdqYzg0NDBhc3plMCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/Z3aQVJ78mmLyo/giphy.gif",
        "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNWUzOWozd3lsYmNmOWxpNTIwcDhzNXRqa2I0MThxcGl4MWlma2U2YSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/ngzhAbaGP1ovS/giphy.gif",
        "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNWUzOWozd3lsYmNmOWxpNTIwcDhzNXRqa2I0MThxcGl4MWlma2U2YSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/ngzhAbaGP1ovS/giphy.gif",
        "https://media.giphy.com/media/cYZkY9HeKgofpQnOUl/giphy.gif?cid=ecf05e47lbcxpnq73rywfgrefu8in9kw2v3vdelfw4vm20dk&ep=v1_gifs_related&rid=giphy.gif&ct=g"
    ]
    await ctx.send(random.choice(doggo_gifs))

# KICK COMMAND ---------------------------------------------------
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

# COUNTING CHEAT COMMAND ---------------------------------------------------         
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

    skipped_numbers = ', '.join(str(i) for i in range(counting_state["current"] + 1, number + 1))
    if skipped_numbers:
        await ctx.send(f"Skipping numbers: {skipped_numbers}")

    counting_state["current"] = number
    counting_state["last_user"] = None
    save_counting_state(counting_state)
    await ctx.send(f"Counting has been skipped to {number}. The next number is {number + 1}!")

# PURGE COMMAND -------------------------------------------------------------------
@bot.command()
@commands.has_permissions(manage_messages=True)
async def purge(ctx, amount: int):
    if amount < 1 or amount > 999:
        await ctx.send("Please specify an amount between 1 and 999.")
        return
    deleted = await ctx.channel.purge(limit=amount + 1)  # +1 to include the command message
    await ctx.send(f"Deleted {len(deleted)-1} messages.", delete_after=3)

# MOD POST COMMAND -------------------------------------------------------------------
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

# COUNTING GAME COMMAND -------------------------------------------------------------------
@bot.command()
async def counting(ctx):
    counting_state["channel_id"] = ctx.channel.id
    counting_state["current"] = 0
    counting_state["last_user"] = None
    save_counting_state(counting_state)
    await ctx.send("Counting game started! The next number is 1.")

# BONK COMMAND -----------------------------------------------------------------------------------------------------------------------------------
@bot.command()
async def bonk(ctx, member: discord.Member = None):
    """Bonk a user with a funny gif! Usage: !bonk @user"""
    bonk_gif = "https://media.tenor.com/2roX3uxz_68AAAAC/cat-bonk.gif"
    if member:
        await ctx.send(f"{member.mention} has been bonked! {bonk_gif}")
    else:
        await ctx.send(f"Bonk! {bonk_gif}")


# PUN COMMAND -----------------------------------------------------------------------------------------------------------------------------------
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
        "Parallel lines have so much in common. It’s a shame they’ll never meet.",
        "Why did the golfer bring two pairs of pants? In case he got a hole in one.",
        "I told my computer I needed a break, and now it won’t stop sending me KitKats.",
        "Why did the tomato turn red? Because it saw the salad dressing!",
        "What do you call cheese that isn't yours? Nacho cheese!",
        "Why did the math book look sad? Because it had too many problems.",
        "How does a penguin build its house? Igloos it together.",
        "Why don’t eggs tell jokes? They’d crack each other up.",
        "What do you call a factory that makes good products? A satisfactory.",
        "Why did the coffee file a police report? It got mugged!"
        "Why did the chicken join a band? Because it had the drumsticks!",
        "Why don’t scientists trust atoms? Because they make up everything.",
        "Why did the computer go to the doctor? Because it had a virus!",
        "Why did the stadium get hot after the game? All the fans left.",
        "Why did the picture go to jail? Because it was framed.",
        "Why did the cookie go to the hospital? Because it felt crummy.",
        "Why did the scarecrow get promoted? Because he was outstanding in his field.",
        "Why did the bicycle stand up by itself? It was two-tired.",
        "Why did the golfer bring an extra shirt? In case he got a hole in one.",
        "Why did the orange stop? It ran out of juice.",
        "Why did the frog take the bus to work? His car got toad.",
        "Why did the music teacher need a ladder? To reach the high notes.",
        "Why did the bee get married? Because he found his honey.",
        "Why did the man put his money in the freezer? He wanted cold hard cash.",
        "Why did the banana go to the doctor? Because it wasn’t peeling well.",
        "Why did the computer show up at work late? It had a hard drive.",
        "Why did the grape stop in the middle of the road? It ran out of juice.",
        "Why did the math teacher look so sad? Because she had too many problems.",
        "Why did the skeleton go to the party alone? He had no body to go with him.",
        "Why did the tomato turn red? Because it saw the salad dressing.",
        "Why did the fish blush? Because it saw the ocean’s bottom.",
        "Why did the cow win an award? Because he was outstanding in his field.",
        "Why did the barber win the race? Because he took a short cut.",
        "Why did the bicycle fall over? Because it was two-tired.",
        "Why did the golfer bring two pairs of pants? In case he got a hole in one.",
        "Why did the chicken cross the playground? To get to the other slide.",
        "Why did the scarecrow win an award? Because he was outstanding in his field.",
        "Why did the student eat his homework? Because his teacher told him it was a piece of cake.",
        "Why did the computer go to art school? To learn how to draw its curtains.",
    ]
    await ctx.send(random.choice(puns))


@bot.command()
@commands.has_permissions(administrator=True)
async def setconc(ctx, member: discord.Member, level: int):
    """
    Set a user's level and trigger the congrats message for debugging.
    Usage: !setconc @user <level>
    Only works for the bot owner.
    """
    # Only allow the command for your Discord user ID
    if ctx.author.id != 1342637991335821352:
        await ctx.send("You are not authorized to use this command.")
        return

    if level < 0:
        await ctx.send("Level must be non-negative.")
        return

    user_id = str(member.id)
    old_points = contributions.get(user_id, 0)
    old_level = get_level(old_points)
    # Set points to the minimum needed for the desired level
    points = (level ** 2) * 100
    contributions[user_id] = points
    save_contributions(contributions)
    new_level = get_level(points)
    if new_level > old_level:
        # Always send congrats in the channel where the command was used
        await ctx.send(f"🎉 {member.mention} congratulations! You leveled up to level {new_level}!")
    await ctx.send(f"{member.mention}'s level set to {new_level} ({points} points).")





@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason: str = "No reason provided"):
    """
    Ban a member from the server. Usage: !ban @user [reason]
    """
    # Prevent banning yourself or the bot
    if member == ctx.author:
        await ctx.send("You can't ban yourself!")
        return
    if member == ctx.guild.me:
        await ctx.send("I can't ban myself!")
        return
    # Prevent banning mods/admins
    if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
        await ctx.send("You can't ban this user because they have a role equal to or higher than yours.")
        return
    if member.guild_permissions.ban_members or member.guild_permissions.administrator:
        await ctx.send("You can't ban another moderator or admin!")
        return
    try:
        await member.ban(reason=reason)
        await ctx.send(f"{member.mention} has been banned. Reason: {reason}")
    except Exception as e:
        await ctx.send(f"Failed to ban {member.mention}: {e}")


# USERINFO COMMAND -----------------------------------------------------------------------------------------------------------------------------------
@bot.command()
@cooldown(1, 30, BucketType.user)  # 1 use per 30 seconds per user
async def guessnumber(ctx):
    """
    Start a number guessing game! Usage: !guessnumber
    The bot will pick a number between 1 and 100. You have 7 tries to guess it.
    """
    number = random.randint(1, 100)
    max_attempts = 7
    await ctx.send("🎲 I'm thinking of a number between 1 and 100. You have 7 tries! Reply with your guess.")

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel and not m.author.bot

    for attempt in range(1, max_attempts + 1):
        try:
            msg = await bot.wait_for('message', timeout=30.0, check=check)
            try:
                guess = int(msg.content.strip())
            except ValueError:
                await ctx.send("❗ Please enter a valid number.")
                continue

            if guess == number:
                await ctx.send(f"🎉 Correct, {ctx.author.mention}! The number was {number}. You guessed it in {attempt} tries!")
                return
            elif guess < number:
                await ctx.send("🔼 Too low!")
            else:
                await ctx.send("🔽 Too high!")
        except asyncio.TimeoutError:
            await ctx.send(f"⏰ Time's up! The number was {number}.")
            return

    await ctx.send(f"❌ Out of tries! The number was {number}. Better luck next time, {ctx.author.mention}!")



# USERINFO COMMAND -----------------------------------------------------------------------------------------------------------------------------------
@bot.command()
async def userinfo(ctx, member: discord.Member = None):
    """
    Show information about a user.
    Usage: !userinfo [@user]
    """
    member = member or ctx.author
    roles = [role.name for role in member.roles if role.name != "@everyone"]
    embed = discord.Embed(
        title=f"User Info: {member.display_name}",
        color=discord.Color.blue()
    )
    embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
    embed.add_field(name="Username", value=f"{member}", inline=True)
    embed.add_field(name="ID", value=member.id, inline=True)
    embed.add_field(name="Joined Server", value=member.joined_at.strftime("%Y-%m-%d %H:%M"), inline=False)
    embed.add_field(name="Account Created", value=member.created_at.strftime("%Y-%m-%d %H:%M"), inline=False)
    embed.add_field(name="Roles", value=", ".join(roles) if roles else "None", inline=False)
    embed.add_field(name="Top Role", value=member.top_role.name, inline=True)
    embed.add_field(name="Bot?", value="Yes" if member.bot else "No", inline=True)
    await ctx.send(embed=embed)

@bot.command()
@cooldown(1, 10, BucketType.user)  # 1 use per 10 seconds per user
async def slap(ctx, member: discord.Member = None):
    """Slap a user with a funny anime gif! Usage: !slap @user"""
    slap_gifs = [
        "https://media.giphy.com/media/Gf3AUz3eBNbTW/giphy.gif",
        "https://media.giphy.com/media/jLeyZWgtwgr2U/giphy.gif",
        "https://media.giphy.com/media/Zau0yrl17uzdK/giphy.gif",
        "https://media.giphy.com/media/3XlEk2RxPS1m8/giphy.gif",
        "https://media.giphy.com/media/mEtSQlxqBtWWA/giphy.gif",
        "https://media.giphy.com/media/81kHQ5v9zbqzC/giphy.gif",
        "https://media.giphy.com/media/9U5J7JpaYBr68/giphy.gif"
    ]
    gif = random.choice(slap_gifs)
    if member:
        await ctx.send(f"{member.mention} just got slapped by {ctx.author.mention}! 🤚\n{gif}")
    else:
        await ctx.send(f"{ctx.author.mention} slaps the air! 🤚\n{gif}")

# 8BALL COMMAND -----------------------------------------------------------------------------------------------------------------------------------
@bot.command(name="8ball", aliases=["eightball"])
@cooldown(1, 300, BucketType.user)  # 1 use per 5 minutes per user
async def eight_ball(ctx, *, question: str = None):
    """
    Ask the magic 8-ball a question.
    Usage: !8ball Will I win the lottery?
    """
    responses = [
        "It is certain.", "It is decidedly so.", "Without a doubt.",
        "Yes – definitely.", "You may rely on it.", "As I see it, yes.",
        "Most likely.", "Outlook good.", "Yes.", "Signs point to yes.",
        "Reply hazy, try again.", "Ask again later.", "Better not tell you now.",
        "Cannot predict now.", "Concentrate and ask again.",
        "Don't count on it.", "My reply is no.", "My sources say no.",
        "Outlook not so good.", "Very doubtful."
    ]
    if not question:
        await ctx.send("🎱 Please ask a question, e.g. `!8ball Will I win the lottery?`")
        return
    answer = random.choice(responses)
    await ctx.send(f"🎱 Question: {question}\nAnswer: {answer}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    last_active[str(message.author.id)] = time.time()
    save_last_active(last_active)
    is_command = message.content.startswith("!")
    is_counting = (
        counting_state["channel_id"] == message.channel.id
        and not message.author.bot
    )
    if is_command and message.guild and message.guild.id == MAIN_SERVER_ID:
        add_contribution(message.author.id, 1, channel=message.channel)
    if is_counting:
        try:
            number = int(message.content.strip())
        except ValueError:
            await bot.process_commands(message)
            return
        expected = counting_state["current"] + 1
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
    await bot.process_commands(message)

# LURKERS COMMAND -----------------------------------------------------------------------------------------------------------------------------------
@bot.command()
@commands.has_permissions(administrator=True)
async def showlurkers(ctx):
    """
    Show members who joined more than 16 days ago and have not sent a message in the last 16 days.
    Usage: !showlurkers
    """
    from datetime import datetime, timedelta, timezone
    now = datetime.now(timezone.utc)
    threshold = now - timedelta(days=16)
    lurkers = []
    for member in ctx.guild.members:
        if member.bot:
            continue
        if member.joined_at and member.joined_at < threshold:
            last = last_active.get(str(member.id), 0)
            # If never active or last active >16 days ago
            if last == 0 or (time.time() - last) > 16 * 24 * 3600:
                lurkers.append(f"{member.mention} (joined {member.joined_at.strftime('%Y-%m-%d')})")
    if lurkers:
        await ctx.send("👀 **Inactive members (joined >16 days ago, no recent messages):**\n" + "\n".join(lurkers))
    else:
        await ctx.send("No inactive members found!")

@bot.command(name="retrogameleaderboard")
async def retrogameleaderboard(ctx):
    """
    Show the top 5 high scores for the retrogame quiz.
    Usage: !retrogameleaderboard
    """
    if not retrogame_scores:
        await ctx.send("No retrogame scores yet!")
        return
    # Sort by score, descending, and take top 5
    top = sorted(retrogame_scores.items(), key=lambda x: x[1], reverse=True)[:5]
    lines = []
    for i, (uid, score) in enumerate(top, 1):
        member = ctx.guild.get_member(int(uid))
        name = member.display_name if member else f"User {uid}"
        lines.append(f"**{i}. {name}** — {score} pts")
    await ctx.send("🏅 **Retrogame Quiz Top 5:**\n" + "\n".join(lines))

#CREDIT COMMAND
@bot.command()
async def credits(ctx):
    await ctx.send("Bot credits: Made by @alexandrospanag on GitHub!")
@bot.command(name="helpwc", aliases=["helpwelcomechan", "helpchan", "welpwchan"])
@cooldown(1, 7200, BucketType.user)  # 1 use per 2 hours per user
async def helpwc(ctx):
    help_text = (
        "✨ **WelcomeChan Commands:** ✨\n"
        "😺 `!cat` — Sends a random cat gif\n"
        "🐶 `!doggo` — Sends a random dog gif\n"
        "🤪 `!pun` — Get a random pun\n"
        "🪓 `!bonk @user` — Bonk a user with a funny gif\n"
        "🏅 `!credits` — Bot credits\n"
        "🪲 `!easteregg` — Fun computer history fact\n"
        "🤗 `!pat @user` — Pat a user with a wholesome gif\n"
        "🤗 `!hug @user` — Hug a user with a wholesome gif\n"
        "✋ `!slap @user` — Slap a user with a funny anime gif\n"
        "🎱 `!8ball <question>` — Ask the magic 8-ball a question\n"
        "🔢 Counting: `!counting`, `!skipcount <n>`\n"
        "🏆 Leaderboards: `!leaderboard` (top 10), `!leaderboardmax` (top 35), `!checkmylevel` (your contribution)\n"
        "🧑‍💻 `!userinfo [@user]` — Show info about a user\n"
        "🧠 `!guessnumber` — Solo number guessing game\n"
        "🎮 `!retrogamequiz` — Play a retro multiple-choice quiz game!\n"
        "🏅 `!retrogameleaderboard` — See the top scores for the retro quiz!\n"
        "🎮 `!consolefunfact` — Posts a fun fact about retro consoles\n"
        "\n"
        "🎲 **Truth or Dare:**\n"
        "`!completed @user`, `!incompleted @user`\n"
        "\n"
        "📝 **License:**\n"
        "`!license` — Shows the bot's license (CC BY-NC-SA 4.0). For commercial use or to purchase rights, contact @alexandrospanag on GitHub.\n"
        "\n"
        "🔧 **Admin Tools:**\n"
        "🧹 `!purge <n>` — Delete messages in bulk\n"
        "📝 `!modpost <id> <msg>` — Post a message as the bot in any channel by ID\n"
        "👢 `!kick @user [reason]` — Kick a user from the server\n"
        "🔨 `!ban @user [reason]` — Ban a user from the server\n"
        "👀 `!showlurkers` — Show users inactive for >16 days\n"
        "🛠️ `!devsetlevel [@user] [level]` — Test the level up embed (owner only)\n"
        "🛠️ `!devlevelup [@user] [levels]` — Instantly level up any user (owner only)\n"
        "\n"
    )
    await ctx.send(help_text)

# Replace 'YOUR_TOKEN_HERE' with your bot token
bot.run('')
