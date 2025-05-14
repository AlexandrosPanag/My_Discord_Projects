import discord
from discord.ext import commands
import os

import discord
from discord.ext import commands
import random
import os

intents = discord.Intents.default()
intents.message_content = True  # Needed to read message content

bot = commands.Bot(command_prefix="!", intents=intents)

#DEBUGGING
@bot.event
async def on_ready():
    print(f"Bot is ready! Logged in as {bot.user}")

#D4 ROLL COMMAND
@bot.command()
async def d4(ctx):
    """Roll a 4-sided die."""
    roll = random.randint(1, 4)
    await ctx.send(f"🎲 You rolled a d4: {roll}")

#D6 ROLL COMMAND
@bot.command()
async def d6(ctx):
    """Roll a 6-sided die."""
    roll = random.randint(1, 6)
    await ctx.send(f"🎲 You rolled a d6: {roll}")


#D8 COMMAND
@bot.command()
async def d8(ctx):
    """Roll an 8-sided die."""
    roll = random.randint(1, 8)
    await ctx.send(f"🎲 You rolled a d8: {roll}")

#D10 COMMAND
@bot.command()
async def d10(ctx):
    """Roll a 10-sided die."""
    roll = random.randint(1, 10)
    await ctx.send(f"🎲 You rolled a d10: {roll}")

#D12 COMMAND    
@bot.command()
async def d12(ctx):
    """Roll a 12-sided die."""
    roll = random.randint(1, 12)
    await ctx.send(f"🎲 You rolled a d12: {roll}")

#D20 COMMAND
@bot.command()
async def d20(ctx):
    """Roll a 20-sided die."""
    roll = random.randint(1, 20)
    await ctx.send(f"🎲 You rolled a d20: {roll}")

#D100 COMMAND
@bot.command()
async def d100(ctx):
    """Roll a 100-sided die."""
    roll = random.randint(1, 100)
    await ctx.send(f"🎲 You rolled a d100: {roll}")


@bot.command()
async def createparty(ctx, *members: discord.Member):
    """
    Create a party and import each member's character stats from a .txt file.
    Usage: !createparty @user1 @user2 ...
    Each user's character file should contain classic DND stats (e.g., Strength, Dexterity, Constitution, Intelligence, Wisdom, Charisma).
    """
    party = []
    stat_names = ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"]
    for member in members:
        filename = f"{member.id}.txt"
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                character = f.read()
            # Parse stats from file (expects lines like "Strength: 15")
            stats = {}
            for line in character.splitlines():
                for stat in stat_names:
                    if line.lower().startswith(stat.lower()):
                        try:
                            value = int(line.split(":")[1].strip())
                            stats[stat] = value
                        except Exception:
                            pass
            # Fill missing stats with "N/A"
            for stat in stat_names:
                if stat not in stats:
                    stats[stat] = "N/A"
            party.append((member.display_name, stats))
        else:
            await ctx.send(f"❌ Character file for {member.display_name} not found ({filename}).")
            return
    # Save party to a file, showing stats
    party_file = "party.txt"
    with open(party_file, "w", encoding="utf-8") as f:
        for name, stats in party:
            f.write(f"=== {name} ===\n")
            for stat in stat_names:
                f.write(f"{stat}: {stats[stat]}\n")
            f.write("\n")
    await ctx.send(f"✅ Party created with {len(party)} members. Party stats saved to `{party_file}`.")

#REMOVE PARTY COMMAND
@bot.command()
async def removeparty(ctx, member: discord.Member):
    """
    Remove a member from the party file.
    Usage: !removeparty @user
    """
    party_file = "party.txt"
    if not os.path.exists(party_file):
        await ctx.send("No party file found.")
        return
    with open(party_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
    new_lines = []
    skip = False
    for line in lines:
        if line.startswith(f"=== {member.display_name} ==="):
            skip = True
            continue
        if skip and line.startswith("==="):
            skip = False
        if not skip:
            new_lines.append(line)
    with open(party_file, "w", encoding="utf-8") as f:
        f.writelines(new_lines)
    await ctx.send(f"🗑️ Removed {member.display_name} from the party.")

#MODIFY PARTY COMMAND
@bot.command()
async def modifyparty(ctx, member: discord.Member, *, new_character: str):
    """
    Modify a party member's character in the party file.
    Usage: !modifyparty @user <new character info>
    """
    party_file = "party.txt"
    if not os.path.exists(party_file):
        await ctx.send("No party file found.")
        return
    with open(party_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
    new_lines = []
    skip = False
    for line in lines:
        if line.startswith(f"=== {member.display_name} ==="):
            skip = True
            new_lines.append(line)
            new_lines.append(new_character + "\n")
            continue
        if skip and line.startswith("==="):
            skip = False
        if not skip:
            new_lines.append(line)
    with open(party_file, "w", encoding="utf-8") as f:
        f.writelines(new_lines)
    await ctx.send(f"✏️ Modified {member.display_name}'s character in the party.")

#ACTIVE PARTY COMMAND
@bot.command()
async def activeparty(ctx):
    """
    Display all current party members and their stats from the party.txt file, with emojis.
    Usage: !activeparty
    """
    party_file = "party.txt"
    if not os.path.exists(party_file):
        await ctx.send("No party file found. Use !createparty to make one.")
        return

    # Emoji mapping for stats
    stat_emojis = {
        "Strength": "💪",
        "Dexterity": "🤸",
        "Constitution": "❤️",
        "Intelligence": "🧠",
        "Wisdom": "🦉",
        "Charisma": "🗣️"
    }

    with open(party_file, "r", encoding="utf-8") as f:
        content = f.read().strip()

    if not content:
        await ctx.send("The party is empty!")
        return

    members = content.split("=== ")
    embed = discord.Embed(title="🧙 Active Party Members", color=discord.Color.purple())
    for member in members:
        if not member.strip():
            continue
        lines = member.strip().splitlines()
        name = lines[0].replace("===", "").strip()
        stats = lines[1:]
        stat_lines = []
        for stat_line in stats:
            if ":" in stat_line:
                stat, value = stat_line.split(":", 1)
                stat = stat.strip()
                value = value.strip()
                emoji = stat_emojis.get(stat, "")
                stat_lines.append(f"{emoji} **{stat}:** {value}")
        embed.add_field(name=name, value="\n".join(stat_lines), inline=False)

    await ctx.send(embed=embed)

#HELP COMMAND
@bot.command()
async def helpdungeonmaster(ctx):
    """
    Show all available DungeonMaster bot commands.
    Usage: !helpdungeonmaster
    """
    help_text = (
        "🧙 **DungeonMaster Bot Commands:**\n"
        "🎲 Dice Rolls:\n"
        "  `!d4`, `!d6`, `!d8`, `!d10`, `!d12`, `!d20`, `!d100`\n"
        "🧑‍🤝‍🧑 Party Management:\n"
        "  `!createparty @user1 @user2 ...` — Import party from character .txt files\n"
        "  `!removeparty @user` — Remove a member from the party\n"
        "  `!modifyparty @user <new character info>` — Modify a member's character\n"
        "  `!activeparty` — Show all current party members and stats\n"
        "👹 Monster Database:\n"
        "  `!createmonster <name> <stats>` — Add a monster (e.g. !createmonster Goblin HP:7 ATK:2 DEF:1)\n"
        "  `!showmonsters` — Display all monsters\n"
        "  `!monsterattack <name>` — Simulate a monster attack (with miss/crit chance)\n"
        "📜 Other:\n"
        "  `!license` — Show bot license info\n"
        "  `!helpdungeonmaster` — Show this help message\n"
    )
    await ctx.send(help_text)

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

# Replace 'YOUR_BOT_TOKEN' with your actual bot token
bot.run('')
