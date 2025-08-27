import discord
import asyncio
import random
import re
from discord.ext import commands
from discord.ext.commands import CommandOnCooldown
from discord.ext.commands import cooldown, BucketType
import json
import os
import time
import collections
import datetime
import requests
import logging
import traceback
from typing import Optional, Dict, Any, List

# IMPORTS - Real functionality
from bot_utils import roast_command, praise_command, dadjoke_command, send_achievement_notification, ShopHelper, WeeklyContributionManager, ChatterBot, SHOP_ROLES as BOT_UTILS_SHOP_ROLES
from achievements import (
    AchievementSystem, achievement_system, 
    check_counting_achievements, check_special_achievements,
    check_message_achievements, check_gaming_achievements,
    check_social_achievements, check_command_achievements,
    check_time_achievements, check_milestone_achievements,
    send_achievement_notification,
    debug_check_time_achievements, debug_check_message_achievements,
    debug_check_social_achievements, debug_check_milestone_achievements,
    debug_check_easy_achievements
)

# Create combined shop roles dictionary
SHOP_ROLES = BOT_UTILS_SHOP_ROLES.copy()
# Add legacy roles for backward compatibility
SHOP_ROLES.update({
    "Bronze Supporter": {"price": 2000, "description": "Basic supporter role", "rarity": "Common", "emoji": "🥉"},
    "Silver Supporter": {"price": 5000, "description": "Silver supporter role", "rarity": "Common", "emoji": "🥈"},
    "Gold Supporter": {"price": 10000, "description": "Gold supporter role", "rarity": "Rare", "emoji": "🥇"},
    "Platinum Supporter": {"price": 20000, "description": "Platinum supporter role", "rarity": "Epic", "emoji": "💎"}
})


# Basic logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('starchan_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('StarChan')

# Discord intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True  
intents.presences = True  

bot = commands.Bot(command_prefix="!", intents=intents)

# BOT CONFIGURATIONS - PLACEHOLDER VALUES FOR OPEN SOURCE
# Replace these with your actual server/channel/user IDs when deploying
MAIN_SERVER_IDS = [000000000000000000]  # Replace with your server ID
BOT_CONFIG = {
    "MAIN_SERVER_IDS": MAIN_SERVER_IDS,
    "main_server_id": 000000000000000000,  # Replace with your primary server ID
    "PREFIX": "!",
    "VERSION": "1.0.0",
    "owner_id": 000000000000000000,  # Replace with your Discord user ID
    "VIP_ROLE_NAME": "⚜️ VIP ⚜️"
}

# GLOBAL DATA STRUCTURES
contributions = {}
lifetime_earnings = {}
last_active = {}
counting_state = {"current_count": 0, "last_user": None}

# Initialize ChatterBot
chat_bot = ChatterBot()

# DATA MANAGEMENT CLASS
class DataManager:
    """Real data manager implementation"""
    
    @staticmethod
    def load_json_file(filename):
        """Load data from JSON file with error handling"""
        try:
            if os.path.exists(filename):
                with open(filename, "r") as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading {filename}: {e}")
        return {}
    
    @staticmethod 
    def save_json_file(filename, data):
        """Save data to JSON file with error handling"""
        try:
            with open(filename, "w") as f:
                json.dump(data, f, indent=2)
            logger.debug(f"Saved data to {filename}")
        except Exception as e:
            logger.error(f"Error saving {filename}: {e}")
    
    @staticmethod
    def load_contributions():
        """Load contributions from file"""
        return DataManager.load_json_file("contributions.txt")
    
    @staticmethod
    def load_counting_state():
        """Load counting state from file"""
        return DataManager.load_json_file("counting_state.txt")

    @staticmethod
    def load_lifetime_earnings():
        """Load lifetime earnings from file"""
        return DataManager.load_json_file("lifetime_earnings.txt")

    @staticmethod
    def load_last_active():
        """Load last active data from file with TXT fallback"""
        try:
            # First try TXT file
            if os.path.exists("last_active.txt"):
                with open("last_active.txt", "r") as f:
                    return json.load(f)
            # Fallback to JSON for backward compatibility
            elif os.path.exists("last_active.json"):
                with open("last_active.json", "r") as f:
                    content = f.read().strip()
                    if content:
                        return json.loads(content)
        except Exception as e:
            logger.error(f"Error in DataManager loading last active: {e}")
        return {}

# HELPER CLASSES - Real implementations
class PermissionHelper:
    """Helper class for permission and role management"""
    
    @staticmethod
    def is_vip_member(member) -> bool:
        """Check if a member has VIP status. Handles both Member and User objects."""
        if not member:
            return False
        
        # Only Member objects have roles, User objects (like in DMs) don't
        if not hasattr(member, 'roles'):
            return False
        
        # Look for VIP role by name (including the exact VIP role name)
        vip_role_names = ["VIP", "Vip", "vip", "Premium", "Patron", "Supporter"]
        for role in member.roles:
            if role.name in vip_role_names or role.name == BOT_CONFIG["VIP_ROLE_NAME"]:
                return True
        return False
    
    @staticmethod
    def is_star_contributor(member) -> bool:
        """Check if a member has Star Contributor status (2x contribution points)."""
        if not member:
            return False
        
        # Only Member objects have roles, User objects (like in DMs) don't
        if not hasattr(member, 'roles'):
            return False
        
        # Look for Star Contributor role by exact name
        star_contributor_role_name = "⚡Star Contributor ⚡"
        return discord.utils.get(member.roles, name=star_contributor_role_name) is not None
    
    @staticmethod
    def get_vip_role(guild):
        """Get the VIP role from the guild"""
        if not guild:
            return None
            
        vip_role_names = ["VIP", "Vip", "vip", "Premium", "Patron", "Supporter"]
        for role in guild.roles:
            if role.name in vip_role_names:
                return role
        return None
    
    @staticmethod 
    def is_bot_owner(user_id: int) -> bool:
        """Check if user is the bot owner"""
        return user_id == BOT_CONFIG.get('owner_id', 0)
    
    @staticmethod
    def has_dev_permissions(member) -> bool:
        """Check if a member has dev command permissions (bot owner or moderation role)"""
        if not member:
            return False
        
        # Check if bot owner
        if PermissionHelper.is_bot_owner(member.id):
            return True
            
        # Check for moderation role
        moderation_role_names = ["⚒️ Moderation", "Moderation", "⚒️Moderation"]
        for role in member.roles:
            if role.name in moderation_role_names:
                return True
        return False

class GameHelpers:
    """Game helpers with text-based reactions (GIFs removed to avoid conflicts)"""
    
    @staticmethod
    def get_random_gif(category: str):
        """Get a placeholder message for the given category (GIFs removed)"""
        # GIFs removed to avoid conflicts - returning category-appropriate messages instead
        messages = {
            'hug': ["*sends virtual hug*", "*hugs*", "*warm embrace*"],
            'pat': ["*pat pat*", "*head pat*", "*gentle pat*"],
            'slap': ["*slap*", "*bonk*", "*whack*"],
            'dog': ["🐕 Woof!", "🐶 *happy dog noises*", "🦮 *tail wagging*"],
            'cat': ["🐱 Meow!", "🐈 *purrs*", "😺 *cat vibes*"]
        }
        
        category_messages = messages.get(category, ["*generic reaction*"])
        return random.choice(category_messages)
    
    @staticmethod
    def get_random_pun():
        """Get a random pun from an expanded collection"""
        puns = [
            # Original classics
            "I told my wife she was drawing her eyebrows too high. She looked surprised.",
            "I haven't slept for ten days, because that would be too long.",
            "A skunk fell in the river and stank to the bottom.",
            "I used to hate facial hair, but then it grew on me.",
            "Time flies like an arrow; fruit flies like a banana.",
            "I wondered why the baseball kept getting bigger. Then it hit me.",
            "Did you hear about the mathematician who's afraid of negative numbers? He'll stop at nothing to avoid them.",
            "Yesterday I accidentally swallowed some food coloring. The doctor says I'm OK, but I feel like I've dyed a little inside.",
            "Why don't scientists trust atoms? Because they make up everything.",
            "I used to be addicted to soap, but I'm clean now.",
            "A bicycle can't stand on its own because it's two-tired.",
            "What do you call a fake noodle? An impasta!",
            "I couldn't quite remember how to throw a boomerang, but eventually it came back to me.",
            "Why did the scarecrow win an award? He was outstanding in his field.",
            "I was wondering why the ball kept getting bigger and bigger... then it hit me!",
            
            # NEW HILARIOUS ADDITIONS
            "I'm reading a book about anti-gravity. It's impossible to put down!",
            "Did you hear about the claustrophobic astronaut? He just needed some space.",
            "I told my cat a joke about dogs, but he didn't find it a-mew-sing.",
            "Why don't skeletons fight each other? They don't have the guts.",
            "I used to be a banker, but I lost interest.",
            "The graveyard is so crowded, people are dying to get in!",
            "I'm terrified of elevators, so I'll start taking steps to avoid them.",
            "Why did the coffee file a police report? It got mugged!",
            "I used to work at a calendar factory, but I got fired for taking days off.",
            "What do you call a sleeping bull? A bulldozer!",
            "I didn't like my beard at first, but then it grew on me.",
            "Why don't eggs tell jokes? They'd crack each other up!",
            "I lost my job at the bank. A woman asked me to check her balance, so I pushed her over.",
            "What's the best thing about Switzerland? I don't know, but the flag is a big plus.",
            "I invented a new word: Plagiarism!",
            "Why did the gym close down? It just didn't work out!",
            "I told my doctor I broke my arm in two places. He told me to stop going to those places.",
            "What do you call a fish wearing a crown? A king fish!",
            "I used to hate facial hair, but then it grew on me.",
            "Why don't scientists trust atoms? Because they make up everything!",
            "I'm addicted to brake fluid, but I can stop anytime I want.",
            "What did the ocean say to the beach? Nothing, it just waved.",
            "I bought the world's worst thesaurus yesterday. Not only is it terrible, it's terrible.",
            "Why did the invisible man turn down the job offer? He couldn't see himself doing it.",
            "I haven't spoken to my wife in years. I didn't want to interrupt her.",
            "What do you call a dinosaur that crashes his car? Tyrannosaurus Wrecks!",
            "I stayed up all night wondering where the sun went... then it dawned on me.",
            "What do you call a bear with no teeth? A gummy bear!",
            "I fired my masseuse today. She just rubbed me the wrong way.",
            "Why did the cookie go to the doctor? Because it felt crumbly!",
            "What's the difference between a poorly dressed man on a bicycle and a well-dressed man on a tricycle? Attire!",
            "I told a chemistry joke, but there was no reaction.",
            "What do you call a cow with no legs? Ground beef!",
            "Why don't programmers like nature? It has too many bugs.",
            "I was going to tell a time-traveling joke, but you didn't like it.",
            "What do you call a fake stone in Ireland? A sham rock!",
            "I used to be obsessed with fixing broken clocks. It was about time.",
            "Why did the golfer bring two pairs of pants? In case he got a hole in one!",
            "What do you call a sleeping bull at the rodeo? A bulldozer having a power nap!",
            "I tried to catch fog earlier. I mist.",
            "What's orange and sounds like a parrot? A carrot!",
            "Why don't some couples go to the gym? Because some relationships don't work out!",
            "I'm reading a book on the history of glue. Can't put it down!",
            "What do you call a factory that makes okay products? A satisfactory!",
            "Why did the math book look so sad? Because it was full of problems!",
            "I got fired from the orange juice factory. Apparently I couldn't concentrate.",
            "What do you call a fish that needs help with his vocals? Auto-tuna!",
            "Why don't scientists trust stairs? Because they're always up to something!",
            "I named my horse Mayo. Sometimes Mayo neighs!",
            "What do you call a dog magician? A labracadabrador!",
            "I used to work for a soft drink can crusher. It was soda pressing.",
            "What do you call a belt made of watches? A waist of time!",
            "Why did the scarecrow become a successful neurosurgeon? He was outstanding in his field!",
            "I told my wife she should embrace her mistakes. She hugged me.",
            "What's the best way to watch a fly-fishing tournament? Live stream!",
            "Why don't aliens ever land at airports? Because they're looking for space!",
            "I wondered why the baseball was getting bigger. Then it hit me!",
            "What do you call a pig that does karate? A pork chop!",
            "Why did the computer go to therapy? It had too many bytes!",
            "I used to be a personal trainer, but I gave my too weak notice.",
            "What do you call a sleeping bull? A bulldozer!",
            "Why don't skeletons ever go trick or treating? Because they have no-body to go with!",
            "I'm terrified of speed bumps, but I'm slowly getting over it.",
            "What do you call a bee that can't make up its mind? A maybe!",
            "I lost my thesaurus. I can't find the words to describe how upset I am.",
            "Why did the bicycle fall over? It was two-tired!",
            "What do you call a group of disorganized cats? A cat-astrophe!",
            "I used to be afraid of hurdles, but I got over it.",
            "Why don't eggs tell each other jokes? They'd crack up!",
            "What did the left eye say to the right eye? Between you and me, something smells.",
            "I'm so good at sleeping, I can do it with my eyes closed!",
            "Why did the tomato turn red? Because it saw the salad dressing!",
            "What do you call a sleeping bull in a flower bed? A bulldozer in a daisy chain!",
            "I got a job at a bakery because I kneaded dough.",
            "What's the best thing about living in Switzerland? Well, the flag is a big plus.",
            "Why don't scientists trust atoms? Because they make up literally everything!",
            "I bought a dog from a blacksmith. As soon as I got home, he made a bolt for the door!",
            "What do you call a fish wearing a bowtie? Sofishticated!",
            "Why did the coffee go to the police? It was mugged!",
            "I'm reading a horror book in braille. Something bad is about to happen, I can feel it.",
            "What do you call a cow in an earthquake? A milkshake!",
            "Why don't melons get married? Because they cantaloupe!",
            "I used to work at a shoe recycling shop. It was sole destroying.",
            "What do you call a fish that wears a crown? Your royal high-ness!",
            "Why did the cookie cry? Because his mom was a wafer too long!",
            "I told my dad jokes to everyone. Now I'm a father figure.",
            "What do you call a dinosaur that loves to sleep? A dino-snore!",
            "Why don't scientists trust atoms? Because they make up everything and split when things get heated!"
        ]
        return random.choice(puns)
    
    @staticmethod
    def get_8ball_response():
        """Get a magic 8-ball response from an expanded collection"""
        responses = [
            # Classic responses
            "It is certain", "Reply hazy, try again", "Don't count on it",
            "It is decidedly so", "Ask again later", "My reply is no",
            "Without a doubt", "Better not tell you now", "My sources say no",
            "Yes definitely", "Cannot predict now", "My sources say no",
            "You may rely on it", "Concentrate and ask again", "Very doubtful",
            "As I see it, yes", "Most likely", "Outlook good", "Yes", "Signs point to yes",
            "Absolutely!", "Not a chance", "All signs point to yes",
            
            # HILARIOUS NEW ADDITIONS
            "The stars say no, but they're probably drunk",
            "Magic 8-ball is tired, ask later (or never)",
            "Definitely maybe, or maybe definitely",
            "The future is unclear, like your question",
            "Ask your cat instead, they're wiser",
            "Only if you sacrifice a pizza to the gods",
            "The universe is undecided and needs therapy",
            "Try turning your life off and on again",
            "My psychic powers say... WiFi connection lost",
            "Error 404: Future not found",
            "The answer is yes, but actually no",
            "I would tell you, but then I'd have to bill you",
            "Survey says... BUZZ! Wrong question!",
            "The magic 8-ball union is on strike, ask tomorrow",
            "Results inconclusive, consult your horoscope... or a coin",
            "I'm just a ball, what do you expect?",
            "The prophecy is unclear, try again in 5-7 business days",
            "Signs point to 'why are you asking a ball?'",
            "The cosmos laughed at your question",
            "I consulted the ancient spirits... they said 'meh'",
            "Your question broke my crystal ball, thanks a lot",
            "The answer is 42, but that's to a different question",
            "I'm having an existential crisis, ask later",
            "The all-knowing ball says... wait, what was the question?",
            "My sources are currently in a meeting, please hold",
            "The future called, it went to voicemail",
            "I would answer, but I'm distracted by how round I am",
            "The spirits are busy binge-watching Netflix",
            "Outlook unclear, needs more coffee",
            "The prophecy says... actually, it's just grocery list",
            "I'm not a miracle worker, I'm just really round",
            "The universe shrugged",
            "My magic is buffering... 99% complete",
            "Error: Question too existential for a plastic ball",
            "The answer lies within... this other magic 8-ball",
            "I'm retired, ask Siri",
            "The cosmic forces are arguing about your question",
            "Probability of answer: maybe",
            "I'm on my lunch break, try the Magic 7-ball",
            "The spirits say 'have you tried googling it?'",
            "My crystal is cloudy, might need Windex",
            "The answer is classified by the Ball Intelligence Agency",
            "I'm experiencing technical difficulties with reality",
            "The future is so bright, I need sunglasses to see it",
            "My prediction powers are currently downloading... 12% complete"
        ]
        return random.choice(responses)

# DATA STRUCTURES - Real shop system
BUYABLE_ROLES = {
    # Legendary Tier
    "electric samurai": "⛩️ Electric Samurai⛩️",
    "phoenix ascendant": "🐦‍🔥 Phoenix Ascendant 🐦‍🔥", 
    "cosmic guardian": "🌌 Cosmic Guardian 🌌",
    "dragon lord": "🐲 Dragon Lord 🐲",
    "shadow assassin": "🗡️ Shadow Assassin 🗡️",
    "crimson monarch": "👑Crimson Monarch 👑",
    
    # Epic Tier
    "ashened one": "🔥 Ashened One 🔥",
    "marked one": "☢️ Marked one ☢️",
    "frost warden": "❄️ Frost Warden ❄️",
    "void walker": "🌑 Void Walker 🌑",
    "storm caller": "⚡ Storm Caller ⚡",
    "mystic sage": "🔮 Mystic Sage 🔮",
    
    # Rare Tier  
    "pixel prodigy": "🌴Pixel Prodigy 🌴",
    "colonizer": "💂 Colonizer💂",
    "cyber knight": "🤖 Cyber Knight 🤖",
    "neon runner": "🏃‍♂️ Neon Runner 🏃‍♂️",
    "crystal miner": "💎 Crystal Miner 💎",
    "star navigator": "⭐ Star Navigator ⭐",
    "code wizard": "🧙‍♂️ Code Wizard 🧙‍♂️",
    
    # Common Tier
    "night owl": "🦉 Night Owl 🦉",
    "coffee addict": "☕ Coffee Addict ☕",
    "meme lord": "😂 Meme Lord 😂",
    "game master": "🎮 Game Master 🎮",
    "music lover": "🎵 Music Lover 🎵",
    "book worm": "📚 Book Worm 📚", 
    "artist": "🎨 Artist 🎨",
    "chef": "👨‍🍳 Chef 👨‍🍳",
    
    # Starter Tier
    "newcomer": "🌱 Newcomer 🌱",
    "enthusiast": "✨ Enthusiast ✨",
    "explorer": "🗺️ Explorer 🗺️",
    "dreamer": "💭 Dreamer 💭",
    "helper": "🤝 Helper 🤝",
    
    # Legacy support for old role names
    "bronze": "Bronze Supporter",
    "silver": "Silver Supporter", 
    "gold": "Gold Supporter",
    "platinum": "Platinum Supporter"
}

DATA_FILES = {
    "RIDDLE_STATE": "riddle_state.txt",
    "CONTRIBUTIONS": "contributions.txt",
    "LIFETIME_EARNINGS": "lifetime_earnings.txt",
    "COUNTING_STATE": "counting_state.txt",
    "LAST_ACTIVE": "last_active.txt",
    "ACHIEVEMENTS": "achievements_data.txt",
    "WEEKLY_CONTRIBUTIONS": "weekly_contributions.txt",
    "WEEKLY_TOP_CONTRIBUTORS": "weekly_top_contributors.txt"
}

# REAL FUNCTIONS - Working implementations
def check_economy_achievements(user_id, stats):
    """Real economy achievement checker"""
    try:
        newly_unlocked = []
        
        # Check various economy-related achievements
        if stats.get("total_spent", 0) >= 10000:
            achievement = achievement_system.get_achievement("big_spender")
            if achievement and not achievement_system.has_achievement(user_id, "big_spender"):
                achievement_system.unlock_achievement(user_id, "big_spender")
                newly_unlocked.append(achievement)
        
        if stats.get("points_earned", 0) >= 50000:
            achievement = achievement_system.get_achievement("point_collector")
            if achievement and not achievement_system.has_achievement(user_id, "point_collector"):
                achievement_system.unlock_achievement(user_id, "point_collector")
                newly_unlocked.append(achievement)
                
        return newly_unlocked
    except Exception as e:
        logger.error(f"Error checking economy achievements: {e}")
        return []

class LevelSystem:
    """Real level system implementation"""
    
    @staticmethod
    def calculate_level(points):
        """Calculate level based on points (level = sqrt(points/100))"""
        if points <= 0:
            return 1
        # Square root formula for smooth progression
        import math
        level = int(math.sqrt(points / 100)) + 1
        return max(1, level)
    
    @staticmethod
    def get_level(points):
        """Get level from points - same as calculate_level"""
        return LevelSystem.calculate_level(points)
    
    @staticmethod
    def get_level_info(user_id):
        """Get comprehensive level info for a user"""
        try:
            user_id_str = str(user_id)
            lifetime_points = lifetime_earnings.get(user_id_str, 0)
            current_level = LevelSystem.calculate_level(lifetime_points)
            
            # Calculate points needed for next level
            next_level = current_level + 1
            next_level_points = (next_level - 1) ** 2 * 100
            points_to_next = next_level_points - lifetime_points
            
            # Calculate progress within current level
            current_level_points = (current_level - 1) ** 2 * 100
            progress_points = lifetime_points - current_level_points
            level_span = next_level_points - current_level_points
            progress_percentage = (progress_points / level_span) * 100 if level_span > 0 else 100
            
            return {
                "level": current_level,
                "current_xp": lifetime_points,
                "next_level_xp": next_level_points,
                "points_to_next": max(0, points_to_next),
                "progress_percentage": min(100, progress_percentage),
                "current_level_start": current_level_points,
                "progress_in_level": progress_points
            }
        except Exception as e:
            logger.error(f"Error getting level info: {e}")
            return {"level": 1, "current_xp": 0, "next_level_xp": 100, "points_to_next": 100, "progress_percentage": 0}
    
    @staticmethod
    def get_xp_for_level(level):
        """Get the XP required to reach a specific level"""
        if level <= 1:
            return 0
        return (level - 1) ** 2 * 100

class EmbedHelper:
    """Enhanced embed helper implementation"""
    
    @staticmethod
    def create_embed(title, description="", color=discord.Color.blue()):
        """Basic embed creation"""
        return discord.Embed(title=title, description=description, color=color)
    
    @staticmethod
    def create_success_embed(title, description=""):
        """Create success embed with green color"""
        return discord.Embed(title=title, description=description, color=discord.Color.green())
    
    @staticmethod
    def create_error_embed(title, description=""):
        """Create error embed with red color"""
        return discord.Embed(title=title, description=description, color=discord.Color.red())
    
    @staticmethod
    def create_warning_embed(title, description=""):
        """Create warning embed with orange color"""
        return discord.Embed(title=title, description=description, color=discord.Color.orange())
    
    @staticmethod
    def create_info_embed(title, description=""):
        """Create info embed with blue color"""
        return discord.Embed(title=title, description=description, color=discord.Color.blue())

# REAL DATA ACCESS FUNCTIONS
def load_counting_state():
    """Load counting state from file with error handling"""
    try:
        filename = DATA_FILES.get("COUNTING_STATE", "counting_state.txt")
        if os.path.exists(filename):
            with open(filename, "r") as f:
                data = json.load(f)
                # Ensure all required fields exist
                if "current" not in data:
                    data["current"] = data.get("current_count", 0)
                if "channel_id" not in data:
                    data["channel_id"] = 000000000000000000  # Replace with your counting channel ID
                logger.info(f"Loaded counting state: current={data.get('current', 0)}, channel={data.get('channel_id')}")
                return data
    except Exception as e:
        logger.error(f"Error loading counting state: {e}")
    
    # Return default state if file doesn't exist or error occurred
    default_state = {
        "current_count": 0, 
        "last_user": None,
        "channel_id": 000000000000000000,  # Replace with your counting channel ID
        "current": 0  # Add current field that the code expects
    }
    logger.info("Using default counting state")
    return default_state

def save_counting_state(state):
    """Save counting state to file with error handling"""
    try:
        filename = DATA_FILES.get("COUNTING_STATE", "counting_state.txt")
        with open(filename, "w") as f:
            json.dump(state, f, indent=2)
        logger.debug(f"Saved counting state: current={state.get('current', 0)}")
    except Exception as e:
        logger.error(f"Error saving counting state: {e}")

def load_contributions():
    """Load contributions from .txt file with fallback to JSON"""
    try:
        # First try to load from contributions.txt
        if os.path.exists("contributions.txt"):
            data = {}
            with open("contributions.txt", "r", encoding='utf-8') as f:
                content = f.read().strip()
                if content:
                    try:
                        # Try JSON format first
                        data = json.loads(content)
                        logger.info(f"Loaded contributions from contributions.txt (JSON format) for {len(data)} users")
                        return data
                    except json.JSONDecodeError:
                        # Try line-by-line format: user_id:points
                        for line in f.readlines():
                            line = line.strip()
                            if ':' in line:
                                user_id, points = line.split(':', 1)
                                try:
                                    data[user_id.strip()] = int(points.strip())
                                except ValueError:
                                    logger.warning(f"Invalid contribution entry: {line}")
                        logger.info(f"Loaded contributions from contributions.txt (line format) for {len(data)} users")
                        return data
        
        # Fallback to JSON file
        filename = DATA_FILES.get("CONTRIBUTIONS", "contributions.txt")
        if os.path.exists(filename):
            with open(filename, "r") as f:
                data = json.load(f)
                logger.info(f"Loaded contributions from {filename} for {len(data)} users")
                return data
                
    except Exception as e:
        logger.error(f"Error loading contributions: {e}")
    
    logger.info("No contributions data found, starting with empty data")
    return {}

def save_contributions(data):
    """Save contributions to TXT file"""
    try:
        # Save to contributions.txt (JSON format for reliability)
        filename = DATA_FILES.get("CONTRIBUTIONS", "contributions.txt")
        with open(filename, "w", encoding='utf-8') as f:
            json.dump(data, f, indent=2)
            
        logger.debug(f"Saved contributions for {len(data)} users to TXT file")
    except Exception as e:
        logger.error(f"Error saving contributions: {e}")

def load_lifetime_earnings():
    """Load lifetime earnings from .txt file with fallback to JSON"""
    try:
        # First try to load from lifetime_earnings.txt
        if os.path.exists("lifetime_earnings.txt"):
            data = {}
            with open("lifetime_earnings.txt", "r", encoding='utf-8') as f:
                content = f.read().strip()
                if content:
                    try:
                        # Try JSON format first
                        data = json.loads(content)
                        logger.info(f"Loaded lifetime earnings from lifetime_earnings.txt (JSON format) for {len(data)} users")
                        return data
                    except json.JSONDecodeError:
                        # Try line-by-line format: user_id:points
                        lines = content.split('\n')
                        for line in lines:
                            line = line.strip()
                            if ':' in line:
                                user_id, points = line.split(':', 1)
                                try:
                                    data[user_id.strip()] = int(points.strip())
                                except ValueError:
                                    logger.warning(f"Invalid lifetime earnings entry: {line}")
                        logger.info(f"Loaded lifetime earnings from lifetime_earnings.txt (line format) for {len(data)} users")
                        return data
        
        # Fallback to JSON file
        filename = DATA_FILES.get("LIFETIME_EARNINGS", "lifetime_earnings.txt")
        if os.path.exists(filename):
            with open(filename, "r") as f:
                data = json.load(f)
                logger.info(f"Loaded lifetime earnings from {filename} for {len(data)} users")
                return data
                
    except Exception as e:
        logger.error(f"Error loading lifetime earnings: {e}")
    
    logger.info("No lifetime earnings data found, starting with empty data")
    return {}

def save_lifetime_earnings(data):
    """Save lifetime earnings to TXT file"""
    try:
        # Save to lifetime_earnings.txt (JSON format for reliability)
        filename = DATA_FILES.get("LIFETIME_EARNINGS", "lifetime_earnings.txt")
        with open(filename, "w", encoding='utf-8') as f:
            json.dump(data, f, indent=2)
            
        logger.debug(f"Saved lifetime earnings for {len(data)} users to TXT file")
    except Exception as e:
        logger.error(f"Error saving lifetime earnings: {e}")

def load_last_active():
    """Load last active data from TXT or JSON file"""
    try:
        # First try to load from TXT file
        if os.path.exists("last_active.txt"):
            with open("last_active.txt", "r") as f:
                data = json.load(f)
                logger.info(f"Loaded last active data for {len(data)} users from TXT")
                return data
        # Fallback to JSON file for backward compatibility
        elif os.path.exists("last_active.json"):
            with open("last_active.json", "r") as f:
                content = f.read().strip()
                if content:
                    data = json.loads(content)
                    logger.info(f"Loaded last active data for {len(data)} users from JSON, converting to TXT")
                    # Convert to TXT format for future use
                    save_last_active(data)
                    return data
    except Exception as e:
        logger.error(f"Error loading last active: {e}")
    return {}

def save_last_active(data):
    """Save last active data to TXT file"""
    try:
        # Save as TXT (primary format)
        with open("last_active.txt", "w") as f:
            json.dump(data, f, indent=2)
        logger.debug(f"Saved last active data for {len(data)} users to TXT")
    except Exception as e:
        logger.error(f"Error saving last active: {e}")

# Initialize global variables with real data
counting_state = load_counting_state()
last_active = load_last_active()
contributions = load_contributions()
lifetime_earnings = load_lifetime_earnings()
contrib_lock = asyncio.Lock()


@bot.command()
@cooldown(1, 30, BucketType.user)  # 30 second cooldown
async def blackjack(ctx, bet: int = None):
    """
    Play blackjack against the bot with your contribution points as stakes!
    Usage: !blackjack <bet_amount>
    
    Rules:
    - Get as close to 21 as possible without going over
    - Aces count as 1 or 11 (whichever is better)
    - Face cards (J, Q, K) count as 10
    - Beat the dealer to win double your bet!
    """
    if bet is None:
        await ctx.send("❌ Please specify a bet amount! Usage: `!blackjack <bet_amount>` - I can't read minds... yet! 🧠")
        return
    
    if bet <= 0:
        await ctx.send("❌ Bet amount must be positive! Unless you've invented negative money... 💸")
        return
    
    user_id = str(ctx.author.id)
    user_points = contributions.get(user_id, 0)
    
    if bet > user_points:
        await ctx.send(f"❌ You don't have enough contribution points! You have **{user_points:,}** points.")
        return
    
    if bet < 10:
        await ctx.send("❌ Minimum bet is **10** contribution points!")
        return
    
    # Deduct bet from user's points
    contributions[user_id] = user_points - bet
    await save_contributions_async(contributions)
    
    # Create deck and shuffle
    suits = ['♠️', '♥️', '♦️', '♣️']
    ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
    deck = [(rank, suit) for suit in suits for rank in ranks]
    random.shuffle(deck)
    
    # Deal initial cards
    player_hand = [deck.pop(), deck.pop()]
    dealer_hand = [deck.pop(), deck.pop()]
    
    def card_value(card):
        """Get the numeric value of a card."""
        rank = card[0]
        if rank in ['J', 'Q', 'K']:
            return 10
        elif rank == 'A':
            return 11  # Will be adjusted later
        else:
            return int(rank)
    
    def hand_value(hand):
        """Calculate the best value for a hand."""
        total = sum(card_value(card) for card in hand)
        aces = sum(1 for card in hand if card[0] == 'A')
        
        # Adjust for aces
        while total > 21 and aces > 0:
            total -= 10
            aces -= 1
        
        return total
    
    def format_hand(hand, hide_first=False):
        """Format a hand for display."""
        if hide_first:
            return f"🎴 {hand[1][0]}{hand[1][1]}"
        else:
            return " ".join(f"{card[0]}{card[1]}" for card in hand)
    
    def is_blackjack(hand):
        """Check if hand is a natural blackjack."""
        return len(hand) == 2 and hand_value(hand) == 21
    
    # Check for natural blackjack
    player_blackjack = is_blackjack(player_hand)
    dealer_blackjack = is_blackjack(dealer_hand)
    
    # Create initial embed with enhanced styling
    embed = discord.Embed(
        title="🃏 💎 BLACKJACK ROYAL CASINO 💎 🃏",
        description="━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        color=discord.Color.from_rgb(0, 128, 0)  # Rich casino green
    )
    
    # Add casino atmosphere
    embed.add_field(
        name="🎰 🌟 WELCOME TO THE TABLES 🌟 🎰",
        value=f"```yaml\n🎯 Player: {ctx.author.display_name}\n🤖 Dealer: StarChan House\n💰 Stakes: {bet:,} points\n```",
        inline=False
    )
    
    # Visual separator with style
    embed.add_field(name="✨ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ ✨", value="", inline=False)
    
    # Enhanced hand display
    embed.add_field(
        name="🎯 👤 YOUR HAND 👤 🎯",
        value=f"```fix\n🃏 {format_hand(player_hand)}\n💫 Total: {hand_value(player_hand)}\n```",
        inline=True
    )
    
    embed.add_field(
        name="🤖 🎰 DEALER'S HAND 🎰 🤖",
        value=f"```yaml\n🎴 {format_hand(dealer_hand, hide_first=True)}\n❓ Hidden: ?\n```",
        inline=True
    )
    
    # Add spacing field with style
    embed.add_field(name="🎲 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 🎲", value="", inline=False)
    
    # Handle natural blackjacks with enhanced styling
    if player_blackjack and dealer_blackjack:
        embed.add_field(
            name="🤝 ⚡ RARE! DOUBLE BLACKJACK! ⚡ 🤝",
            value="```yaml\n🎭 INCREDIBLE! Both players hit 21!\n🤝 PUSH - Honors even!\n💰 Bet gracefully returned\n```",
            inline=False
        )
        embed.color = discord.Color.from_rgb(255, 215, 0)  # Gold
        await add_points_direct(user_id, bet)
        await ctx.send(embed=embed)
        return
    elif player_blackjack:
        winnings = int(bet * 2.5)  # Blackjack pays 3:2
        embed.add_field(
            name="🎊 💥 BLACKJACK ROYALE! 💥 🎊",
            value=f"```yaml\n🌟 NATURAL 21! PHENOMENAL!\n💎 You win {winnings:,} points!\n👑 Blackjack pays 3:2 premium!\n🏆 Casino bows to your skill!\n```",
            inline=False
        )
        embed.color = discord.Color.from_rgb(255, 215, 0)  # Gold
        await add_points_direct(user_id, winnings)
        
        # Track blackjack win achievement
        try:
            user_achievement = achievement_system.get_user_achievement(ctx.author.id, "blackjack_winner")
            blackjack_wins = user_achievement.progress.get("blackjack_wins", 0) + 1
            newly_unlocked = check_gaming_achievements(ctx.author.id, {"blackjack_wins": blackjack_wins})
            
            for achievement in newly_unlocked:
                await send_achievement_notification(bot, ctx.author, achievement)
                if achievement.reward_points > 0:
                    await add_contribution(ctx.author.id, achievement.reward_points * 10, ctx.channel, ctx.author)
        except Exception as e:
            logger.error(f"Error tracking blackjack achievement: {e}")
        
        # Check for Gambler role award (10k+ bet win)
        if bet >= 10000:
            await _award_gambler_role(ctx, bet)
        
        await ctx.send(embed=embed)
        return
    elif dealer_blackjack:
        embed.add_field(
            name="💀 🎰 HOUSE BLACKJACK 🎰 💀",
            value="```diff\n- The house reveals natural 21!\n- Lady Luck favors the dealer today\n- Your courage is noted, challenger\n```",
            inline=False
        )
        embed.color = discord.Color.from_rgb(139, 0, 0)  # Dark red
        embed.set_field_at(2,
            name="🤖 🎰 DEALER'S HAND 🎰 🤖",
            value=f"```fix\n🃏 {format_hand(dealer_hand)}\n💫 Total: {hand_value(dealer_hand)} - BLACKJACK!\n```",
            inline=True
        )
        await ctx.send(embed=embed)
        return
    
    # Add enhanced game instructions
    embed.add_field(
        name="🎮 ⚡ YOUR MOVE, CHAMPION! ⚡ 🎮",
        value="```yaml\n🇭 HIT    - Draw another card (risk vs reward)\n🇸 STAND  - Lock in your current hand\n\n⏰ 60 seconds to choose your destiny!\n🎯 Will you chase perfection or play it safe?\n```",
        inline=False
    )
    
    embed.add_field(
        name="🎲 🌟 FORTUNE FAVORS THE BOLD 🌟 🎲",
        value="```diff\n+ Get to 21 without going over\n+ Beat the dealer to win 2x your bet\n+ Natural blackjack pays 2.5x!\n```",
        inline=False
    )
    
    embed.set_footer(text="🎰 StarChan Royal Casino • Where legends are made! 👑", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
    
    game_message = await ctx.send(embed=embed)
    await game_message.add_reaction("🇭")  # Hit
    await game_message.add_reaction("🇸")  # Stand
    
    # Player's turn
    def check(reaction, user):
        return (user == ctx.author and 
                str(reaction.emoji) in ["🇭", "🇸"] and 
                reaction.message.id == game_message.id)
    
    while hand_value(player_hand) < 21:
        try:
            reaction, user = await bot.wait_for("reaction_add", timeout=60.0, check=check)
            
            if str(reaction.emoji) == "🇭":
                # Hit
                player_hand.append(deck.pop())
                player_value = hand_value(player_hand)
                
                embed.set_field_at(1, 
                    name="🎯 👤 YOUR HAND 👤 🎯",
                    value=f"```fix\n🃏 {format_hand(player_hand)}\n💫 Total: {player_value}\n```",
                    inline=True
                )
                
                if player_value > 21:
                    embed.add_field(
                        name="💥 🎲 BUST! GAME OVER! 🎲 💥", 
                        value="```diff\n- Exceeded 21! The cards have spoken!\n- House claims victory this round\n- The risk didn't pay off this time\n```", 
                        inline=False
                    )
                    embed.color = discord.Color.from_rgb(139, 0, 0)  # Dark red
                    await game_message.edit(embed=embed)
                    return
                elif player_value == 21:
                    embed.set_field_at(3, 
                        name="🎯 ⚡ PERFECT 21! EXCELLENCE! ⚡ 🎯",
                        value="```yaml\n🌟 You've achieved perfection!\n🎯 Standing automatically with 21\n👑 The cards align in your favor\n```",
                        inline=False
                    )
                    embed.color = discord.Color.from_rgb(255, 215, 0)  # Gold
                    await game_message.edit(embed=embed)
                    await asyncio.sleep(2)  # Longer pause for dramatic effect
                    break
                else:
                    embed.set_field_at(3, 
                        name="🎮 ⚡ YOUR MOVE, CHAMPION! ⚡ 🎮",
                        value="```yaml\n🇭 HIT    - Draw another card (risk vs reward)\n🇸 STAND  - Lock in your current hand\n\n⏰ 60 seconds to choose your destiny!\n🎯 Will you chase perfection or play it safe?\n```",
                        inline=False
                    )
                    await game_message.edit(embed=embed)
                    
            elif str(reaction.emoji) == "🇸":
                # Stand
                break
                
        except asyncio.TimeoutError:
            embed.add_field(
                name="⏰ ⌛ TIME EXPIRED! ⌛ ⏰", 
                value="```yaml\n🕐 Decision time has elapsed!\n💰 Bet graciously returned\n⚖️ No winners, no losers - honor intact\n```", 
                inline=False
            )
            embed.color = discord.Color.from_rgb(255, 165, 0)  # Orange
            await add_points_direct(user_id, bet)
            await game_message.edit(embed=embed)
            return
    
    # Dealer's turn with enhanced styling
    embed.set_field_at(2,
        name="🤖 🎰 DEALER'S HAND 🎰 🤖",
        value=f"```fix\n🃏 {format_hand(dealer_hand)}\n💫 Total: {hand_value(dealer_hand)}\n```",
        inline=True
    )
    
    # Remove the game instructions fields
    while len(embed.fields) > 3:
        embed.remove_field(-1)
    
    embed.add_field(
        name="🤖 🎰 THE HOUSE REVEALS ITS HAND 🎰 🤖",
        value="```yaml\n🏛️ House rules: Hit on 16, Stand on 17\n🎲 The cards of fate are turning...\n👁️ All secrets now revealed\n```",
        inline=False
    )
    
    await game_message.edit(embed=embed)
    await asyncio.sleep(3)  # Longer dramatic pause
    
    # Dealer hits until 17 or higher
    while hand_value(dealer_hand) < 17:
        dealer_hand.append(deck.pop())
        dealer_value = hand_value(dealer_hand)
        
        embed.set_field_at(1,
            name="🤖 🎰 Dealer's Hand",
            value=f"```\n{format_hand(dealer_hand)} = {dealer_value}\n```",
            inline=True
        )
        
        if dealer_value > 21:
            embed.set_field_at(2,
                name="💥 🎰 DEALER BUSTS! 🎰 💥",
                value="```diff\n- Dealer went over 21!\n+ You win!\n```",
                inline=False
            )
        else:
            embed.set_field_at(2,
                name="🤖 🎲 DEALER'S TURN 🎲 🤖",
                value="```\n🎯 " + ("Dealer hits..." if dealer_value < 17 else "Dealer stands.") + "\n```",
                inline=False
            )
        
        await game_message.edit(embed=embed)
        await asyncio.sleep(2)
    
    # Determine winner with enhanced styling
    player_value = hand_value(player_hand)
    dealer_value = hand_value(dealer_hand)
    
    if dealer_value > 21:
        # Dealer busts, player wins
        winnings = bet * 2
        embed.add_field(
            name="🎊 🏆 SPECTACULAR VICTORY! 🏆 🎊", 
            value=f"```yaml\n💥 DEALER BUST! The house falls!\n🏆 Champion earns {winnings:,} points!\n👑 Victory pays 2:1 premium!\n🌟 Your patience rewarded magnificently!\n```", 
            inline=False
        )
        embed.color = discord.Color.from_rgb(255, 215, 0)  # Gold
        contributions[user_id] = contributions.get(user_id, 0) + winnings
        # Update lifetime earnings too since this is earning points
        lifetime_earnings[user_id] = lifetime_earnings.get(user_id, 0) + winnings
        
        # Track blackjack win achievement
        try:
            user_achievement = achievement_system.get_user_achievement(ctx.author.id, "blackjack_winner")
            blackjack_wins = user_achievement.progress.get("blackjack_wins", 0) + 1
            newly_unlocked = check_gaming_achievements(ctx.author.id, {"blackjack_wins": blackjack_wins})
            
            for achievement in newly_unlocked:
                await send_achievement_notification(bot, ctx.author, achievement)
                if achievement.reward_points > 0:
                    await add_contribution(ctx.author.id, achievement.reward_points * 10, ctx.channel, ctx.author)
        except Exception as e:
            logger.error(f"Error tracking blackjack achievement: {e}")
        
        # Check for Gambler role award (10k+ bet win)
        if bet >= 10000:
            await _award_gambler_role(ctx, bet)
            
    elif player_value > dealer_value:
        # Player wins
        winnings = bet * 2
        embed.add_field(
            name="🎉 👑 MASTERFUL TRIUMPH! 👑 🎉", 
            value=f"```yaml\n🎯 Superior hand claims victory!\n💎 Champion receives {winnings:,} points!\n🏆 Skill conquers chance!\n⚡ The crowd roars in approval!\n```", 
            inline=False
        )
        embed.color = discord.Color.from_rgb(255, 215, 0)  # Gold
        await add_points_direct(user_id, winnings)
        
        # Track blackjack win achievement
        try:
            user_achievement = achievement_system.get_user_achievement(ctx.author.id, "blackjack_winner")
            blackjack_wins = user_achievement.progress.get("blackjack_wins", 0) + 1
            newly_unlocked = check_gaming_achievements(ctx.author.id, {"blackjack_wins": blackjack_wins})
            
            for achievement in newly_unlocked:
                await send_achievement_notification(bot, ctx.author, achievement)
                if achievement.reward_points > 0:
                    await add_contribution(ctx.author.id, achievement.reward_points * 10, ctx.channel, ctx.author)
        except Exception as e:
            logger.error(f"Error tracking blackjack achievement: {e}")
        
        # Check for Gambler role award (10k+ bet win)
        if bet >= 10000:
            await _award_gambler_role(ctx, bet)
        
    elif player_value == dealer_value:
        # Push
        embed.add_field(
            name="🤝 ⚖️ HONORABLE DRAW! ⚖️ 🤝", 
            value=f"```yaml\n🎭 Perfect balance achieved!\n⚖️ Equal hands, equal honor\n💰 Stake returned with respect\n🌟 A contest of true equals!\n```", 
            inline=False
        )
        embed.color = discord.Color.from_rgb(255, 165, 0)  # Orange
        await add_points_direct(user_id, bet)
    else:
        # Dealer wins
        embed.add_field(
            name="💀 🎰 HOUSE SUPREMACY 🎰 💀", 
            value=f"```diff\n- The house edge prevails today\n- Your challenge was valiant\n- Fortune favors the patient\n- Return stronger, brave challenger\n```", 
            inline=False
        )
        embed.color = discord.Color.from_rgb(139, 0, 0)  # Dark red
    
    await save_contributions_async(contributions)
    
    # Show final balance with enhanced styling
    final_points = contributions.get(user_id, 0)
    embed.add_field(
        name="💰 👑 TREASURY STATUS 👑 💰",
        value=f"```yaml\n💎 Current Fortune: {final_points:,} points\n🏛️ Account stands in good standing\n⚡ Ready for your next adventure\n```",
        inline=False
    )
    
    # Enhanced footer with final touches
    embed.set_footer(
        text="🎰 StarChan Royal Casino • Where legends are forged in cards and courage! 👑", 
        icon_url=ctx.author.avatar.url if ctx.author.avatar else None
    )
    
    # Add final visual separator
    embed.add_field(name="✨ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ ✨", value="*Thank you for the thrilling game!*", inline=False)
    
    await game_message.edit(embed=embed)
    

async def save_contributions_async(data: Dict[str, int]):
    """Save contributions asynchronously with error handling."""
    try:
        async with contrib_lock:
            save_contributions(data)
            logger.debug(f"Async saved contributions for {len(data)} users")
    except Exception as e:
        logger.error(f"Error saving contributions async: {e}")

async def save_lifetime_earnings_async(data: Dict[str, int]):
    """Save lifetime earnings asynchronously with error handling."""
    try:
        async with contrib_lock:
            save_lifetime_earnings(data)
            logger.debug(f"Async saved lifetime earnings for {len(data)} users")
    except Exception as e:
        logger.error(f"Error saving lifetime earnings async: {e}")

async def add_points_direct(user_id: str, points: int):
    """Add points directly to both current balance and lifetime earnings."""
    # Add to current balance (spendable)
    contributions[user_id] = contributions.get(user_id, 0) + points
    # Add to lifetime earnings (for level calculation)
    lifetime_earnings[user_id] = lifetime_earnings.get(user_id, 0) + points
    # Add to weekly contributions
    WeeklyContributionManager.add_weekly_points(user_id, points)
    # Save both files
    await save_contributions_async(contributions)
    await save_lifetime_earnings_async(lifetime_earnings)

async def _award_gambler_role(ctx, bet_amount: int):
    """Award the Gambler role for winning a high-stakes blackjack game."""
    try:
        gambler_role_name = "🎲Gambler🎲"
        gambler_role = discord.utils.get(ctx.guild.roles, name=gambler_role_name)
        
        # Create the role if it doesn't exist
        if not gambler_role:
            try:
                gambler_role = await ctx.guild.create_role(
                    name=gambler_role_name,
                    color=discord.Color.from_rgb(255, 215, 0),  # Gold color for gambling
                    reason="Created Gambler role for high-stakes blackjack winners"
                )
                logger.info(f"Created Gambler role in guild {ctx.guild.id}")
            except discord.Forbidden:
                logger.error(f"No permission to create Gambler role in guild {ctx.guild.id}")
                return
        
        # Check if user already has this role
        if gambler_role in ctx.author.roles:
            logger.info(f"User {ctx.author.id} already has Gambler role")
            return
        
        # Check if bot can assign the role
        if gambler_role.position >= ctx.guild.me.top_role.position:
            logger.error(f"Bot cannot assign Gambler role - insufficient permissions in guild {ctx.guild.id}")
            return
        
        # Award the role
        await ctx.author.add_roles(gambler_role, reason=f"Won blackjack with {bet_amount:,} point high-stakes bet")
        
        # Send achievement notification
        achievement_embed = discord.Embed(
            title="🎲 🏆 LEGENDARY GAMBLER ACHIEVEMENT! 🏆 🎲",
            description=f"**{ctx.author.mention} has earned the prestigious Gambler role!**",
            color=discord.Color.from_rgb(255, 215, 0)
        )
        
        achievement_embed.add_field(
            name="🎯 Achievement Unlocked",
            value=f"```yaml\n🎲 High-Stakes Champion\n💰 Won blackjack with {bet_amount:,} points\n🏆 Nerves of steel proven!\n👑 True gambling legend!\n```",
            inline=False
        )
        
        achievement_embed.add_field(
            name="🎭 Role Awarded",
            value=f"**{gambler_role_name}**\n*Master of high-stakes gambling - Won blackjack with 10k+ bet*",
            inline=False
        )
        
        achievement_embed.set_thumbnail(url=ctx.author.display_avatar.url if ctx.author.display_avatar else None)
        achievement_embed.set_footer(text="🎰 StarChan Casino • Where legends are born! 🎲")
        
        await ctx.send(embed=achievement_embed)
        logger.info(f"Awarded Gambler role to {ctx.author.id} ({ctx.author.name}) for {bet_amount:,} point blackjack win")
        
    except Exception as e:
        logger.error(f"Error awarding Gambler role: {e}")


async def add_contribution(user_id: int, amount: int, channel: Optional[discord.TextChannel] = None, member: Optional[discord.Member] = None):
    """Add contribution points to a user with role multiplier support."""
    user_id_str = str(user_id)
    
    # Check for special role multipliers if member is provided
    actual_amount = amount
    if member:
        # Check for Star Contributor status (2x multiplier)
        if PermissionHelper.is_star_contributor(member):
            actual_amount = amount * 2  # 2x points for Star Contributors
            logger.info(f"Star Contributor multiplier applied: User {user_id} received {actual_amount} points (base {amount} x2)")
    
    # Add to current balance (spendable)
    contributions[user_id_str] = contributions.get(user_id_str, 0) + actual_amount
    # Add to lifetime earnings (for level calculation)
    lifetime_earnings[user_id_str] = lifetime_earnings.get(user_id_str, 0) + actual_amount
    
    # Save both files
    save_contributions(contributions)
    save_lifetime_earnings(lifetime_earnings)
    
    # Also add to weekly tracking
    WeeklyContributionManager.add_weekly_points(user_id_str, actual_amount)


async def find_suitable_channel(guild: discord.Guild, member: discord.Member, preferred_channel: Optional[discord.TextChannel] = None) -> Optional[discord.TextChannel]:
    """Find a suitable channel to send messages with error handling."""
    try:
        # Use preferred channel if valid
        if (preferred_channel and 
            hasattr(preferred_channel, "send") and 
            preferred_channel.permissions_for(guild.me).send_messages):
            return preferred_channel
        
        # Try to find the most recent channel the user spoke in
        # Import BOT_CONFIG to get forbidden channel IDs
        from bot_utils import BOT_CONFIG
        forbidden_channel_ids = BOT_CONFIG.get("FORBIDDEN_CHANNEL_IDS", [
            000000000000000000,  # Replace with channels where bot shouldn't work (like rules)
            000000000000000000   # Add more forbidden channel IDs as needed
        ])
        try:
            for text_channel in guild.text_channels:
                if (not text_channel.permissions_for(guild.me).read_message_history or
                    text_channel.id in forbidden_channel_ids):
                    continue
                async for message in text_channel.history(limit=100):
                    if message.author.id == member.id:
                        if text_channel.permissions_for(guild.me).send_messages:
                            return text_channel
                        break
        except discord.HTTPException:
            pass  # Continue if we can't read history
        
        # Find any suitable channel
        for channel in guild.text_channels:
            if (channel.permissions_for(member).read_messages and
                channel.permissions_for(guild.me).send_messages and
                channel != guild.rules_channel and
                channel != guild.system_channel and
                channel.id not in forbidden_channel_ids):
                return channel
        
        # Last resort: system or rules channel (but not the forbidden channels)
        for channel in [guild.system_channel, guild.rules_channel]:
            if (channel and 
                channel.permissions_for(guild.me).send_messages and
                channel.id not in forbidden_channel_ids):
                return channel
                
        return None
        
    except Exception as e:
        logger.error(f"Error finding suitable channel: {e}")
        return None

async def send_levelup_embed(channel: discord.TextChannel, member: discord.Member, level: int):
    """Send level up embed with error handling."""
    try:
        # Import BOT_CONFIG to get forbidden and forced channel IDs
        from bot_utils import BOT_CONFIG
        forbidden_channel_ids = BOT_CONFIG.get("FORBIDDEN_CHANNEL_IDS", [
            000000000000000000,  # Replace with channels where bot shouldn't work (like rules)
            000000000000000000   # Add more forbidden channel IDs as needed
        ])
        
        # Force the level up message to always post in the configured channel
        forced_channel_id = BOT_CONFIG.get("FORCED_LEVELUP_CHANNEL_ID", 000000000000000000)
        forced_channel = bot.get_channel(forced_channel_id)
        
        # Only use forced channel if it exists and is not in the forbidden channels
        if forced_channel is not None and forced_channel.id not in forbidden_channel_ids:
            channel = forced_channel
        elif channel.id in forbidden_channel_ids:
            # If the current channel is a forbidden channel, find an alternative
            guild = channel.guild
            alternative_channel = None
            
            # Try to find a suitable alternative channel
            for text_channel in guild.text_channels:
                if (text_channel.id not in forbidden_channel_ids and
                    text_channel.permissions_for(member).read_messages and
                    text_channel.permissions_for(guild.me).send_messages):
                    alternative_channel = text_channel
                    break
            
            if alternative_channel:
                channel = alternative_channel
            else:
                # If no alternative found, don't send the message
                logger.warning(f"Could not find suitable channel for level up message, skipping for {member}")
                return

        embed = discord.Embed(
            title="🎉 Level Up! 🎉",
            description=f"{member.mention} has reached **Level {level}**!",
            color=discord.Color.gold()
        )
        
        avatar_url = member.avatar.url if member.avatar else member.default_avatar.url
        embed.set_thumbnail(url=avatar_url)
        embed.add_field(name="Congratulations!", value="Keep up the great work!", inline=False)
        embed.set_footer(text="StarChan Level System")
        
        await channel.send(embed=embed)
        logger.info(f"Level up embed sent for {member} (Level {level}) in channel {channel.name}")
        
    except discord.HTTPException as e:
        logger.error(f"Failed to send level up embed: {e}")
    except Exception as e:
        logger.error(f"Error in send_levelup_embed: {e}")
        logger.error(traceback.format_exc())

def get_level(points: int) -> int:
    """Calculate level based on points with input validation."""
    return LevelSystem.get_level(points)

def get_user_level(user_id: str) -> int:
    """Get a user's level based on their lifetime earnings."""
    lifetime_points = lifetime_earnings.get(user_id, 0)
    return LevelSystem.get_level(lifetime_points)


# =============================================================================
# DAILY RIDDLE COMMANDS
# =============================================================================

@bot.command(name='riddlemethis', aliases=['riddle', 'weeklyriddle'])
async def riddle_me_this(ctx, *, answer: str = None):
    """
    Weekly riddle challenge! Solve the riddle to earn 3,000 contribution points.
    Only one person can win per week!
    Usage: !riddlemethis [answer]
    """
    try:
        # Import RiddleManager here to avoid circular imports
        from bot_utils import RiddleManager, DataManager
        
        # Load riddle state
        riddle_state = DataManager.load_riddle_state()
        current_riddle = RiddleManager.get_current_riddle(riddle_state)
        
        # If no answer provided, show the riddle
        if not answer:
            await _show_riddle(ctx, riddle_state, current_riddle)
            return
        
        # If riddle already solved this week
        if riddle_state.get("solved", False):
            winner_id = riddle_state.get("current_winner") or riddle_state.get("winner_id")
            if winner_id:
                try:
                    winner = await bot.fetch_user(winner_id)
                    winner_name = winner.display_name if winner else "Someone"
                except:
                    winner_name = "Someone"
                embed = EmbedHelper.create_info_embed(
                    "🏆 Riddle Already Solved!",
                    f"This week's riddle has already been solved by **{winner_name}**!\n\n"
                    f"🎁 They earned **3,000 contribution points**!\n"
                    f"⏰ Next riddle: **{RiddleManager.get_time_until_next_riddle()}**"
                )
            else:
                embed = EmbedHelper.create_info_embed(
                    "🏆 Riddle Already Solved!",
                    f"This week's riddle has already been solved!\n\n"
                    f"⏰ Next riddle: **{RiddleManager.get_time_until_next_riddle()}**"
                )
            await ctx.send(embed=embed)
            return
        
        # Check if user can attempt
        can_attempt, remaining = RiddleManager.can_attempt(ctx.author.id, riddle_state)
        if not can_attempt:
            embed = EmbedHelper.create_error_embed(
                "❌ No More Attempts",
                f"You've used all your attempts for today's riddle!\n\n"
                f"⏰ Next riddle available in: **{RiddleManager.get_time_until_next_riddle()}**"
            )
            await ctx.send(embed=embed)
            return
        
        # Check the answer
        if RiddleManager.check_answer(answer, current_riddle["answer"]):
            await _handle_correct_answer(ctx, riddle_state, current_riddle)
        else:
            await _handle_incorrect_answer(ctx, riddle_state, remaining - 1)
            
    except Exception as e:
        logger.error(f"Error in riddle command: {e}")
        embed = EmbedHelper.create_error_embed(
            "❌ Error",
            "Something went wrong with the riddle command. Please try again later."
        )
        await ctx.send(embed=embed)


async def _show_riddle(ctx, riddle_state, current_riddle):
    """Display the current riddle."""
    from bot_utils import RiddleManager
    
    user_attempts = riddle_state["attempts"].get(str(ctx.author.id), 0)
    remaining_attempts = 3 - user_attempts
    
    if riddle_state.get("solved", False):
        winner_id = riddle_state.get("current_winner")
        winner = bot.get_user(winner_id) if winner_id else None
        winner_text = f"\n🏆 **Solved by:** {winner.mention if winner else 'Someone'}" if winner_id else ""
        
        embed = EmbedHelper.create_success_embed(
            "🧩 Today's Riddle (SOLVED)",
            f"**{current_riddle['riddle']}**\n\n"
            f"✅ **Answer:** {current_riddle['answer'][0].title()}{winner_text}\n\n"
            f"⏰ Next riddle available in: **{RiddleManager.get_time_until_next_riddle()}**"
        )
    else:
        embed = EmbedHelper.create_info_embed(
            "🧩 Weekly Riddle Challenge",
            f"**{current_riddle['riddle']}**\n\n"
            f"🎯 **How to answer:** `!riddlemethis your answer here`\n"
            f"🎁 **Prize:** 3,000 contribution points!\n"
            f"⚠️ **Note:** Only ONE person can win per week!\n\n"
            f"⏰ Riddle resets: **{RiddleManager.get_time_until_next_riddle()}**"
        )
        
        # Add hint if some hints have been given
        hints_given = riddle_state.get("hints_given", 0)
        if hints_given > 0:
            embed.add_field(
                name="💡 Hint",
                value=current_riddle["hint"],
                inline=False
            )
    
    embed.set_footer(text="Daily riddle challenge • Solve to become VIP!")
    await ctx.send(embed=embed)


async def _handle_correct_answer(ctx, riddle_state, current_riddle):
    """Handle when user gives correct answer."""
    try:
        from bot_utils import RiddleManager, DataManager
        
        # Update riddle state
        riddle_state["solved"] = True
        riddle_state["current_winner"] = ctx.author.id
        riddle_state["winner_id"] = ctx.author.id
        riddle_state["winner_name"] = ctx.author.display_name
        RiddleManager.record_attempt(ctx.author.id, riddle_state)
        DataManager.save_json_file(DATA_FILES["RIDDLE_STATE"], riddle_state)
        
        # Award 3,000 contribution points instead of VIP role
        await add_contribution(ctx.author.id, 3000, ctx.channel, ctx.author)
        
        # Create success embed
        embed = EmbedHelper.create_success_embed(
            "🎉 CORRECT! Riddle Solved!",
            f"**Congratulations {ctx.author.mention}!**\n\n"
            f"🧩 **The answer was:** {current_riddle['answer'][0].title()}\n"
            f"🎁 **You've earned 3,000 contribution points!**\n\n"
            f"🏆 You are this week's riddle champion!"
        )
        embed.set_thumbnail(url=ctx.author.display_avatar.url if ctx.author.display_avatar else None)
        embed.set_footer(text=f"Next riddle available in: {RiddleManager.get_time_until_next_riddle()}")
        
        await ctx.send(embed=embed)
        
        # Log the achievement
        logger.info(f"User {ctx.author.id} ({ctx.author.name}) solved daily riddle")
        
    except Exception as e:
        logger.error(f"Error handling correct answer: {e}")
        embed = EmbedHelper.create_error_embed(
            "❌ Error",
            "You got the right answer, but there was an error awarding the prize. Please contact an admin."
        )
        await ctx.send(embed=embed)


async def _handle_incorrect_answer(ctx, riddle_state, remaining_attempts):
    """Handle when user gives incorrect answer."""
    from bot_utils import RiddleManager, DataManager
    
    RiddleManager.record_attempt(ctx.author.id, riddle_state)
    DataManager.save_json_file(DATA_FILES["RIDDLE_STATE"], riddle_state)
    
    if remaining_attempts > 0:
        embed = EmbedHelper.create_warning_embed(
            "❌ Incorrect Answer",
            f"Sorry {ctx.author.mention}, that's not correct.\n\n"
            f"🔄 **Attempts remaining:** {remaining_attempts}/3\n"
            f"💡 **Tip:** Think carefully and try again!\n\n"
            f"Use `!riddlemethis` to see the riddle again."
        )
    else:
        embed = EmbedHelper.create_error_embed(
            "❌ No More Attempts",
            f"Sorry {ctx.author.mention}, that's not correct and you've used all your attempts.\n\n"
            f"⏰ **Next riddle available in:** {RiddleManager.get_time_until_next_riddle()}\n"
            f"🍀 Better luck tomorrow!"
        )
    
    await ctx.send(embed=embed)


async def _award_vip_role(ctx):
    """Award the VIP role to the user."""
    try:
        vip_role = PermissionHelper.get_vip_role(ctx.guild)
        
        if not vip_role:
            # Try to create the VIP role if it doesn't exist
            try:
                vip_role = await ctx.guild.create_role(
                    name=BOT_CONFIG["VIP_ROLE_NAME"],
                    color=discord.Color.gold(),
                    reason="Created VIP role for daily riddle winners"
                )
                logger.info(f"Created VIP role in guild {ctx.guild.id}")
            except discord.Forbidden:
                logger.error(f"No permission to create VIP role in guild {ctx.guild.id}")
                return
        
        if vip_role and vip_role not in ctx.author.roles:
            await ctx.author.add_roles(vip_role, reason="Won daily riddle challenge")
            logger.info(f"Awarded VIP role to {ctx.author.id} in guild {ctx.guild.id}")
            
    except Exception as e:
        logger.error(f"Error awarding VIP role: {e}")


@bot.command(name='riddlehint')
async def riddle_hint(ctx):
    """Get a hint for the current riddle (owner only for now)."""
    if not PermissionHelper.is_bot_owner(ctx.author.id):
        embed = EmbedHelper.create_error_embed(
            "❌ Permission Denied",
            "Only the bot owner can give hints for now."
        )
        await ctx.send(embed=embed)
        return
    
    try:
        from bot_utils import RiddleManager, DataManager
        
        riddle_state = DataManager.load_riddle_state()
        current_riddle = RiddleManager.get_current_riddle(riddle_state)
        
        if riddle_state.get("solved", False):
            embed = EmbedHelper.create_info_embed(
                "🧩 Riddle Already Solved",
                "Today's riddle has already been solved!"
            )
            await ctx.send(embed=embed)
            return
        
        # Give hint and update state
        riddle_state["hints_given"] = riddle_state.get("hints_given", 0) + 1
        DataManager.save_json_file(DATA_FILES["RIDDLE_STATE"], riddle_state)
        
        embed = EmbedHelper.create_info_embed(
            "💡 Riddle Hint Released!",
            f"**Hint:** {current_riddle['hint']}\n\n"
            f"The hint has been added to the riddle display. "
            f"Use `!riddlemethis` to see the riddle with the hint!"
        )
        await ctx.send(embed=embed)
        
    except Exception as e:
        logger.error(f"Error in riddle hint command: {e}")
        embed = EmbedHelper.create_error_embed(
            "❌ Error",
            "Something went wrong. Please try again later."
        )
        await ctx.send(embed=embed)


@bot.command(name='riddlestatus', aliases=['riddleinfo'])
async def riddle_status(ctx):
    """Show current riddle status and user's attempts."""
    try:
        from bot_utils import RiddleManager, DataManager
        
        riddle_state = DataManager.load_riddle_state()
        user_attempts = riddle_state["attempts"].get(str(ctx.author.id), 0)
        remaining_attempts = 3 - user_attempts
        
        # Check if user has VIP role  
        is_vip = PermissionHelper.is_vip_member(ctx.author)
        vip_status = "⚜️ Yes" if is_vip else "❌ No"
        
        embed = EmbedHelper.create_info_embed(
            "🧩 Your Riddle Status",
            f"**Today's Status:**\n"
            f"🔄 Attempts used: {user_attempts}/3\n"
            f"🔄 Attempts remaining: {remaining_attempts}\n"
            f"⚜️ VIP Status: {vip_status}\n"
            f"🏆 Riddle solved: {'✅ Yes' if riddle_state.get('solved', False) else '❌ No'}\n\n"
            f"⏰ Next riddle: {RiddleManager.get_time_until_next_riddle()}"
        )
        
        if is_vip:
            embed.add_field(
                name="⚜️ VIP Benefits",
                value="• Special role color\n• Bragging rights!",
                inline=False
            )
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        logger.error(f"Error in riddle status command: {e}")
        embed = EmbedHelper.create_error_embed(
            "❌ Error",
            "Something went wrong. Please try again later."
        )
        await ctx.send(embed=embed)


# =============================================================================
# END DAILY RIDDLE COMMANDS
# =============================================================================


@bot.command(name="dmhelp", aliases=["dmcommands", "privatemessage"])
async def dm_help(ctx):
    """
    Show available commands for Direct Messages (DMs)
    Usage: !dmhelp
    """
    if isinstance(ctx.channel, discord.DMChannel):
        embed = discord.Embed(
            title="📬 StarChan DM Commands",
            description="Welcome to StarChan's Direct Message mode! 🎮\nHere are the commands you can use privately:",
            color=discord.Color.purple()
        )
        
        embed.add_field(
            name="🎯 Gaming Commands",
            value="🎮 `!tictactoe` - Play Tic-Tac-Toe against the bot\n"
                  "🃏 `!blackjack <bet>` - Play blackjack (requires points from server)\n"
                  "🎱 `!8ball <question>` - Ask the magic 8-ball\n"
                  "🔢 `!guessnumber` - Number guessing game\n"
                  "🎯 `!hangman` - Word guessing game with hangman drawings",
            inline=False
        )
        
        embed.add_field(
            name="🎭 Fun Commands",
            value="😺 `!cat` - Get a random cat image/message\n"
                  "🐶 `!doggo` - Get a random dog image/message\n"
                  "🤪 `!pun` - Hear a hilarious pun\n"
                  "🎭 `!dadjoke` - Get a dad joke",
            inline=False
        )
        
        embed.add_field(
            name="📊 Info Commands",
            value="🏅 `!achievements` - View your achievements\n"
                  "💰 `!balance` - Check your points\n"
                  "🔢 `!countingstatus` - Learn about the counting game\n"
                  "🆔 `!whatismyid` - Get your Discord ID\n"
                  "📜 `!credits` - Bot credits and info",
            inline=False
        )
        
        embed.add_field(
            name="💡 DM Special Features",
            value="✨ **Private Gaming**: Play games without server spam!\n"
                  "🏆 **Achievement Notifications**: Get notified here when you earn achievements!\n"
                  "🤖 **Bot Opponent**: Perfect for solo gaming sessions",
            inline=False
        )
        
        embed.add_field(
            name="🎯 Pro Tips",
            value="• Your points and progress carry over from the server\n"
                  "• Games played here still count for achievements\n"
                  "• Use `!tictactoe` for a fun bot challenge!\n"
                  "• Some commands may require server activity first",
            inline=False
        )
        
        embed.set_footer(text="📬 DM Mode • Enjoying private gaming with StarChan!")
    else:
        embed = discord.Embed(
            title="📬 DM Commands Info",
            description="This command shows DM-specific help. Try using it in a direct message with me!",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="💌 How to DM me:",
            value="1. Click on my profile\n2. Click 'Message'\n3. Use `!dmhelp` to see available commands",
            inline=False
        )
    
    await ctx.send(embed=embed)


@bot.command()
async def tictactoe(ctx, opponent: discord.Member = None):
    """
    Play a game of Tic-Tac-Toe with another user or against the bot!
    Usage: 
    - In server: !tictactoe @opponent (or !tictactoe for bot opponent)
    - In DMs: !tictactoe (automatically plays against bot)
    """
    # Check if command is used in DMs
    is_dm = isinstance(ctx.channel, discord.DMChannel)
    
    # Determine opponent
    if is_dm:
        # In DMs, always play against the bot
        if opponent is not None:
            await ctx.send("💬 **DM Mode**: In direct messages, you can only play against the bot!\n"
                          "Starting a game against StarChan Bot! 🤖")
        opponent = bot.user
        vs_bot = True
    else:
        # In server, use existing logic
        if opponent is None:
            # Play against bot
            opponent = bot.user
            vs_bot = True
        else:
            # Play against another user
            if opponent.bot and opponent != bot.user:
                await ctx.send("❌ You can only play against other users or the bot!")
                return
            if opponent == ctx.author:
                await ctx.send("❌ You can't play against yourself! Use `!tictactoe` to play against the bot. Trust me, I'm more fun than arguing with yourself! 🤖")
                return
            vs_bot = False

    # Initialize game
    board = ["⬜"] * 9
    players = [ctx.author, opponent]
    symbols = ["❌", "⭕"]
    current_player = 0
    
    def format_board():
        """Format the board for display with position numbers."""
        display_board = []
        for i in range(9):
            if board[i] == "⬜":
                display_board.append(f"{i+1}️⃣")
            else:
                display_board.append(board[i])
        
        return (
            f"{display_board[0]}{display_board[1]}{display_board[2]}\n"
            f"{display_board[3]}{display_board[4]}{display_board[5]}\n"
            f"{display_board[6]}{display_board[7]}{display_board[8]}"
        )
    
    def check_winner():
        """Check if there's a winner."""
        win_patterns = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Rows
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columns
            [0, 4, 8], [2, 4, 6]              # Diagonals
        ]
        
        for pattern in win_patterns:
            if (board[pattern[0]] == board[pattern[1]] == board[pattern[2]] != "⬜"):
                return board[pattern[0]]
        return None
    
    def is_board_full():
        """Check if the board is full."""
        return "⬜" not in board
    
    def get_available_moves():
        """Get list of available moves."""
        return [i for i, cell in enumerate(board) if cell == "⬜"]
    
    def bot_move():
        """Bot makes a move using basic AI."""
        available = get_available_moves()
        if not available:
            return None
        
        # Check for winning move
        for move in available:
            board[move] = symbols[1]  # Bot's symbol
            if check_winner() == symbols[1]:
                board[move] = "⬜"  # Reset for actual move
                return move
            board[move] = "⬜"  # Reset
        
        # Check for blocking move
        for move in available:
            board[move] = symbols[0]  # Player's symbol
            if check_winner() == symbols[0]:
                board[move] = "⬜"  # Reset for actual move
                return move
            board[move] = "⬜"  # Reset
        
        # Take center if available
        if 4 in available:
            return 4
        
        # Take corners
        corners = [0, 2, 6, 8]
        corner_moves = [move for move in available if move in corners]
        if corner_moves:
            return random.choice(corner_moves)
        
        # Take any available move
        return random.choice(available)
    
    # Create initial embed with appropriate title for DM vs Server
    game_title = f"🎮 Tic-Tac-Toe {'(DM Mode)' if is_dm else 'Game'} 🎮"
    embed = discord.Embed(
        title=game_title,
        description=f"**{players[0].display_name}** (❌) vs **{players[1].display_name}** (⭕)",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="📋 Game Board",
        value=format_board(),
        inline=False
    )
    
    if vs_bot:
        play_instructions = "React with 1️⃣-9️⃣ to make your move!\nYou are ❌, Bot is ⭕"
        if is_dm:
            play_instructions += "\n💬 **DM Game**: Enjoy private gaming with StarChan!"
        
        embed.add_field(
            name="🎯 How to Play",
            value=play_instructions,
            inline=False
        )
        embed.add_field(
            name="🤖 Current Turn",
            value=f"{players[current_player].display_name}'s turn!",
            inline=False
        )
    else:
        embed.add_field(
            name="🎯 How to Play",
            value="React with 1️⃣-9️⃣ to make your move!\nTake turns placing your symbols!",
            inline=False
        )
        embed.add_field(
            name="👤 Current Turn",
            value=f"{players[current_player].mention}'s turn!",
            inline=False
        )
    
    # Send game message and add reactions
    game_message = await ctx.send(embed=embed)
    
    # Add number reactions
    number_emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]
    for emoji in number_emojis:
        await game_message.add_reaction(emoji)
    
    # Game loop
    game_over = False
    moves_made = 0
    
    while not game_over and moves_made < 9:
        if vs_bot and current_player == 1:
            # Bot's turn
            await asyncio.sleep(1)  # Thinking time
            move = bot_move()
            if move is not None:
                board[move] = symbols[current_player]
                moves_made += 1
                
                # Update embed
                embed.set_field_at(0, name="📋 Game Board", value=format_board(), inline=False)
                
                winner = check_winner()
                if winner:
                    embed.color = discord.Color.green() if winner == symbols[0] else discord.Color.red()
                    winner_text = f"Winner: {players[0].display_name if is_dm else players[0].mention} ({winner})" if winner == symbols[0] else f"Winner: Bot ({winner})"
                    embed.set_field_at(2, name="🎉 Game Over!", 
                                     value=winner_text, 
                                     inline=False)
                    game_over = True
                elif is_board_full():
                    embed.color = discord.Color.gold()
                    embed.set_field_at(2, name="🤝 Game Over!", value="It's a draw!", inline=False)
                    game_over = True
                else:
                    current_player = 0
                    player_ref = players[current_player].display_name if is_dm else players[current_player].mention
                    embed.set_field_at(2, name="🤖 Current Turn", value=f"{player_ref}'s turn!", inline=False)
                
                await game_message.edit(embed=embed)
        else:
            # Human player's turn
            def check_reaction(reaction, user):
                return (
                    user == players[current_player] and 
                    reaction.message.id == game_message.id and
                    str(reaction.emoji) in number_emojis
                )
            
            try:
                reaction, user = await bot.wait_for("reaction_add", timeout=60.0, check=check_reaction)
                
                # Get move from reaction
                move = number_emojis.index(str(reaction.emoji))
                
                # Check if move is valid
                if board[move] == "⬜":
                    board[move] = symbols[current_player]
                    moves_made += 1
                    
                    # Remove the reaction
                    try:
                        await game_message.remove_reaction(reaction.emoji, user)
                    except:
                        pass
                    
                    # Update embed
                    embed.set_field_at(0, name="📋 Game Board", value=format_board(), inline=False)
                    
                    # Check for winner
                    winner = check_winner()
                    if winner:
                        winner_player = players[0] if winner == symbols[0] else players[1]
                        embed.color = discord.Color.green()
                        # Use display_name for DMs, mention for server
                        winner_ref = winner_player.display_name if is_dm else winner_player.mention
                        embed.set_field_at(2, name="🎉 Game Over!", 
                                         value=f"Winner: {winner_ref} ({winner})", 
                                         inline=False)
                        game_over = True
                        
                        # Award points to winner (only in server context or if playing vs bot)
                        if not is_dm or vs_bot:
                            if not vs_bot or winner == symbols[0]:
                                await add_contribution(winner_player.id, 10)
                    elif is_board_full():
                        embed.color = discord.Color.gold()
                        embed.set_field_at(2, name="🤝 Game Over!", value="It's a draw!", inline=False)
                        game_over = True
                        
                        # Award points for draw (only in server context or if playing vs bot)
                        if not is_dm or vs_bot:
                            if not vs_bot:
                                await add_contribution(players[0].id, 5)
                                await add_contribution(players[1].id, 5)
                            else:
                                await add_contribution(players[0].id, 5)
                    else:
                        # Switch turns
                        current_player = 1 - current_player
                        if vs_bot and current_player == 1:
                            turn_text = "🤖 Bot's turn!"
                        else:
                            # Use display_name for DMs, mention for server
                            player_ref = players[current_player].display_name if is_dm else players[current_player].mention
                            turn_text = f"{player_ref}'s turn!"
                        embed.set_field_at(2, name="👤 Current Turn", value=turn_text, inline=False)
                    
                    await game_message.edit(embed=embed)
                else:
                    # Invalid move - remove reaction
                    try:
                        await game_message.remove_reaction(reaction.emoji, user)
                    except:
                        pass
                    
            except asyncio.TimeoutError:
                embed.color = discord.Color.orange()
                player_ref = players[current_player].display_name if is_dm else players[current_player].mention
                embed.set_field_at(2, name="⏰ Game Timeout!", 
                                 value=f"{player_ref} took too long!", 
                                 inline=False)
                await game_message.edit(embed=embed)
                game_over = True
    
    # Track tictactoe achievements for both players
    try:
        for i, player in enumerate(players):
            if player.bot:  # Skip bot players
                continue
                
            # Track game participation
            user_achievement = achievement_system.get_user_achievement(player.id, "first_tictactoe")
            current_games = user_achievement.progress.get("tictactoe_games", 0) + 1
            
            # Update progress for playing a game and check if achievement unlocked
            if achievement_system.check_achievement(player.id, "first_tictactoe", {"tictactoe_games": current_games}):
                achievement = achievement_system.achievements["first_tictactoe"]
                await send_achievement_notification(bot, player, achievement)
                if achievement.reward_points > 0:
                    await add_contribution(player.id, achievement.reward_points * 10, ctx.channel)
            
            # Track wins if this player won
            if winner and winner == symbols[i]:
                win_achievements = ["tictactoe_winner", "tictactoe_master"]
                for ach_id in win_achievements:
                    user_achievement = achievement_system.get_user_achievement(player.id, ach_id)
                    current_wins = user_achievement.progress.get("tictactoe_wins", 0) + 1
                    
                    if achievement_system.check_achievement(player.id, ach_id, {"tictactoe_wins": current_wins}):
                        achievement = achievement_system.achievements[ach_id]
                        await send_achievement_notification(bot, player, achievement)
                        if achievement.reward_points > 0:
                            await add_contribution(player.id, achievement.reward_points * 10, ctx.channel)
    
    except Exception as e:
        logger.error(f"Error tracking tictactoe achievements: {e}")
    
    # Clean up reactions
    try:
        await game_message.clear_reactions()
    except:
        pass

@bot.command(name="whatismyid")
async def whatismyid(ctx, member: discord.Member = None):
    """
    Show your Discord user ID (or another user's if mentioned).
    Usage: !whatismyid [@user]
    """
    member = member or ctx.author
    await ctx.send(f"{member.mention}, your user ID is: `{member.id}`")


@bot.command(name="pingservertime")
async def pingservertime(ctx):
    """
    Show the current server time where the bot is running.
    Usage: !pingservertime
    
    This helps you understand when daily resets occur (00:00 server time).
    """
    try:
        # Get current server time
        now = datetime.datetime.now()
        
        # Format the time nicely
        formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
        weekday = now.strftime("%A")
        
        # Create embed with server time info
        embed = discord.Embed(
            title="🕐 Server Time Information",
            description="Current time where the bot is running",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="📅 Current Date & Time",
            value=f"```\n{formatted_time}\n{weekday}\n```",
            inline=False
        )
        
        embed.add_field(
            name="🌍 Server Location",
            value="🇩🇪 **Germany** (CET/CEST)\n"
                  "• Winter: UTC+1 (CET)\n"
                  "• Summer: UTC+2 (CEST)",
            inline=True
        )
        
        embed.add_field(
            name="⏰ Daily Reset Time",
            value="**00:00** German time\n"
                  "(Midnight server time)\n"
                  "This affects various daily features.",
            inline=True
        )
        
        # Add timezone info
        embed.add_field(
            name="🔄 Time Zone Info",
            value="All bot operations use **German local time**.\n"
                  "Use this time to calculate when daily features reset!",
            inline=False
        )
        
        # Add some visual elements
        embed.set_footer(
            text="💡 Tip: Daily features reset at 00:00 (midnight) server time!",
            icon_url=ctx.author.avatar.url if ctx.author.avatar else None
        )
        
        await ctx.send(embed=embed)
        logger.info(f"Server time check by {ctx.author}")
        
    except Exception as e:
        logger.error(f"Error in pingservertime command: {e}")
        await ctx.send("❌ Error getting server time. The time lords are on break! ⏰ Please try again later.")


@bot.command()
@cooldown(1, 600, BucketType.user)
async def leaderboard(ctx):
    """
    Show the top 10 contributors by weekly activity.
    Usage: !leaderboard
    """
    try:
        # Get weekly leaderboard data
        weekly_top = WeeklyContributionManager.get_weekly_leaderboard(10)
        
        if not weekly_top:
            embed = discord.Embed(
                title="🏆 Weekly Leaderboard",
                description="No contributions this week yet! Be the first to earn some points! 🚀",
                color=discord.Color.gold()
            )
            embed.add_field(
                name="💡 How to Earn Points",
                value="• Send messages in chat\n• Play games and complete achievements\n• Participate in counting games!",
                inline=False
            )
            embed.set_footer(text="Weekly leaderboard resets every Monday at 00:00 UTC")
            await ctx.send(embed=embed)
            return

        # Filter out users who are no longer in the guild
        valid_top = []
        for uid, points in weekly_top:
            member = ctx.guild.get_member(int(uid))
            if member:
                valid_top.append((uid, points, member))

        if not valid_top:
            await ctx.send("No valid contributors this week!")
            return

        # Get time until next week reset
        time_until_reset = WeeklyContributionManager.get_time_until_next_week()

        embed = discord.Embed(
            title="🏆 Weekly Top Contributors",
            description=f"✨ **This week's most active members!** ✨\n⏰ **Resets in:** {time_until_reset}",
            color=discord.Color.gold()
        )
        
        # Add leaderboard entries with elegant formatting
        leaderboard_text = ""
        for i, (uid, points, member) in enumerate(valid_top, 1):
            total_points = contributions.get(uid, 0)
            level = get_user_level(uid)  # Use lifetime earnings for level calculation
            
            if i == 1:
                medal = "🥇"
                rank_color = "**"
            elif i == 2:
                medal = "🥈"
                rank_color = "**"
            elif i == 3:
                medal = "🥉"
                rank_color = "**"
            else:
                medal = f"#{i}"
                rank_color = ""
            
            # Format member name with proper truncation
            display_name = member.display_name
            if len(display_name) > 20:
                display_name = display_name[:17] + "..."
            
            leaderboard_text += f"{medal} {rank_color}{display_name}{rank_color}\n"
            leaderboard_text += f"    📈 Weekly: **{points:,}** pts  💰 Balance: **{total_points:,}** pts  ⭐ Lv.{level}\n\n"
        
        embed.add_field(
            name="🎯 Current Rankings",
            value=leaderboard_text,
            inline=False
        )
        
        embed.set_footer(text="💡 Weekly points = activity this week • Balance = total lifetime points")
        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/741090849569824779.png")  # Trophy emoji
        await ctx.send(embed=embed)
        
    except Exception as e:
        logger.error(f"Error in leaderboard command: {e}")
        await ctx.send("❌ Error displaying leaderboard. Please try again later.")

@bot.command()
@cooldown(1, 1200, BucketType.user)
async def leaderboardmax(ctx):
    """
    Show the top 35 contributors by weekly activity.
    Usage: !leaderboardmax
    """
    try:
        # Get weekly leaderboard data
        weekly_top = WeeklyContributionManager.get_weekly_leaderboard(35)
        
        if not weekly_top:
            embed = discord.Embed(
                title="🏆 Extended Weekly Leaderboard",
                description="No contributions this week yet! Be the first to make your mark! 🌟",
                color=discord.Color.purple()
            )
            embed.add_field(
                name="💡 How to Climb the Rankings",
                value="• Stay active in chat\n• Complete achievements and challenges\n• Participate in community events!",
                inline=False
            )
            embed.set_footer(text="Weekly leaderboard resets every Monday at 00:00 UTC")
            await ctx.send(embed=embed)  
            return

        # Filter out users who are no longer in the guild
        valid_top = []
        for uid, points in weekly_top:
            member = ctx.guild.get_member(int(uid))
            if member:
                valid_top.append((uid, points, member))

        if not valid_top:
            await ctx.send("No valid contributors this week!")
            return

        # Get time until next week reset
        time_until_reset = WeeklyContributionManager.get_time_until_next_week()

        embed = discord.Embed(
            title="🏆 Extended Weekly Leaderboard",
            description=f"🌟 **Top 35 most dedicated members this week!** 🌟\n⏰ **Resets in:** {time_until_reset}",
            color=discord.Color.purple()
        )
        
        # Process entries in groups to handle Discord's 25 field limit
        entries_per_embed = 20  # Keep some room for better formatting
        fields_added = 0
        current_embed = embed
        
        for i, (uid, points, member) in enumerate(valid_top, 1):
            total_points = contributions.get(uid, 0)
            level = get_user_level(uid)  # Use lifetime earnings for level calculation
            
            # Get medal/rank display
            if i == 1:
                medal = "🥇"
            elif i == 2:
                medal = "🥈" 
            elif i == 3:
                medal = "🥉"
            elif i <= 10:
                medal = f"🏅 #{i}"
            else:
                medal = f"#{i}"
            
            # Format member name with proper truncation
            display_name = member.display_name
            if len(display_name) > 18:
                display_name = display_name[:15] + "..."
            
            current_embed.add_field(
                name=f"{medal} {display_name}",
                value=f"📈 **{points:,}** weekly pts\n💰 **{total_points:,}** balance\n⭐ Level {level}",
                inline=True
            )
            fields_added += 1
            
            # Check if we need to send current embed and create a new one
            if fields_added == entries_per_embed or i == len(valid_top):
                if i <= 35:  # Only add footer to the last embed
                    current_embed.set_footer(text="💡 Weekly = this week's activity • Balance = lifetime total points")
                
                await ctx.send(embed=current_embed)
                
                # Create new embed for continuation if needed
                if i < len(valid_top):
                    current_embed = discord.Embed(
                        title="🏆 Extended Weekly Leaderboard (continued)",
                        description=f"More of this week's top contributors! 📈",
                        color=discord.Color.purple()
                    )
                    fields_added = 0
                    
    except Exception as e:
        logger.error(f"Error in leaderboardmax command: {e}")
        await ctx.send("❌ Error displaying extended leaderboard. Please try again later.")


# Check your own level command
@bot.command(name="balance")
async def balance(ctx):
    """Show your own contribution points and level with error handling."""
    try:
        user_id = str(ctx.author.id)
        points = contributions.get(user_id, 0)  # Current spendable balance
        lifetime_points = lifetime_earnings.get(user_id, 0)  # Total earned for level
        level = get_user_level(user_id)  # Level based on lifetime earnings
        await ctx.send(f"{ctx.author.mention}, you have **{points:,}** contribution points (Level **{level}**) | Lifetime earned: **{lifetime_points:,}**")
        logger.debug(f"Balance check for {ctx.author}: {points} current, {lifetime_points} lifetime, level {level}")
    except Exception as e:
        logger.error(f"Error in balance: {e}")
        await ctx.send("❌ Error checking your level. Please try again later.")

# BUY COMMAND ---------------------------------------------------
@bot.command()
async def buy(ctx, *, role_name: str = None):
    """
    Buy a special role with contribution points!
    Usage: !buy [role_name]
    
    Roles available at various price points - use !shop to see all options!
    """
    try:
        # If no role specified, show available roles organized by price
        if not role_name:
            embed = discord.Embed(
                title="🛒 Role Shop",
                description="Purchase special roles with your contribution points!\n\n**Use `!shop` for detailed descriptions**",
                color=discord.Color.gold()
            )
            
            # Group roles by price tier
            price_tiers = {}
            for key, full_name in BUYABLE_ROLES.items():
                if full_name in SHOP_ROLES:
                    price = SHOP_ROLES[full_name]["price"]
                    if price not in price_tiers:
                        price_tiers[price] = []
                    price_tiers[price].append((key, full_name))
            
            # Sort by price (lowest to highest)
            for price in sorted(price_tiers.keys()):
                roles_at_price = price_tiers[price]
                role_list = "\n".join([f"• `!buy {key}`" for key, _ in roles_at_price])
                
                embed.add_field(
                    name=f"💰 {price:,} Points",
                    value=role_list,
                    inline=True
                )
            
            user_id = str(ctx.author.id)
            user_points = contributions.get(user_id, 0)
            embed.add_field(
                name="💎 Your Current Points",
                value=f"{user_points:,} contribution points",
                inline=False
            )
            
            embed.set_footer(text="Example: !buy electric samurai • Use !shop for detailed role info")
            await ctx.send(embed=embed)
            return
        
        # Normalize role name for lookup
        role_key = role_name.lower().strip()
        
        # Check if role exists
        if role_key not in BUYABLE_ROLES:
            await ctx.send(f"❌ Role '{role_name}' not found! Use `!buy` to see available roles.")
            return
        
        # Get the full role name and check if it's in shop
        role_name_full = BUYABLE_ROLES[role_key]
        if role_name_full not in SHOP_ROLES:
            await ctx.send(f"❌ Role '{role_name_full}' is not available for purchase!")
            return
        
        # Check if it's a special achievement role that can't be purchased
        role_info = SHOP_ROLES[role_name_full]
        if role_info.get("rarity") == "Special Achievement":
            await ctx.send(f"❌ The **{role_name_full}** role is a special achievement role and cannot be purchased!\n"
                          f"🎯 **How to earn it:** {role_info['description']}")
            return
        
        # Get role price from shop configuration
        role_price = SHOP_ROLES[role_name_full]["price"]
        
        # Get user's current points
        user_id = str(ctx.author.id)
        user_points = contributions.get(user_id, 0)
        
        # Check if user has enough points
        if user_points < role_price:
            needed = role_price - user_points
            await ctx.send(f"❌ You don't have enough points! You need {needed:,} more points to buy this role.\n"
                          f"💰 Your current points: {user_points:,}\n"
                          f"💎 Role price: {role_price:,} points")
            return
        
        # Find the role in the server
        role = discord.utils.get(ctx.guild.roles, name=role_name_full)
        
        if not role:
            await ctx.send(f"❌ Role '{role_name_full}' not found in this server! Please contact an admin.")
            logger.error(f"Role '{role_name_full}' not found in guild {ctx.guild.name}")
            return
        
        # Check if user already has this role
        if role in ctx.author.roles:
            await ctx.send(f"❌ You already have the {role_name_full} role!")
            return
        
        # Check if bot can assign the role
        if role.position >= ctx.guild.me.top_role.position:
            await ctx.send(f"❌ I don't have permission to assign the {role_name_full} role! Please contact an admin.")
            return
        
        # Deduct points and assign role
        new_points = user_points - role_price
        contributions[user_id] = new_points
        await save_contributions_async(contributions)
        
        # Assign the role
        await ctx.author.add_roles(role, reason=f"Purchased with {role_price:,} contribution points")
        
        # Track economy achievement
        try:
            user_achievement = achievement_system.get_user_achievement(ctx.author.id, "shopaholic")
            current_purchases = user_achievement.progress.get("purchases", 0) + 1
            total_spent = user_achievement.progress.get("total_spent", 0) + role_price
            
            newly_unlocked = check_economy_achievements(ctx.author.id, {
                "purchases": current_purchases,
                "total_spent": total_spent
            })
            
            for achievement in newly_unlocked:
                await send_achievement_notification(bot, ctx.author, achievement)
                
                if achievement.reward_points > 0:
                    await add_contribution(ctx.author.id, achievement.reward_points * 10, ctx.channel, ctx.author)
        
        except Exception as e:
            logger.error(f"Error tracking economy achievement: {e}")
        
        # Success message
        embed = discord.Embed(
            title="✅ Role Purchased Successfully!",
            description=f"{ctx.author.mention} has purchased the {role_name_full} role!",
            color=discord.Color.green()
        )
        
        embed.add_field(
            name="💸 Points Spent",
            value=f"{role_price:,} points",
            inline=True
        )
        
        embed.add_field(
            name="💰 Remaining Points",
            value=f"{new_points:,} points",
            inline=True
        )
        
        # Add role details
        role_info = SHOP_ROLES[role_name_full]
        embed.add_field(
            name="🎭 Role Details",
            value=f"**{role_info['rarity']}** {role_info['emoji']}\n{role_info['description']}",
            inline=False
        )
        
        embed.set_thumbnail(url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
        await ctx.send(embed=embed)
        
        logger.info(f"User {ctx.author} ({user_id}) purchased role '{role_name_full}' for {role_price:,} points")
        
    except discord.Forbidden:
        await ctx.send("❌ I don't have permission to assign roles! My hands are tied... metaphorically speaking! 🤝 Please contact an admin.")
    except Exception as e:
        logger.error(f"Error in buy command: {e}")
        await ctx.send("❌ An error occurred while processing your purchase. Please try again later.")


# SELL COMMAND ---------------------------------------------------
@bot.command(name='sell', aliases=['sellrole'])
@cooldown(1, 30, BucketType.user)  # 1 use per 30 seconds per user
async def sell_role(ctx, *, role_name: str = None):
    """
    Sell a role you own back to the shop for 50% of its original price.
    Usage: !sell <role name>
    Example: !sell meme lord
    
    You'll receive 50% of the role's original purchase price in contribution points.
    Special achievement roles cannot be sold.
    """
    try:
        if not role_name:
            embed = discord.Embed(
                title="💰 Role Selling System",
                description="**How to sell a role:**\n"
                f"`!sell <role name>`\n\n"
                "**Examples:**\n"
                f"• `!sell meme lord`\n"
                f"• `!sell night owl`\n"
                f"• `!sell electric samurai`\n\n"
                "💡 **You'll receive 50% of the original price back!**\n"
                f"📋 Use `!shop` to see role prices.",
                color=discord.Color.gold()
            )
            
            # Show user's sellable roles
            user_roles = [role.name for role in ctx.author.roles if role.name != "@everyone"]
            sellable_roles = []
            
            for role_display_name, role_data in SHOP_ROLES.items():
                if (role_display_name in user_roles and 
                    role_data.get("rarity") != "Special Achievement"):
                    sellable_roles.append(f"• **{role_display_name}** - Get {role_data['price'] // 2:,} points")
            
            if sellable_roles:
                embed.add_field(
                    name="🎭 Your Sellable Roles",
                    value="\n".join(sellable_roles[:10]),  # Limit to 10 roles
                    inline=False
                )
            else:
                embed.add_field(
                    name="🎭 Your Sellable Roles",
                    value="You don't own any sellable roles yet!\nUse `!shop` to buy some roles first.",
                    inline=False
                )
            
            await ctx.send(embed=embed)
            return

        # Load current contributions
        user_id = str(ctx.author.id)
        current_points = contributions.get(user_id, 0)
        
        # Find the role by searching through SHOP_ROLES
        role_name_lower = role_name.lower().strip()
        found_role_data = None
        found_role_display_name = None
        
        # Search through SHOP_ROLES to find matching role
        for role_display_name, role_data in SHOP_ROLES.items():
            # Flexible matching - check various forms
            role_clean = role_display_name.lower()
            # Remove common emojis to make matching easier
            role_clean_no_emojis = ''.join(c for c in role_clean if c.isalnum() or c.isspace())
            
            if (role_name_lower in role_clean or 
                role_name_lower == role_clean_no_emojis.strip() or
                any(role_name_lower == key.lower() for key, display in BUYABLE_ROLES.items() if display == role_display_name)):
                found_role_data = role_data
                found_role_display_name = role_display_name
                break
        
        if not found_role_data:
            embed = discord.Embed(
                title="❌ Role Not Found",
                description=f"Could not find a role matching '{role_name}'.\n\n"
                           "Use `!sell` without arguments to see your sellable roles.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        # Check if it's a special achievement role (cannot be sold)
        if found_role_data.get("rarity") == "Special Achievement":
            embed = discord.Embed(
                title="🚫 Cannot Sell Achievement Role",
                description=f"The **{found_role_display_name}** role is a special achievement role and cannot be sold!\n\n"
                           f"🏆 **How you earned it:** {found_role_data['description']}\n"
                           f"💡 Achievement roles are permanent rewards for your accomplishments.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        # Check if user actually has this role
        user_role = discord.utils.get(ctx.author.roles, name=found_role_display_name)
        if not user_role:
            embed = discord.Embed(
                title="❌ You Don't Own This Role",
                description=f"You don't currently have the **{found_role_display_name}** role.\n\n"
                           f"Use `!sell` to see roles you can sell.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        # Calculate sell price (50% of original)
        original_price = found_role_data["price"]
        sell_price = original_price // 2

        # Remove the role from user
        try:
            await ctx.author.remove_roles(user_role, reason=f"Sold role for {sell_price:,} contribution points")
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to remove that role! Please contact an admin.")
            return
        except Exception as e:
            logger.error(f"Error removing role in sell command: {e}")
            await ctx.send("❌ An error occurred while removing the role. Please try again later.")
            return

        # Add points to user
        new_points = current_points + sell_price
        contributions[user_id] = new_points
        # Note: Selling roles does NOT count towards weekly leaderboard (only earning activities do)
        await save_contributions_async(contributions)

        # Success message
        embed = discord.Embed(
            title="✅ Role Sold Successfully!",
            description=f"{ctx.author.mention} has sold the **{found_role_display_name}** role!",
            color=discord.Color.green()
        )
        
        embed.add_field(
            name="💰 Points Received",
            value=f"+{sell_price:,} points",
            inline=True
        )
        
        embed.add_field(
            name="💎 New Total",
            value=f"{new_points:,} points",
            inline=True
        )
        
        embed.add_field(
            name="📊 Original Price",
            value=f"{original_price:,} points",
            inline=True
        )

        # Add role details
        embed.add_field(
            name="🎭 Role Sold",
            value=f"**{found_role_display_name}**\n*{found_role_data['description']}*\n\n"
                  f"💡 You received 50% of the original price back!",
            inline=False
        )
        
        embed.set_thumbnail(url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
        embed.set_footer(text="💰 You can always buy it back later if you change your mind!")
        
        await ctx.send(embed=embed)
        
        logger.info(f"User {ctx.author} ({user_id}) sold role '{found_role_display_name}' for {sell_price:,} points")
        
    except Exception as e:
        logger.error(f"Error in sell command: {e}")
        await ctx.send("❌ An error occurred while processing your sale. Please try again later.")


@bot.event
async def on_ready():
    """Event handler for when bot is ready."""
    logger.info(f"Bot {bot.user} is ready!")
    
    # Load data from .txt files
    try:
        logger.info("Loading data from .txt files...")
        load_contributions()
        load_lifetime_earnings()
        logger.info(f"Data loaded: {len(contributions)} users with contributions, {len(lifetime_earnings)} users with earnings")
    except Exception as e:
        logger.error(f"Error loading data from .txt files: {e}")
    
    logger.info(f"Counting state loaded: current={counting_state.get('current', 0)}, channel_id={counting_state.get('channel_id')}")
    logger.info(f"Serving {len(bot.guilds)} guilds")

@bot.event
async def on_reaction_add(reaction, user):
    """Handle reaction additions with error handling and achievement tracking."""
    try:
        if not user.bot:
            await add_contribution(user.id, 1)  # +1 point per reaction
            
            # Track reaction achievements
            try:
                # Get current reaction stats
                first_reaction_progress = achievement_system.get_user_achievement(user.id, "first_reaction")
                reaction_enthusiast_progress = achievement_system.get_user_achievement(user.id, "reaction_enthusiast")
                
                reactions_added = reaction_enthusiast_progress.progress.get("reactions_added", 0) + 1
                
                # Check social achievements
                social_stats = {
                    "reactions_added": reactions_added,
                    "first_reaction": True  # They just added a reaction
                }
                
                newly_unlocked = check_social_achievements(user.id, social_stats)
                
                # Send achievement notifications
                for achievement in newly_unlocked:
                    await send_achievement_notification(bot, user, achievement)
                    if achievement.reward_points > 0:
                        try:
                            # Try to add contribution points in the same channel as the reaction
                            await add_contribution(user.id, achievement.reward_points * 10, reaction.message.channel)
                        except:
                            # If that fails, just log it
                            logger.info(f"Achievement points earned by {user.display_name}: {achievement.reward_points * 10}")
                            
            except Exception as achievement_error:
                logger.error(f"Error tracking reaction achievements for {user.display_name}: {achievement_error}")
                
    except Exception as e:
        logger.error(f"Error in on_reaction_add: {e}")


# SLAP COMMAND ---------------------------------------------------
@bot.command()
async def slap(ctx, member: discord.Member):
    """Slap a user with a funny gif! Usage: !slap @user"""
    try:
        from bot_utils import GIF_COLLECTIONS
        import random
        
        # Get a random slap GIF directly from the collection
        if "slap" in GIF_COLLECTIONS and GIF_COLLECTIONS["slap"]:
            gif_url = random.choice(GIF_COLLECTIONS["slap"])
            logger.info(f"Slap command: Using GIF URL: {gif_url}")
        else:
            gif_url = None
            logger.warning("Slap command: No slap GIFs found in collection")
        
        # Create embed with GIF
        embed = discord.Embed(
            description=f"{member.mention} just got slapped by {ctx.author.mention}! 👋💥",
            color=discord.Color.red()
        )
        
        if gif_url:
            embed.set_image(url=gif_url)
            logger.info(f"Slap command: Set image URL in embed: {gif_url}")
        else:
            logger.warning("Slap command: No GIF URL available, sending without image")
            
        embed.set_footer(text="Ouch! That's gotta hurt! 💥")
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        logger.error(f"Error in slap command: {e}")
        await ctx.send("❌ Something went wrong with the slap command!")
    
    # Track achievements (if you want to add slap achievements later)
    try:
        user_achievement = achievement_system.get_user_achievement(ctx.author.id, "slapper")
        current_slaps = user_achievement.progress.get("slaps_given", 0) + 1
        
        newly_unlocked = check_social_achievements(ctx.author.id, {"slaps_given": current_slaps})
        
        for achievement in newly_unlocked:
            await send_achievement_notification(bot, ctx.author, achievement)
            
            if achievement.reward_points > 0:
                await add_contribution(ctx.author.id, achievement.reward_points * 10, ctx.channel)
    
    except Exception as e:
        logger.error(f"Error tracking slap achievement: {e}")


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



@bot.event
async def on_error(event, *args, **kwargs):
    """Global error handler for bot events."""
    logger.error(f"Error in event {event}: {traceback.format_exc()}")

@bot.event
async def on_command_error(ctx, error):
    """Handle command errors gracefully."""
    try:
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"⏰ Command is on cooldown. Try again in {error.retry_after:.1f} seconds.")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You don't have permission to use this command.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"❌ Missing required argument: {error.param}")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("❌ Invalid argument provided.")
        elif isinstance(error, commands.CommandNotFound):
            # Silently ignore unknown commands
            pass
        else:
            logger.error(f"Unhandled command error in {ctx.command}: {error}")
            logger.error(traceback.format_exc())
            await ctx.send("❌ An unexpected error occurred. Please try again later.")
    except Exception as e:
        logger.error(f"Error in error handler: {e}")

# DOGGO COMMANDS ---------------------------------------------------
@bot.command()
async def doggo(ctx):
    """Sends a random gif of a dog! Usage: !doggo"""
    from bot_utils import GameHelpers
    gif_url = GameHelpers.get_random_gif("dog")
    
    # Create embed with GIF
    embed = discord.Embed(
        description="🐶 Here's your random doggo! 🐶",
        color=discord.Color.orange()
    )
    if gif_url:
        embed.set_image(url=gif_url)
    embed.set_footer(text="Who's a good boy? 🦴")
    
    await ctx.send(embed=embed)
    
    # Track command usage achievement
    try:
        # Get current usage counts
        user_achievement = achievement_system.get_user_achievement(ctx.author.id, "animal_lover")
        current_dog_uses = user_achievement.progress.get("dog_uses", 0) + 1
        current_cat_uses = user_achievement.progress.get("cat_uses", 0)
        
        # Check achievement with updated stats
        newly_unlocked = check_command_achievements(ctx.author.id, {
            "dog_uses": current_dog_uses,
            "cat_uses": current_cat_uses
        })
        
        # Send notifications for any newly unlocked achievements
        for achievement in newly_unlocked:
            await send_achievement_notification(bot, ctx.author, achievement)
            if achievement.reward_points > 0:
                await add_contribution(ctx.author.id, achievement.reward_points * 10, ctx.channel)
                
    except Exception as e:
        logger.error(f"Error tracking dog achievement: {e}")

@bot.command()
async def cat(ctx):
    """Sends a random gif of a cat! Usage: !cat"""
    from bot_utils import GameHelpers
    gif_url = GameHelpers.get_random_gif("cat")
    
    # Create embed with GIF
    embed = discord.Embed(
        description="🐱 Here's your random kitty! 🐱",
        color=discord.Color.purple()
    )
    if gif_url:
        embed.set_image(url=gif_url)
    embed.set_footer(text="Meow! 🐾")
    
    await ctx.send(embed=embed)
    
    # Track command usage achievement
    try:
        # Get current usage counts
        user_achievement = achievement_system.get_user_achievement(ctx.author.id, "animal_lover")
        current_cat_uses = user_achievement.progress.get("cat_uses", 0) + 1
        current_dog_uses = user_achievement.progress.get("dog_uses", 0)
        
        # Check achievement with updated stats
        newly_unlocked = check_command_achievements(ctx.author.id, {
            "cat_uses": current_cat_uses,
            "dog_uses": current_dog_uses
        })
        
        # Send notifications for any newly unlocked achievements
        for achievement in newly_unlocked:
            await send_achievement_notification(bot, ctx.author, achievement)
            if achievement.reward_points > 0:
                await add_contribution(ctx.author.id, achievement.reward_points * 10, ctx.channel)
                
    except Exception as e:
        logger.error(f"Error tracking cat achievement: {e}")

# ACHIEVEMENT SYSTEM COMMANDS ---------------------------------------------------
@bot.command(name='achievementstatus')
async def achievement_status(ctx):
    """Display comprehensive achievement system status."""
    try:
        # Clean up invalid users first
        cleanup_results = achievement_system.cleanup_invalid_users(ctx.guild)
        
        status = achievement_system.get_system_status()
        
        embed = discord.Embed(
            title="🏆 Achievement System Status",
            color=0x00ff00 if not status.get("error") and status.get("integrity_issues", 0) == 0 else 0xff9900
        )
        
        # Basic stats
        embed.add_field(
            name="📊 System Overview",
            value=f"**Total Achievements:** {status['total_achievements']}\n"
                  f"**Active Users:** {status['total_users']}\n"
                  f"**Total Unlocked:** {status['total_unlocked']}\n"
                  f"**Recent Unlocks (24h):** {status['recent_unlocks']}\n"
                  f"**Cleaned Up Users:** {cleanup_results.get('removed', 0)}",
            inline=True
        )
        
        # File status
        file_status = "✅" if status["data_file_exists"] else "❌"
        backup_status = "✅" if status["backup_file_exists"] else "❌"
        size_mb = status["data_file_size"] / 1024 / 1024 if status["data_file_size"] > 0 else 0
        
        embed.add_field(
            name="💾 File System",
            value=f"**Data File:** {file_status}\n"
                  f"**Backup File:** {backup_status}\n"
                  f"**File Size:** {size_mb:.2f} MB\n"
                  f"**Integrity Issues:** {status['integrity_issues']}",
            inline=True
        )
        
        # Category breakdown
        if status["categories"]:
            category_text = ""
            for category, data in status["categories"].items():
                percentage = (data["unlocked"] / data["total"]) * 100 if data["total"] > 0 else 0
                category_text += f"**{category.title()}:** {data['unlocked']}/{data['total']} ({percentage:.1f}%)\n"
            
            embed.add_field(
                name="📂 Categories",
                value=category_text,
                inline=False
            )
        
        # Health indicators
        health_color = "🟢"
        if status.get("error") or status.get("integrity_issues", 0) > 0:
            health_color = "🟡"
        if not status["data_file_exists"] or status.get("integrity_issues", 0) > 10:
            health_color = "🔴"
            
        embed.add_field(
            name=f"{health_color} System Health",
            value="System operating normally" if health_color == "🟢" else
                  "Minor issues detected" if health_color == "🟡" else
                  "Critical issues detected",
            inline=False
        )
        
        if status.get("error"):
            embed.add_field(
                name="⚠️ Error",
                value=f"```{status['error']}```",
                inline=False
            )
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send(f"❌ Error checking achievement system status: {str(e)}")

@bot.command(name='myachievements', aliases=['achievements', 'myach'])
async def my_achievements(ctx, page: int = 1):
    """View your achievements progress with premium interactive display."""
    try:
        user_stats = achievement_system.get_user_stats(ctx.author.id)
        user_achievements = achievement_system.get_user_achievements(ctx.author.id)
        
        # Get current user stats for accurate progress tracking
        current_stats = {}
        
        try:
            # Get message count and level
            user_messages = contributions.get(str(ctx.author.id), 0)
            current_stats["messages"] = user_messages
            current_stats["level"] = get_user_level(str(ctx.author.id))
            
            # Get current time info
            current_hour = datetime.datetime.now().hour
            current_stats["early_message"] = 5 <= current_hour <= 7
            current_stats["night_message"] = current_hour >= 23 or current_hour <= 3
            current_stats["midnight_message"] = current_hour == 0
            
            # Add guild member time data for time-based achievements
            if ctx.guild and ctx.author in ctx.guild.members:
                member = ctx.guild.get_member(ctx.author.id)
                if member and member.joined_at:
                    join_date = member.joined_at
                    now = datetime.datetime.now(datetime.timezone.utc)
                    days_in_server = (now - join_date).days
                    current_stats["days_in_server"] = days_in_server
                    current_stats["total_active_days"] = days_in_server
                    current_stats["consecutive_days"] = min(days_in_server, 30)
                    current_stats["weekend_messages"] = days_in_server >= 7
            
            # Get achievement progress from stored data (for command/game stats) 
            # combined with current stats (for message/level/time stats)
            for achievement_id in achievement_system.achievements:
                user_achievement = achievement_system.get_user_achievement(ctx.author.id, achievement_id)
                for key, value in user_achievement.progress.items():
                    if key not in current_stats:  # Don't override current real-time stats
                        current_stats[key] = value
                        
        except Exception as e:
            logger.error(f"Error getting current user stats for achievements list: {e}")
        
        # Get all achievements organized by category
        achievements_by_category = {}
        unlocked_achievements = []
        locked_achievements = []
        
        for achievement_id, achievement in achievement_system.achievements.items():
            category = achievement.category
            if category not in achievements_by_category:
                achievements_by_category[category] = {"unlocked": [], "locked": []}
            
            user_achievement = user_achievements.get(achievement_id)
            progress_info = achievement_system.get_achievement_progress(ctx.author.id, achievement_id, current_stats)
            
            achievement_data = {
                'achievement': achievement,
                'user_achievement': user_achievement,
                'progress': progress_info
            }
            
            if user_achievement and user_achievement.unlocked:
                achievements_by_category[category]["unlocked"].append(achievement_data)
                unlocked_achievements.append(achievement_data)
            else:
                achievements_by_category[category]["locked"].append(achievement_data)
                locked_achievements.append(achievement_data)
        
        # Pagination setup - Show categories with count
        categories = list(achievements_by_category.keys())
        categories.insert(0, "Overview")  # Add overview page
        total_pages = len(categories)
        
        if page < 1 or page > total_pages:
            page = 1
        
        def get_rarity_color(rarity_level):
            """Get color based on achievement rarity/difficulty."""
            colors = {
                "Common": discord.Color.green(),
                "Uncommon": discord.Color.blue(),
                "Rare": discord.Color.purple(),
                "Epic": discord.Color.orange(),
                "Legendary": discord.Color.gold(),
                "Mythic": discord.Color.magenta()
            }
            return colors.get(rarity_level, discord.Color.gold())
        
        def get_progress_bar(percentage):
            """Create a visual progress bar."""
            bar_length = 10
            filled = int(percentage / 10)
            empty = bar_length - filled
            return "🟦" * filled + "⬜" * empty
        
        def create_embed(current_page):
            """Create premium embed for the current page."""
            if current_page == 1:
                # Overview page
                embed = discord.Embed(
                    title="🏆 ✨ ACHIEVEMENT VAULT ✨ 🏆",
                    description=f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                    color=discord.Color.from_rgb(255, 215, 0)  # Gold
                )
                
                # Premium header with user info
                embed.add_field(
                    name="👑 🌟 CHAMPION PROFILE 🌟 👑",
                    value=f"```yaml\n🎯 Player: {ctx.author.display_name}\n🆔 ID: {ctx.author.id}\n⭐ Status: Achievement Hunter\n```",
                    inline=False
                )
                
                # Overall statistics with visual elements
                completion_bar = get_progress_bar(user_stats['completion_percentage'])
                embed.add_field(
                    name="📊 🏅 ACHIEVEMENT MASTERY 🏅 📊",
                    value=f"```yaml\n🏆 Unlocked: {user_stats['unlocked_count']}/{user_stats['total_count']} achievements\n"
                          f"📈 Progress: {user_stats['completion_percentage']:.1f}%\n"
                          f"💎 Total Points: {user_stats['total_points']:,}\n```\n"
                          f"**Progress Bar:** {completion_bar} `{user_stats['completion_percentage']:.1f}%`",
                    inline=False
                )
                
                # Category breakdown with premium styling
                category_text = ""
                for category in categories[1:]:  # Skip overview
                    cat_data = achievements_by_category[category]
                    unlocked_count = len(cat_data["unlocked"])
                    total_count = len(cat_data["unlocked"]) + len(cat_data["locked"])
                    percentage = (unlocked_count / total_count * 100) if total_count > 0 else 0
                    
                    # Category icons
                    category_icons = {
                        "Social": "👥", "Gaming": "🎮", "Special": "⭐", "Time": "⏰",
                        "Counting": "🔢", "Economy": "💰", "Commands": "⚡", "Messages": "💬"
                    }
                    icon = category_icons.get(category, "🏅")
                    
                    status = "🟢" if percentage == 100 else "🟡" if percentage >= 50 else "🔴"
                    category_text += f"{status} {icon} **{category}**: {unlocked_count}/{total_count} `({percentage:.0f}%)`\n"
                
                embed.add_field(
                    name="🗂️ 📋 CATEGORY BREAKDOWN 📋 🗂️",
                    value=category_text or "No categories available",
                    inline=False
                )
                
                # Recent achievements (last 3 unlocked)
                recent_unlocked = sorted(unlocked_achievements, 
                                       key=lambda x: x['user_achievement'].unlock_date or '', 
                                       reverse=True)[:3]
                
                if recent_unlocked:
                    recent_text = ""
                    for i, item in enumerate(recent_unlocked, 1):
                        achievement = item['achievement']
                        unlock_date = item['user_achievement'].unlock_date[:10] if item['user_achievement'].unlock_date else "Unknown"
                        recent_text += f"🏆 **{achievement.name}** {achievement.emoji}\n📅 Unlocked: {unlock_date}\n\n"
                    
                    embed.add_field(
                        name="🎉 🆕 RECENT VICTORIES 🆕 🎉",
                        value=recent_text[:1024],  # Discord field limit
                        inline=False
                    )
                
                # Navigation footer
                embed.add_field(name="━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", value="", inline=False)
                embed.set_footer(text="🎮 Use ⬅️➡️ to navigate categories • 🏆 Achievement Mastery System", 
                               icon_url=ctx.author.display_avatar.url if ctx.author.display_avatar else None)
                
            else:
                # Category pages
                current_category = categories[current_page - 1]
                category_achievements = achievements_by_category[current_category]
                
                # Category icons and colors
                category_setup = {
                    "Social": {"icon": "👥", "color": discord.Color.from_rgb(0, 191, 255), "desc": "Community & Interaction"},
                    "Gaming": {"icon": "🎮", "color": discord.Color.from_rgb(255, 20, 147), "desc": "Games & Entertainment"},
                    "Special": {"icon": "⭐", "color": discord.Color.from_rgb(255, 215, 0), "desc": "Rare & Exclusive"},
                    "Time": {"icon": "⏰", "color": discord.Color.from_rgb(138, 43, 226), "desc": "Time-based Challenges"},
                    "Counting": {"icon": "🔢", "color": discord.Color.from_rgb(30, 144, 255), "desc": "Counting Game Mastery"},
                    "Economy": {"icon": "💰", "color": discord.Color.from_rgb(255, 165, 0), "desc": "Points & Trading"},
                    "Commands": {"icon": "⚡", "color": discord.Color.from_rgb(255, 69, 0), "desc": "Bot Command Usage"},
                    "Messages": {"icon": "💬", "color": discord.Color.from_rgb(0, 250, 154), "desc": "Communication & Activity"}
                }
                
                category_info = category_setup.get(current_category, {"icon": "🏅", "color": discord.Color.gold(), "desc": "Achievement Category"})
                
                embed = discord.Embed(
                    title=f"{category_info['icon']} ✨ {current_category.upper()} ACHIEVEMENTS ✨ {category_info['icon']}",
                    description=f"**{category_info['desc']}**\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                    color=category_info['color']
                )
                
                # Show unlocked achievements first (premium styling)
                unlocked = category_achievements["unlocked"]
                locked = category_achievements["locked"]
                
                if unlocked:
                    unlocked_text = ""
                    for item in unlocked:
                        achievement = item['achievement']
                        user_achievement = item['user_achievement']
                        unlock_date = user_achievement.unlock_date[:10] if user_achievement.unlock_date else "Unknown"
                        
                        unlocked_text += f"✅ {achievement.emoji} **{achievement.name}**\n"
                        unlocked_text += f"💎 **{achievement.reward_points}** points • 📅 **{unlock_date}**\n"
                        unlocked_text += f"*{achievement.description}*\n\n"
                    
                    embed.add_field(
                        name="🏆 🎉 MASTERED ACHIEVEMENTS 🎉 🏆",
                        value=unlocked_text[:1024],  # Discord limit
                        inline=False
                    )
                
                if locked:
                    locked_text = ""
                    for item in locked:
                        achievement = item['achievement']
                        progress = item['progress']
                        
                        # Calculate overall progress
                        overall_percentage = 0
                        if progress and progress.get('progress'):
                            req_count = len(progress['progress'])
                            if req_count > 0:
                                total_percentage = sum(req_progress.get('percentage', 0) 
                                                     for req_progress in progress['progress'].values())
                                overall_percentage = total_percentage / req_count
                        
                        progress_bar = get_progress_bar(overall_percentage)
                        
                        locked_text += f"🔒 {achievement.emoji} **{achievement.name}**\n"
                        locked_text += f"💰 **{achievement.reward_points}** points • {progress_bar} `{overall_percentage:.0f}%`\n"
                        locked_text += f"*{achievement.description}*\n\n"
                    
                    embed.add_field(
                        name="🎯 🔓 AVAILABLE CHALLENGES 🔓 🎯",
                        value=locked_text[:1024],  # Discord limit
                        inline=False
                    )
                
                # Category statistics
                total_in_category = len(unlocked) + len(locked)
                category_percentage = (len(unlocked) / total_in_category * 100) if total_in_category > 0 else 0
                category_bar = get_progress_bar(category_percentage)
                
                embed.add_field(
                    name="📈 🏅 CATEGORY MASTERY 🏅 📈",
                    value=f"**Progress:** {category_bar} `{category_percentage:.1f}%`\n"
                          f"**Completed:** {len(unlocked)}/{total_in_category} achievements\n"
                          f"**Points Earned:** {sum(item['achievement'].reward_points for item in unlocked):,}",
                    inline=False
                )
                
                # Navigation footer
                embed.add_field(name="━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", value="", inline=False)
                embed.set_footer(text=f"🎮 Page {current_page}/{total_pages} • Use ⬅️➡️ to navigate • 🏆 Achievement System", 
                               icon_url=ctx.author.display_avatar.url if ctx.author.display_avatar else None)
            
            return embed
        
        # Send initial embed
        embed = create_embed(page)
        message = await ctx.send(embed=embed)
        
        # Add premium navigation reactions
        if total_pages > 1:
            reactions = ["⬅️", "➡️", "🏠", "❌"]  # Added home button
            for reaction in reactions:
                await message.add_reaction(reaction)
            
            def check_reaction(reaction, user):
                return (
                    user == ctx.author and 
                    reaction.message.id == message.id and
                    str(reaction.emoji) in reactions
                )
            
            current_page = page
            timeout_time = 300  # 5 minutes
            
            while True:
                try:
                    reaction, user = await bot.wait_for("reaction_add", timeout=timeout_time, check=check_reaction)
                    
                    # Remove the user's reaction
                    try:
                        await message.remove_reaction(reaction.emoji, user)
                    except:
                        pass
                    
                    if str(reaction.emoji) == "⬅️":
                        # Previous page
                        current_page = current_page - 1 if current_page > 1 else total_pages
                        embed = create_embed(current_page)
                        await message.edit(embed=embed)
                        
                    elif str(reaction.emoji) == "➡️":
                        # Next page
                        current_page = current_page + 1 if current_page < total_pages else 1
                        embed = create_embed(current_page)
                        await message.edit(embed=embed)
                        
                    elif str(reaction.emoji) == "🏠":
                        # Home (overview page)
                        current_page = 1
                        embed = create_embed(current_page)
                        await message.edit(embed=embed)
                        
                    elif str(reaction.emoji) == "❌":
                        # Close/remove reactions
                        try:
                            await message.clear_reactions()
                        except:
                            pass
                        break
                        
                except asyncio.TimeoutError:
                    # Remove reactions after timeout
                    try:
                        await message.clear_reactions()
                    except:
                        pass
                    break
        
    except Exception as e:
        logger.error(f"Error in my_achievements: {e}")
        await ctx.send(f"❌ Error retrieving achievements: {str(e)}")

@bot.command(name='achievement', aliases=['ach'])
async def view_achievement(ctx, *, achievement_name: str):
    """View detailed information about a specific achievement with premium styling."""
    try:
        # Find achievement by name (case insensitive)
        target_achievement = None
        for achievement_id, achievement in achievement_system.achievements.items():
            if achievement.name.lower() == achievement_name.lower():
                target_achievement = achievement
                break
        
        if not target_achievement:
            # Try partial match
            matches = []
            for achievement_id, achievement in achievement_system.achievements.items():
                if achievement_name.lower() in achievement.name.lower():
                    matches.append(achievement)
            
            if not matches:
                # Premium error embed
                embed = discord.Embed(
                    title="🔍 ❌ ACHIEVEMENT NOT FOUND ❌ 🔍",
                    description=f"```yaml\n❌ No achievement matching '{achievement_name}' was found.\n💡 Try using partial names or check spelling.\n```",
                    color=discord.Color.red()
                )
                embed.add_field(
                    name="💭 🎯 SEARCH TIPS 🎯 💭",
                    value="• Use `!achievements` to browse all achievements\n"
                          "• Try partial names (e.g., 'early' for 'Early Bird')\n"
                          "• Check spelling and capitalization\n"
                          "• Use `!listach` to see all achievement names",
                    inline=False
                )
                embed.set_footer(text="🏆 Achievement System • Type !achievements to explore")
                await ctx.send(embed=embed)
                return
                
            elif len(matches) > 1:
                # Premium multiple matches embed
                embed = discord.Embed(
                    title="🔍 ✨ MULTIPLE MATCHES FOUND ✨ 🔍",
                    description=f"Found **{len(matches)}** achievements matching `{achievement_name}`. Please be more specific:",
                    color=discord.Color.orange()
                )
                
                matches_text = ""
                for i, ach in enumerate(matches[:8], 1):  # Limit to 8 results
                    matches_text += f"**{i}.** {ach.emoji} **{ach.name}**\n"
                    matches_text += f"   📂 *{ach.category}* • 💎 *{ach.reward_points} points*\n\n"
                
                embed.add_field(
                    name="🎯 📋 ACHIEVEMENT MATCHES 📋 🎯",
                    value=matches_text,
                    inline=False
                )
                
                embed.add_field(
                    name="💡 🔧 HOW TO SELECT 🔧 💡",
                    value="Use the exact achievement name from the list above.\n"
                          "Example: `!achievement Early Bird`",
                    inline=False
                )
                
                embed.set_footer(text="🏆 Achievement System • Be more specific in your search")
                await ctx.send(embed=embed)
                return
            else:
                target_achievement = matches[0]
        
        # Get user's progress on this achievement
        user_achievement = achievement_system.get_user_achievement(ctx.author.id, target_achievement.id)
        progress_info = achievement_system.get_achievement_progress(ctx.author.id, target_achievement.id)
        
        # Determine achievement rarity/difficulty for color theming
        difficulty_colors = {
            0: discord.Color.green(),      # Easy (0-99 points)
            100: discord.Color.blue(),     # Medium (100-499 points)
            500: discord.Color.purple(),   # Hard (500-999 points)
            1000: discord.Color.orange(),  # Very Hard (1000+ points)
            2000: discord.Color.gold(),    # Legendary (2000+ points)
        }
        
        achievement_color = discord.Color.green()
        for threshold, color in sorted(difficulty_colors.items(), reverse=True):
            if target_achievement.reward_points >= threshold:
                achievement_color = color
                break
        
        # Premium achievement embed
        if user_achievement.unlocked:
            embed = discord.Embed(
                title=f"🏆 ✅ ACHIEVEMENT MASTERED ✅ 🏆",
                description=f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                color=discord.Color.gold()
            )
        else:
            embed = discord.Embed(
                title=f"🎯 🔒 ACHIEVEMENT CHALLENGE 🔒 🎯",
                description=f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                color=achievement_color
            )
        
        # Achievement header with premium styling
        status_icon = "🏆" if user_achievement.unlocked else "🔒"
        embed.add_field(
            name=f"{status_icon} {target_achievement.emoji} **{target_achievement.name}** {target_achievement.emoji} {status_icon}",
            value=f"```yaml\n💬 Description: {target_achievement.description}\n📂 Category: {target_achievement.category}\n💎 Reward: {target_achievement.reward_points:,} points\n```",
            inline=False
        )
        
        # Status section
        if user_achievement.unlocked:
            unlock_date = user_achievement.unlock_date[:19] if user_achievement.unlock_date else "Unknown"
            embed.add_field(
                name="🎉 ✨ ACHIEVEMENT STATUS ✨ 🎉",
                value=f"```diff\n+ STATUS: COMPLETED ✅\n+ UNLOCKED: {unlock_date}\n+ POINTS EARNED: {target_achievement.reward_points:,}\n```",
                inline=False
            )
        else:
            # Progress calculation
            overall_percentage = 0
            progress_details = []
            
            if progress_info and progress_info.get('progress'):
                req_count = len(progress_info['progress'])
                if req_count > 0:
                    total_percentage = 0
                    for req_name, req_data in progress_info['progress'].items():
                        current = req_data.get('current', 0)
                        required = req_data.get('required', 1)
                        percentage = req_data.get('percentage', 0)
                        total_percentage += percentage
                        
                        if isinstance(required, bool):
                            status = "✅" if current else "❌"
                            progress_details.append(f"{status} {req_name}")
                        else:
                            progress_bar = "🟦" * min(int(percentage / 10), 10) + "⬜" * max(0, 10 - int(percentage / 10))
                            progress_details.append(f"{progress_bar} {req_name}: {current:,}/{required:,}")
                    
                    overall_percentage = total_percentage / req_count
            
            main_progress_bar = "🟦" * min(int(overall_percentage / 10), 10) + "⬜" * max(0, 10 - int(overall_percentage / 10))
            
            embed.add_field(
                name="📊 🎯 PROGRESS TRACKING 🎯 📊",
                value=f"```yaml\n📈 Overall Progress: {overall_percentage:.1f}%\n```\n"
                      f"**Progress Bar:** {main_progress_bar} `{overall_percentage:.1f}%`",
                inline=False
            )
            
            # Detailed requirements
            if progress_details:
                requirements_text = "\n".join(progress_details[:10])  # Limit to 10 requirements
                embed.add_field(
                    name="📋 🔧 REQUIREMENTS BREAKDOWN 🔧 📋",
                    value=requirements_text,
                    inline=False
                )
        
        # Achievement category info with themed colors
        category_info = {
            "Social": {"icon": "👥", "desc": "Community & Interaction Mastery"},
            "Gaming": {"icon": "🎮", "desc": "Gaming & Entertainment Excellence"},
            "Special": {"icon": "⭐", "desc": "Rare & Exclusive Achievement"},
            "Time": {"icon": "⏰", "desc": "Time-based Challenge"},
            "Counting": {"icon": "🔢", "desc": "Counting Game Achievement"},
            "Economy": {"icon": "💰", "desc": "Economy & Trading Mastery"},
            "Commands": {"icon": "⚡", "desc": "Bot Command Mastery"},
            "Messages": {"icon": "💬", "desc": "Communication Achievement"}
        }
        
        cat_info = category_info.get(target_achievement.category, {"icon": "🏅", "desc": "Achievement Category"})
        
        embed.add_field(
            name=f"{cat_info['icon']} 📂 CATEGORY INFO 📂 {cat_info['icon']}",
            value=f"**{target_achievement.category}** - *{cat_info['desc']}*",
            inline=True
        )
        
        # Difficulty rating based on points
        if target_achievement.reward_points < 100:
            difficulty = "🟢 Easy"
        elif target_achievement.reward_points < 500:
            difficulty = "🔵 Medium"
        elif target_achievement.reward_points < 1000:
            difficulty = "🟣 Hard"
        elif target_achievement.reward_points < 2000:
            difficulty = "🟠 Very Hard"
        else:
            difficulty = "🟡 Legendary"
        
        embed.add_field(
            name="⚡ 🎖️ DIFFICULTY 🎖️ ⚡",
            value=difficulty,
            inline=True
        )
        
        # Tips section for locked achievements
        if not user_achievement.unlocked and progress_details:
            embed.add_field(
                name="💡 🚀 SUCCESS TIPS 🚀 💡",
                value="• Check your progress regularly with `!achievements`\n"
                      "• Focus on incomplete requirements\n"
                      "• Some achievements unlock through gameplay\n"
                      "• Ask in chat if you need help understanding requirements",
                inline=False
            )
        
        # Footer with user info
        embed.add_field(name="━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", value="", inline=False)
        embed.set_footer(
            text=f"🏆 Achievement System • Requested by {ctx.author.display_name}",
            icon_url=ctx.author.display_avatar.url if ctx.author.display_avatar else None
        )
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        logger.error(f"Error in achievement command: {e}")
        embed = discord.Embed(
            title="❌ 🔧 SYSTEM ERROR 🔧 ❌",
            description=f"```yaml\n❌ Error retrieving achievement information\n🔧 Technical Details: {str(e)}\n💡 Please try again later\n```",
            color=discord.Color.red()
        )
        embed.set_footer(text="🏆 Achievement System • Error occurred")
        await ctx.send(embed=embed)
        
        # Progress info
        if user_achievement.unlocked:
            embed.add_field(
                name="✅ Status",
                value="**COMPLETED!**",
                inline=False
            )
            if user_achievement.unlock_date:
                embed.add_field(
                    name="📅 Unlocked",
                    value=user_achievement.unlock_date[:10],
                    inline=True
                )
        else:
            embed.add_field(
                name="📊 Progress",
                value=f"{progress_info['progress_percentage']:.1f}%",
                inline=False
            )
            
            if progress_info['requirements_met']:
                req_text = "\n".join([f"**{k.replace('_', ' ').title()}:** {v}" 
                                    for k, v in progress_info['requirements_met'].items()])
                embed.add_field(
                    name="📋 Current Progress",
                    value=req_text,
                    inline=False
                )
            
            if target_achievement.requirements:
                req_text = "\n".join([f"**{k.replace('_', ' ').title()}:** {v}" 
                                    for k, v in target_achievement.requirements.items()])
                embed.add_field(
                    name="🎯 Requirements",
                    value=req_text,
                    inline=False
                )
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        logger.error(f"Error in view_achievement: {e}")
        await ctx.send(f"❌ Error retrieving achievement: {str(e)}")

@bot.command(name='leaderboard_achievements', aliases=['achleaderboard', 'achievementlb'])
async def achievement_leaderboard(ctx, category: str = None):
    """Show achievement leaderboard by category or overall."""
    try:
        if not PermissionHelper.has_dev_permissions(ctx.author):
            await ctx.send("❌ This command is restricted to bot owner or moderation role only.")
            return
        
        # Clean up invalid users first
        cleanup_results = achievement_system.cleanup_invalid_users(ctx.guild)
        
        # Get all users and their achievement stats
        user_stats = []
        for member in ctx.guild.members:
            if member.bot:
                continue
            
            stats = achievement_system.get_user_stats(member.id)
            if stats['unlocked_count'] > 0:
                user_stats.append({
                    'member': member,
                    'stats': stats
                })
        
        if not user_stats:
            await ctx.send("❌ No achievement data found!")
            return
        
        if category:
            # Category-specific leaderboard
            category = category.lower()
            if category not in ['message', 'social', 'gaming', 'economy', 'time', 'command', 'milestone', 'special']:
                await ctx.send(f"❌ Invalid category! Valid categories: message, social, gaming, economy, time, command, milestone, special")
                return
            
            # Sort by category completion
            user_stats.sort(key=lambda x: x['stats']['categories'].get(category, {}).get('unlocked', 0), reverse=True)
            title = f"🏆 {category.title()} Achievement Leaderboard"
        else:
            # Overall leaderboard
            user_stats.sort(key=lambda x: x['stats']['unlocked_count'], reverse=True)
            title = "🏆 Overall Achievement Leaderboard"
        
        embed = discord.Embed(
            title=title,
            color=discord.Color.gold()
        )
        
        # Add cleanup information in footer if any users were removed
        if cleanup_results.get('removed', 0) > 0:
            embed.set_footer(text=f"Cleaned up {cleanup_results['removed']} invalid users from achievement data")
        
        # Top 10 users
        for i, user_data in enumerate(user_stats[:10], 1):
            member = user_data['member']
            stats = user_data['stats']
            
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"`#{i}`"
            
            if category:
                unlocked = stats['categories'].get(category, {}).get('unlocked', 0)
                total = stats['categories'].get(category, {}).get('total', 0)
                percentage = (unlocked / total * 100) if total > 0 else 0
                value = f"**{unlocked}/{total}** achievements ({percentage:.1f}%)"
            else:
                value = f"**{stats['unlocked_count']}/{stats['total_count']}** achievements ({stats['completion_percentage']:.1f}%)\n{stats['total_points']:,} points"
            
            embed.add_field(
                name=f"{medal} {member.display_name}",
                value=value,
                inline=False
            )
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        logger.error(f"Error in achievement_leaderboard: {e}")
        await ctx.send(f"❌ Error generating leaderboard: {str(e)}")

@bot.command(name='cleanupachievements', aliases=['achcleanup'])
async def cleanup_achievements(ctx):
    """Manually clean up achievement data for users who left the server or are bots."""
    try:
        if not PermissionHelper.has_dev_permissions(ctx.author):
            await ctx.send("❌ This command is restricted to bot owner or moderation role only.")
            return
        
        # Perform cleanup
        cleanup_results = achievement_system.cleanup_invalid_users(ctx.guild)
        
        embed = discord.Embed(
            title="🧹 Achievement Data Cleanup",
            color=discord.Color.green() if cleanup_results.get('removed', 0) > 0 else discord.Color.blue()
        )
        
        embed.add_field(
            name="📊 Results",
            value=f"**Users Removed:** {cleanup_results.get('removed', 0)}\n"
                  f"**Users Kept:** {cleanup_results.get('kept', 0)}\n"
                  f"**Total Processed:** {cleanup_results.get('total_processed', 0)}",
            inline=False
        )
        
        if cleanup_results.get('error'):
            embed.add_field(
                name="⚠️ Error",
                value=f"```{cleanup_results['error']}```",
                inline=False
            )
            embed.color = discord.Color.red()
        elif cleanup_results.get('removed', 0) > 0:
            embed.add_field(
                name="✅ Status",
                value="Successfully removed achievement data for users who have left the server or are bots.",
                inline=False
            )
        else:
            embed.add_field(
                name="ℹ️ Status",
                value="No invalid users found. All achievement data is for current server members.",
                inline=False
            )
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        logger.error(f"Error in cleanup_achievements: {e}")
        await ctx.send(f"❌ Error during cleanup: {str(e)}")

@bot.command(name='achievements_list', aliases=['listach', 'allachievements'])
async def list_achievements(ctx, category: str = None):
    """List all available achievements, optionally filtered by category."""
    try:
        achievements_by_category = {}
        category_emojis = {
            'social': '👥',
            'gaming': '🎮', 
            'special': '⭐',
            'time': '⏰',
            'counting': '🔢',
            'economy': '💰',
            'commands': '⚡',
            'messages': '💬'
        }
        
        for achievement_id, achievement in achievement_system.achievements.items():
            cat = achievement.category
            if cat not in achievements_by_category:
                achievements_by_category[cat] = []
            achievements_by_category[cat].append(achievement)
        
        # Sort achievements by difficulty/points within each category
        for cat in achievements_by_category:
            achievements_by_category[cat].sort(key=lambda x: x.reward_points)
        
        if category:
            category = category.lower()
            if category not in achievements_by_category:
                available_cats = ", ".join([f"`{cat}`" for cat in achievements_by_category.keys()])
                error_embed = discord.Embed(
                    title="❌ Category Not Found",
                    description=f"**'{category}'** is not a valid category!",
                    color=discord.Color.red()
                )
                error_embed.add_field(
                    name="🔍 Available Categories",
                    value=available_cats,
                    inline=False
                )
                await ctx.send(embed=error_embed)
                return
            
            # Category-specific view with premium styling
            cat_emoji = category_emojis.get(category, '📁')
            embed = discord.Embed(
                title=f"{cat_emoji} **{category.title()}** Achievements",
                description=f"Complete these challenges to earn rewards!\n",
                color=discord.Color.from_rgb(255, 215, 0)  # Gold color
            )
            
            # Add achievements with detailed info
            achievements = achievements_by_category[category]
            total_points = sum(a.reward_points for a in achievements)
            
            embed.description += f"**{len(achievements)}** achievements • **{total_points:,}** total points"
            
            for i, achievement in enumerate(achievements, 1):
                # Difficulty indicator based on points
                if achievement.reward_points >= 1000:
                    difficulty = "🔴 **Legendary**"
                elif achievement.reward_points >= 500:
                    difficulty = "🟡 **Epic**" 
                elif achievement.reward_points >= 100:
                    difficulty = "🟢 **Rare**"
                else:
                    difficulty = "⚪ **Common**"
                
                # Format requirements nicely
                req_text = ""
                if achievement.requirements:
                    reqs = []
                    for k, v in achievement.requirements.items():
                        key_formatted = k.replace('_', ' ').title()
                        reqs.append(f"**{key_formatted}:** {v:,}" if isinstance(v, int) else f"**{key_formatted}:** {v}")
                    req_text = f"\n📋 " + " • ".join(reqs)
                
                value = f"{achievement.description}\n" \
                       f"💎 **{achievement.reward_points:,}** points • {difficulty}" \
                       f"{req_text}"
                
                embed.add_field(
                    name=f"{achievement.emoji} **{achievement.name}**",
                    value=value,
                    inline=False
                )
            
            embed.set_footer(text=f"Use '!myachievements' to see your progress • {len(achievements)} achievements in {category.title()}")
            
        else:
            # Premium category overview
            embed = discord.Embed(
                title="🏆 **Achievement Categories**",
                description="Explore different types of achievements and unlock rewards!\n⭐ *Select a category to view detailed achievements*",
                color=discord.Color.from_rgb(138, 43, 226)  # Purple
            )
            
            # Calculate total stats
            total_achievements = sum(len(achs) for achs in achievements_by_category.values())
            total_points = sum(sum(a.reward_points for a in achs) for achs in achievements_by_category.values())
            
            embed.add_field(
                name="📊 **Server Statistics**",
                value=f"🎯 **{total_achievements}** total achievements\n💎 **{total_points:,}** total points available\n📁 **{len(achievements_by_category)}** categories",
                inline=False
            )
            
            # Show categories with stats and examples
            for i, (cat, achievements) in enumerate(achievements_by_category.items()):
                cat_emoji = category_emojis.get(cat, '📁')
                cat_points = sum(a.reward_points for a in achievements)
                
                # Get a random achievement as example
                example_ach = achievements[len(achievements)//2] if achievements else None
                example_text = f"\n*Example: {example_ach.name}*" if example_ach else ""
                
                embed.add_field(
                    name=f"{cat_emoji} **{cat.title()}**",
                    value=f"🎯 **{len(achievements)}** achievements\n" \
                          f"💎 **{cat_points:,}** points\n" \
                          f"📝 `!listach {cat}`{example_text}",
                    inline=True
                )
                
                # Add spacing every 2 fields for better layout
                if (i + 1) % 2 == 0:
                    embed.add_field(name="\u200b", value="\u200b", inline=True)
            
            embed.set_footer(text="💡 Tip: Use '!myachievements' to see your personal progress!")
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        logger.error(f"Error in list_achievements: {e}")
        error_embed = discord.Embed(
            title="❌ System Error",
            description=f"Failed to load achievements: `{str(e)}`",
            color=discord.Color.red()
        )
        await ctx.send(embed=error_embed)

@bot.command(name='testachievement', aliases=['testach'])
async def test_achievement(ctx):
    """Test the achievement system - gives you a test achievement."""
    try:
        if not PermissionHelper.has_dev_permissions(ctx.author):
            await ctx.send("❌ This command is restricted to bot owner or moderation role only.")
            return
            
        # Test by checking the "hugger" achievement with some progress
        test_stats = {"hugs_given": 1}
        newly_unlocked = check_social_achievements(ctx.author.id, test_stats)
        
        if newly_unlocked:
            for achievement in newly_unlocked:
                await send_achievement_notification(bot, ctx.author, achievement)
                await ctx.send(f"✅ Test successful! Unlocked: {achievement.name}")
        else:
            # Show current progress
            user_achievement = achievement_system.get_user_achievement(ctx.author.id, "hugger")
            progress = achievement_system.get_achievement_progress(ctx.author.id, "hugger")
            
            await ctx.send(f"📊 Test complete! Current progress on 'Hugger' achievement:\n"
                          f"Progress: {progress['progress_percentage']:.1f}%\n"
                          f"Unlocked: {user_achievement.unlocked}")
        
    except Exception as e:
        logger.error(f"Error in test_achievement: {e}")
        await ctx.send(f"❌ Error testing achievement: {str(e)}")

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
@commands.has_permissions(manage_messages=True)
async def skipcount(ctx, number: int):
    """
    Skip the counting to a specific number (moderators only). The bot will announce the skipped numbers,
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
    logger.info(f"Counting skipped to {number} by {ctx.author} in channel {ctx.channel.name}")

# PURGE COMMAND (Enhanced version defined earlier) -------------------------------------------------------------------
@bot.command()
@commands.has_permissions(manage_messages=True)
async def purge(ctx, amount: int = 5):
    """Delete messages in the current channel. Usage: !purge [amount] (default: 5)"""
    if amount < 1 or amount > 999:
        await ctx.send("❌ Please provide a number between 1 and 999.")
        return
    
    try:
        deleted = await ctx.channel.purge(limit=amount + 1)  # +1 to include the command message
        await ctx.send(f"✅ Deleted {len(deleted)-1} messages.", delete_after=3)
    except Exception as e:
        await ctx.send(f"❌ Error purging messages: {e}")


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
@commands.has_permissions(manage_messages=True)
async def counting(ctx):
    """Reset the counting game (moderators only). Usage: !counting"""
    counting_state["channel_id"] = ctx.channel.id
    counting_state["current"] = 0
    counting_state["last_user"] = None
    save_counting_state(counting_state)
    await ctx.send("🔄 **Counting game reset!** The next number is 1.")
    logger.info(f"Counting game reset by {ctx.author} in channel {ctx.channel.name}")

@bot.command()
async def countingstatus(ctx):
    """
    Check the current counting status. 
    Usage: 
    - In server: !countingstatus (shows server counting game status)
    - In DMs: !countingstatus (shows general info about the counting game)
    """
    # Check if command is used in DMs
    is_dm = isinstance(ctx.channel, discord.DMChannel)
    
    if is_dm:
        # In DMs, provide general information about the counting game
        embed = discord.Embed(
            title="🔢 Counting Game Info (DM Mode)",
            description="The counting game is a server-based activity where members count up together!",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="🎯 How It Works",
            value="• Members take turns counting up from 1\n"
                  "• Each person can only say the next number\n"
                  "• If someone posts the wrong number, it resets!\n"
                  "• Goal: Reach the highest number possible as a team",
            inline=False
        )
        
        embed.add_field(
            name="🏆 Benefits",
            value="• Earn contribution points for participating\n"
                  "• Unlock counting-related achievements\n"
                  "• Build community teamwork\n"
                  "• Milestone bonuses at special numbers!",
            inline=False
        )
        
        embed.add_field(
            name="💡 Getting Started",
            value="Join a server where StarChan is active and look for the counting channel!\n"
                  "Usually named something like `#counting` or `#counting-game`",
            inline=False
        )
        
        embed.set_footer(text="🎮 Join a server to participate in the counting game!")
        await ctx.send(embed=embed)
        return
    
    # Original server functionality
    current = counting_state.get("current", 0)
    channel_id = counting_state.get("channel_id")
    last_user_id = counting_state.get("last_user")
    
    if channel_id:
        channel = bot.get_channel(channel_id)
        channel_name = channel.name if channel else f"Unknown Channel (ID: {channel_id})"
    else:
        channel_name = "No channel set"
    
    last_user_name = "None"
    if last_user_id:
        last_user = bot.get_user(last_user_id)
        last_user_name = last_user.display_name if last_user else f"Unknown User (ID: {last_user_id})"
    
    embed = discord.Embed(
        title="🔢 Counting Game Status",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="Current Number",
        value=f"**{current}**",
        inline=True
    )
    
    embed.add_field(
        name="Next Number",
        value=f"**{current + 1}**",
        inline=True
    )
    
    embed.add_field(
        name="Channel",
        value=channel_name,
        inline=True
    )
    
    embed.add_field(
        name="Last Counter",
        value=last_user_name,
        inline=True
    )
    
    await ctx.send(embed=embed)


# SIMPLE TEST COMMAND -----------------------------------------------------------------------------------------------------------------------------------
@bot.command(name='testme')
async def test_me(ctx):
    """Simple test command to verify bot permissions. Usage: !testme"""
    embed = discord.Embed(
        title="✅ Bot Test Results",
        color=discord.Color.green()
    )
    
    embed.add_field(
        name="🆔 Your User ID",
        value=f"`{ctx.author.id}`",
        inline=True
    )
    
    embed.add_field(
        name="👑 Bot Owner",
        value="✅ Yes" if ctx.author.id == BOT_CONFIG.get('owner_id') else "❌ No",
        inline=True
    )
    
    embed.add_field(
        name="🏠 Server ID",
        value=f"`{ctx.guild.id}`" if ctx.guild else "DM",
        inline=True
    )
    
    embed.add_field(
        name="📋 Bot Config Check",
        value=f"Owner ID in config: `{BOT_CONFIG.get('owner_id')}`\nServer ID in config: `{BOT_CONFIG.get('main_server_id')}`",
        inline=False
    )
    
    embed.set_footer(text="If you see this, the bot is working!")
    await ctx.send(embed=embed)


# PUN COMMAND -----------------------------------------------------------------------------------------------------------------------------------
@bot.command()
async def pun(ctx):
    """Send a random pun! Usage: !pun"""
    await ctx.send(GameHelpers.get_random_pun())
    
    # Track command usage achievement
    try:
        # Get current usage count and add 1
        user_achievement = achievement_system.get_user_achievement(ctx.author.id, "pun_lover")
        current_uses = user_achievement.progress.get("pun_uses", 0) + 1
        
        # Debug log the progress
        logger.info(f"Pun command used by {ctx.author.display_name}: {current_uses}/50 uses")
        
        # Check achievement with updated stats
        newly_unlocked = check_command_achievements(ctx.author.id, {"pun_uses": current_uses})
        
        # Send notifications for any newly unlocked achievements
        for achievement in newly_unlocked:
            await send_achievement_notification(bot, ctx.author, achievement)
            if achievement.reward_points > 0:
                await add_contribution(ctx.author.id, achievement.reward_points * 10, ctx.channel)
                
    except Exception as e:
        logger.error(f"Error tracking pun achievement: {e}")


# DAD JOKES COMMAND -----------------------------------------------------------------------------------------------------------------------------------
@bot.command(aliases=['dadjoke', 'dad'])
async def dadjokes(ctx):
    """Send a random dad joke! Usage: !dadjokes"""
    await dadjoke_command(ctx, bot)
    
    # Track achievement points (since bot_utils can't award points directly)
    try:
        user_achievement = achievement_system.get_user_achievement(ctx.author.id, "pun_lover")
        current_uses = user_achievement.progress.get("pun_uses", 0)
        
        # Check if the achievement was just unlocked and award points if needed
        achievement = achievement_system.achievements["pun_lover"]
        if user_achievement.unlocked and current_uses == achievement.requirements["pun_uses"]:
            # Achievement was just unlocked, award points
            await add_contribution(ctx.author.id, achievement.reward_points * 10, ctx.channel)
    except Exception as e:
        logger.error(f"Error awarding dad joke achievement points: {e}")


# ROAST COMMAND -----------------------------------------------------------------------------------------------------------------------------------
@bot.command()
async def roast(ctx, member: discord.Member = None):
    """Playfully roast someone! Usage: !roast @user or !roast for self-roast"""
    await roast_command(ctx, bot, member)


# COMPLIMENT COMMAND -----------------------------------------------------------------------------------------------------------------------------------
@bot.command(aliases=['compliment', 'nice'])
async def praise(ctx, member: discord.Member = None):
    """Give someone a nice compliment! Usage: !praise @user or !praise for self-love"""
    await praise_command(ctx, bot, member)



# USERINFO COMMAND -----------------------------------------------------------------------------------------------------------------------------------
@bot.command()
@cooldown(1, 30, BucketType.user)  # 1 use per 30 seconds per user
async def guessnumber(ctx):
    """
    Start a number guessing game! 
    Usage: 
    - In server: !guessnumber
    - In DMs: !guessnumber
    The bot will pick a number between 1 and 100. You have 7 tries to guess it.
    """
    # Check if command is used in DMs
    is_dm = isinstance(ctx.channel, discord.DMChannel)
    
    number = random.randint(1, 100)
    max_attempts = 7
    
    if is_dm:
        embed = discord.Embed(
            title="🎲 Number Guessing Game (DM Mode)",
            description="I'm thinking of a number between 1 and 100.\nYou have **7 tries** to guess it!",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="🎯 How to Play",
            value="Just type your guess as a number (e.g., `42`)\nI'll tell you if it's too high or too low!",
            inline=False
        )
        embed.set_footer(text="⏰ You have 30 seconds per guess!")
        await ctx.send(embed=embed)
    else:
        await ctx.send("🎲 I'm thinking of a number between 1 and 100. You have 7 tries! Reply with your guess.")

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel and not m.author.bot

    for attempt in range(1, max_attempts + 1):
        try:
            msg = await bot.wait_for('message', timeout=30.0, check=check)
            try:
                guess = int(msg.content.strip())
            except ValueError:
                if is_dm:
                    await ctx.send("❗ **Invalid Input**: Please enter a valid number between 1 and 100.")
                else:
                    await ctx.send("❗ Please enter a valid number.")
                continue

            if guess == number:
                if is_dm:
                    embed = discord.Embed(
                        title="🎉 Congratulations!",
                        description=f"**You got it!** The number was **{number}**",
                        color=discord.Color.green()
                    )
                    embed.add_field(
                        name="📊 Your Performance",
                        value=f"✅ Guessed in **{attempt}** {'try' if attempt == 1 else 'tries'}!\n"
                              f"🎯 {'Perfect!' if attempt == 1 else 'Excellent!' if attempt <= 3 else 'Great job!' if attempt <= 5 else 'Nice work!'}",
                        inline=False
                    )
                    embed.set_footer(text="🎲 Thanks for playing! Use !guessnumber to play again.")
                    await ctx.send(embed=embed)
                else:
                    await ctx.send(f"🎉 Correct, {ctx.author.mention}! The number was {number}. You guessed it in {attempt} tries!")
                return
            elif guess < number:
                if is_dm:
                    await ctx.send(f"🔼 **Too low!** Try a higher number. ({attempt}/{max_attempts} tries used)")
                else:
                    await ctx.send("� Too low!")
            else:
                if is_dm:
                    await ctx.send(f"�🔽 **Too high!** Try a lower number. ({attempt}/{max_attempts} tries used)")
                else:
                    await ctx.send("🔽 Too high!")
                    
        except asyncio.TimeoutError:
            if is_dm:
                embed = discord.Embed(
                    title="⏰ Time's Up!",
                    description=f"The number was **{number}**",
                    color=discord.Color.orange()
                )
                embed.add_field(
                    name="🎯 Better Luck Next Time!",
                    value="Use `!guessnumber` to try again!",
                    inline=False
                )
                await ctx.send(embed=embed)
            else:
                await ctx.send(f"⏰ Time's up! The number was {number}.")
            return

    if is_dm:
        embed = discord.Embed(
            title="❌ Game Over",
            description=f"You've used all **{max_attempts}** tries!",
            color=discord.Color.red()
        )
        embed.add_field(
            name="🎯 The Answer",
            value=f"The number was **{number}**",
            inline=True
        )
        embed.add_field(
            name="🔄 Try Again",
            value="Use `!guessnumber` to play again!",
            inline=True
        )
        embed.set_footer(text="🎲 Don't give up - practice makes perfect!")
        await ctx.send(embed=embed)
    else:
        await ctx.send(f"❌ Out of tries! The number was {number}. Better luck next time, {ctx.author.mention}!")


# HANGMAN GAME COMMAND -----------------------------------------------------------------------------------------------------------------------------------
@bot.command()
@cooldown(1, 60, BucketType.user)  # 1 use per minute per user
async def hangman(ctx):
    """
    Start a hangman word guessing game! 
    Usage: 
    - In server: !hangman
    - In DMs: !hangman
    Guess the mystery word letter by letter. You have 6 wrong attempts.
    """
    # Check if command is used in DMs
    is_dm = isinstance(ctx.channel, discord.DMChannel)
    
    # Word lists by category for variety
    word_lists = {
        "Animals": ["elephant", "giraffe", "butterfly", "penguin", "kangaroo", "dolphin", "octopus", "cheetah"],
        "Countries": ["australia", "brazil", "canada", "denmark", "finland", "germany", "italy", "japan"],
        "Colors": ["purple", "orange", "yellow", "crimson", "turquoise", "magenta", "silver", "golden"],
        "Food": ["pizza", "chocolate", "strawberry", "sandwich", "spaghetti", "hamburger", "cookie", "banana"],
        "Technology": ["computer", "internet", "keyboard", "monitor", "software", "website", "programming", "digital"],
        "Nature": ["mountain", "rainbow", "thunder", "waterfall", "forest", "ocean", "volcano", "desert"],
        "Sports": ["basketball", "football", "swimming", "tennis", "baseball", "volleyball", "soccer", "hockey"]
    }
    
    # Select random category and word
    category = random.choice(list(word_lists.keys()))
    word = random.choice(word_lists[category]).upper()
    
    # Game state
    guessed_letters = set()
    wrong_letters = set()
    max_attempts = 6
    current_attempts = 0
    
    # Track first hangman game achievement
    try:
        # Get current hangman games count
        hangman_user_progress = achievement_system.get_user_achievement(ctx.author.id, "first_hangman")
        hangman_games = hangman_user_progress.progress.get("hangman_games", 0) + 1
        
        # Check first hangman achievement
        game_stats = {"hangman_games": hangman_games}
        newly_unlocked = check_gaming_achievements(ctx.author.id, game_stats)
        
        # Send achievement notifications for first game
        for achievement in newly_unlocked:
            await send_achievement_notification(bot, ctx.author, achievement)
            if achievement.reward_points > 0 and not is_dm:
                await add_contribution(ctx.author.id, achievement.reward_points * 10, ctx.channel)
                
    except Exception as e:
        logger.error(f"Error tracking first hangman achievement: {e}")
    
    # Hangman drawings
    hangman_drawings = [
        "```\n   +---+\n   |   |\n       |\n       |\n       |\n       |\n=========```",
        "```\n   +---+\n   |   |\n   O   |\n       |\n       |\n       |\n=========```",
        "```\n   +---+\n   |   |\n   O   |\n   |   |\n       |\n       |\n=========```",
        "```\n   +---+\n   |   |\n   O   |\n  /|   |\n       |\n       |\n=========```",
        "```\n   +---+\n   |   |\n   O   |\n  /|\\  |\n       |\n       |\n=========```",
        "```\n   +---+\n   |   |\n   O   |\n  /|\\  |\n  /    |\n       |\n=========```",
        "```\n   +---+\n   |   |\n   O   |\n  /|\\  |\n  / \\  |\n       |\n=========```"
    ]
    
    def get_display_word():
        """Get the current state of the word with guessed letters revealed"""
        return " ".join([letter if letter in guessed_letters else "_" for letter in word])
    
    def create_game_embed(title_text, color, show_result=False):
        """Create the game embed with current state"""
        embed = discord.Embed(title=f"🎯 Hangman - {title_text}", color=color)
        
        if not show_result:
            embed.add_field(
                name=f"📚 Category: {category}",
                value=f"**`{get_display_word()}`**",
                inline=False
            )
        
        embed.add_field(
            name="🎨 Hangman",
            value=hangman_drawings[current_attempts],
            inline=True
        )
        
        if guessed_letters:
            correct_letters = [letter for letter in guessed_letters if letter in word]
            embed.add_field(
                name="✅ Correct Letters",
                value=f"`{', '.join(sorted(correct_letters)) if correct_letters else 'None'}`",
                inline=True
            )
        
        if wrong_letters:
            embed.add_field(
                name="❌ Wrong Letters", 
                value=f"`{', '.join(sorted(wrong_letters))}`",
                inline=True
            )
        
        embed.add_field(
            name="📊 Progress",
            value=f"**Wrong guesses:** {current_attempts}/{max_attempts}\n"
                  f"**Letters left:** {26 - len(guessed_letters) - len(wrong_letters)}",
            inline=False
        )
        
        if not show_result:
            embed.add_field(
                name="🎯 How to Play",
                value="Type a **single letter** to guess!\n"
                      "Guess the word before the hangman is complete.",
                inline=False
            )
        
        return embed
    
    # Initial game message
    embed = create_game_embed("New Game", discord.Color.blue())
    embed.set_footer(text="⏰ You have 45 seconds per guess!")
    await ctx.send(embed=embed)

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel and not m.author.bot

    # Game loop
    while current_attempts < max_attempts:
        # Check if word is complete
        if all(letter in guessed_letters for letter in word):
            # Player wins!
            
            # Track achievements for hangman win
            try:
                # Get cumulative hangman stats (similar to tictactoe approach)
                hangman_user_progress = achievement_system.get_user_achievement(ctx.author.id, "hangman_winner")
                hangman_games = hangman_user_progress.progress.get("hangman_games", 0) + 1
                hangman_wins = hangman_user_progress.progress.get("hangman_wins", 0) + 1
                
                perfect_hangman_progress = achievement_system.get_user_achievement(ctx.author.id, "perfect_hangman")
                perfect_hangman_wins = perfect_hangman_progress.progress.get("perfect_hangman_wins", 0)
                if current_attempts == 0:  # Perfect game
                    perfect_hangman_wins += 1
                
                fast_hangman_progress = achievement_system.get_user_achievement(ctx.author.id, "hangman_speedster")
                fast_hangman_wins = fast_hangman_progress.progress.get("fast_hangman_wins", 0)
                if current_attempts <= 4:  # Fast game
                    fast_hangman_wins += 1
                
                # Check achievements 
                game_stats = {
                    "hangman_games": hangman_games,
                    "hangman_wins": hangman_wins,
                    "perfect_hangman_wins": perfect_hangman_wins,
                    "fast_hangman_wins": fast_hangman_wins,
                    "total_games": hangman_games  # For gaming addict achievement
                }
                
                newly_unlocked = check_gaming_achievements(ctx.author.id, game_stats)
                
                # Send achievement notifications
                for achievement in newly_unlocked:
                    await send_achievement_notification(bot, ctx.author, achievement)
                    if achievement.reward_points > 0 and not is_dm:
                        await add_contribution(ctx.author.id, achievement.reward_points * 10, ctx.channel)
                        
            except Exception as e:
                logger.error(f"Error tracking hangman achievements: {e}")
            
            embed = discord.Embed(
                title="🎉 Congratulations! You Win!",
                description=f"**The word was: `{word}`**",
                color=discord.Color.green()
            )
            embed.add_field(
                name="📚 Category",
                value=category,
                inline=True
            )
            embed.add_field(
                name="📊 Your Score",
                value=f"✅ **{len(guessed_letters)}** correct letters\n"
                      f"❌ **{current_attempts}** wrong guesses\n"
                      f"🎯 **{max_attempts - current_attempts}** lives remaining",
                inline=True
            )
            embed.add_field(
                name="🏆 Performance",
                value=f"{'🌟 Perfect!' if current_attempts == 0 else '🎖️ Excellent!' if current_attempts <= 2 else '👏 Great job!' if current_attempts <= 4 else '👍 Nice work!'}",
                inline=False
            )
            embed.set_footer(text="🎯 Use !hangman to play again!")
            await ctx.send(embed=embed)
            return
        
        try:
            msg = await bot.wait_for('message', timeout=45.0, check=check)
            guess = msg.content.strip().upper()
            
            # Validate input
            if len(guess) != 1 or not guess.isalpha():
                await ctx.send("❗ **Invalid Input**: Please enter a single letter (A-Z)")
                continue
                
            if guess in guessed_letters or guess in wrong_letters:
                await ctx.send(f"❗ **Already Guessed**: You've already guessed the letter `{guess}`")
                continue
            
            # Process guess
            if guess in word:
                guessed_letters.add(guess)
                embed = create_game_embed("Correct Guess!", discord.Color.green())
                embed.add_field(
                    name="✅ Good Job!",
                    value=f"The letter **`{guess}`** is in the word!",
                    inline=False
                )
                await ctx.send(embed=embed)
            else:
                wrong_letters.add(guess)
                current_attempts += 1
                embed = create_game_embed("Wrong Guess", discord.Color.red())
                embed.add_field(
                    name="❌ Not Found",
                    value=f"The letter **`{guess}`** is not in the word.",
                    inline=False
                )
                await ctx.send(embed=embed)
                
        except asyncio.TimeoutError:
            embed = discord.Embed(
                title="⏰ Time's Up!",
                description=f"**The word was: `{word}`**",
                color=discord.Color.orange()
            )
            embed.add_field(
                name="📚 Category",
                value=category,
                inline=True
            )
            embed.add_field(
                name="🔄 Try Again",
                value="Use `!hangman` to start a new game!",
                inline=True
            )
            await ctx.send(embed=embed)
            return
    
    # Game over - player lost
    
    # Track achievements for playing hangman (even if lost)
    try:
        game_stats = {
            "hangman_games": 1,
            "total_games": 1  # For gaming addict achievement
        }
        
        newly_unlocked = check_gaming_achievements(ctx.author.id, game_stats)
        
        # Send achievement notifications
        for achievement in newly_unlocked:
            await send_achievement_notification(bot, ctx.author, achievement)
            if achievement.reward_points > 0 and not is_dm:
                await add_contribution(ctx.author.id, achievement.reward_points * 10, ctx.channel)
                
    except Exception as e:
        logger.error(f"Error tracking hangman game achievements: {e}")
    
    embed = discord.Embed(
        title="💀 Game Over - Hangman Complete!",
        description=f"**The word was: `{word}`**",
        color=discord.Color.red()
    )
    embed.add_field(
        name="📚 Category",
        value=category,
        inline=True
    )
    embed.add_field(
        name="📊 Final Score",
        value=f"✅ **{len(guessed_letters)}** correct letters\n"
              f"❌ **{current_attempts}** wrong guesses",
        inline=True
    )
    embed.add_field(
        name="🎨 Final Hangman",
        value=hangman_drawings[current_attempts],
        inline=False
    )
    embed.add_field(
        name="🔄 Don't Give Up!",
        value="Use `!hangman` to try again!\nPractice makes perfect! 💪",
        inline=False
    )
    embed.set_footer(text="🎯 Better luck next time!")
    await ctx.send(embed=embed)


# 8BALL COMMAND -----------------------------------------------------------------------------------------------------------------------------------
@bot.command(name="8ball", aliases=["eightball"])
@cooldown(1, 100, BucketType.user)  # 1 use per 5 minutes per user
async def eight_ball(ctx, *, question: str = None):
    """
    Ask the magic 8-ball a question.
    Usage: 
    - In server: !8ball Will I win the lottery?
    - In DMs: !8ball Will I win the lottery?
    """
    # Check if command is used in DMs
    is_dm = isinstance(ctx.channel, discord.DMChannel)
    
    if not question:
        if is_dm:
            await ctx.send("🎱 **DM Mode**: Ask the magic 8-ball a question!\n"
                          "Example: `!8ball Will I have a good day?`")
        else:
            await ctx.send("🎱 Please ask a question, e.g. `!8ball Will I win the lottery?`")
        return
    
    answer = GameHelpers.get_8ball_response()
    
    if is_dm:
        embed = discord.Embed(
            title="🎱 Magic 8-Ball (DM Mode)",
            color=discord.Color.purple()
        )
        embed.add_field(
            name="❓ Your Question",
            value=question,
            inline=False
        )
        embed.add_field(
            name="🔮 The Answer",
            value=answer,
            inline=False
        )
        embed.set_footer(text="✨ The magic 8-ball has spoken! ✨")
        await ctx.send(embed=embed)
    else:
        await ctx.send(f"🎱 Question: {question}\nAnswer: {answer}")
    
    # Track command usage achievement
    try:
        # Get current usage count
        user_achievement = achievement_system.get_user_achievement(ctx.author.id, "fortune_seeker")
        current_uses = user_achievement.progress.get("eightball_uses", 0) + 1
        
        # Check achievement with updated stats
        newly_unlocked = check_command_achievements(ctx.author.id, {"eightball_uses": current_uses})
        
        # Send notifications for any newly unlocked achievements
        for achievement in newly_unlocked:
            await send_achievement_notification(bot, ctx.author, achievement)
            # Only award contribution points if not in DMs (since DMs don't have guild context)
            if not is_dm and achievement.reward_points > 0:
                await add_contribution(ctx.author.id, achievement.reward_points * 10, ctx.channel)
        
    except Exception as e:
        logger.error(f"Error tracking 8ball achievement: {e}")


# LURKERS COMMAND -----------------------------------------------------------------------------------------------------------------------------------
@bot.command()
@commands.has_permissions(administrator=True)
async def showlurkers(ctx):
    """
    Show members who joined more than 18 days ago and have not sent a message in the last 18 days.
    Usage: !showlurkers
    """
    from datetime import datetime, timedelta, timezone
    now = datetime.now(timezone.utc)
    threshold = now - timedelta(days=18)
    lurkers = []
    for member in ctx.guild.members:
        if member.bot:
            continue
        if member.joined_at and member.joined_at < threshold:
            last = last_active.get(str(member.id), 0)
            # If never active or last active >18 days ago
            if last == 0 or (time.time() - last) > 18 * 24 * 3600:
                lurkers.append(f"{member.mention} (joined {member.joined_at.strftime('%Y-%m-%d')})")
    if lurkers:
        await ctx.send("👀 **Inactive members (joined >18 days ago, no recent messages):**\n" + "\n".join(lurkers))
    else:
        await ctx.send("No inactive members found!")


#CREDIT COMMAND
@bot.command()
async def credits(ctx):
    await ctx.send("Bot credits: Made by @alexandrospanag on GitHub! (StarChan)")

# DEV LEVEL COMMANDS (Owner only) ---------------------------------------------------
@bot.command()
async def devlevelup(ctx, member: discord.Member, levels: int):
    """
    [DEV/MOD ONLY] Level up a user by a specified number of levels.
    Usage: !devlevelup @user 5
    """
    # Restrict to bot owner or moderation role
    if not PermissionHelper.has_dev_permissions(ctx.author):
        await ctx.send("❌ This command is restricted to bot owner or moderation role only.")
        return
    
    if levels <= 0:
        await ctx.send("❌ Level amount must be positive!")
        return
    
    if levels > 100:
        await ctx.send("❌ Maximum 100 levels at once to prevent abuse!")
        return
    
    user_id = str(member.id)
    current_points = contributions.get(user_id, 0)  # Current balance
    current_lifetime = lifetime_earnings.get(user_id, 0)  # Lifetime earnings
    current_level = get_user_level(user_id)  # Level based on lifetime earnings
    
    # Calculate points needed for target level based on lifetime earnings
    target_level = current_level + levels
    target_lifetime_points = (target_level ** 2) * 100  # Reverse of level formula
    lifetime_points_to_add = target_lifetime_points - current_lifetime
    
    # Update both current balance and lifetime earnings
    contributions[user_id] = current_points + lifetime_points_to_add
    lifetime_earnings[user_id] = current_lifetime + lifetime_points_to_add
    await save_contributions_async(contributions)
    await save_lifetime_earnings_async(lifetime_earnings)
    
    # Success message
    embed = discord.Embed(
        title="⬆️ DEV LEVEL UP ⬆️",
        description=f"**{member.display_name}** has been leveled up!",
        color=discord.Color.green()
    )
    
    embed.add_field(
        name="📊 Level Change",
        value=f"**{current_level}** → **{target_level}** (+{levels} levels)",
        inline=True
    )
    
    embed.add_field(
        name="💰 Points Added",
        value=f"+{lifetime_points_to_add:,} points",
        inline=True
    )
    
    embed.add_field(
        name="💎 New Total",
        value=f"{contributions[user_id]:,} points",
        inline=True
    )
    
    embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
    embed.set_footer(text="DEV Command - Level adjustment complete")
    
    await ctx.send(embed=embed)
    logger.info(f"DEV: {ctx.author} leveled up {member} by {levels} levels (+{lifetime_points_to_add:,} points)")

@bot.command()
async def devleveldown(ctx, member: discord.Member, levels: int):
    """
    [DEV/MOD ONLY] Level down a user by a specified number of levels.
    Usage: !devleveldown @user 5
    """
    # Restrict to bot owner or moderation role
    if not PermissionHelper.has_dev_permissions(ctx.author):
        await ctx.send("❌ This command is restricted to bot owner or moderation role only.")
        return
    
    if levels <= 0:
        await ctx.send("❌ Level amount must be positive!")
        return
    
    if levels > 100:
        await ctx.send("❌ Maximum 100 levels at once to prevent abuse!")
        return
    
    user_id = str(member.id)
    current_points = contributions.get(user_id, 0)  # Current balance
    current_lifetime = lifetime_earnings.get(user_id, 0)  # Lifetime earnings
    current_level = get_user_level(user_id)  # Level based on lifetime earnings
    
    # Calculate target level (ensure it doesn't go below 0)
    target_level = max(0, current_level - levels)
    target_lifetime_points = (target_level ** 2) * 100  # Reverse of level formula
    lifetime_points_to_remove = current_lifetime - target_lifetime_points
    
    # Update lifetime earnings (ensure it doesn't go below 0)
    new_lifetime_points = max(0, current_lifetime - lifetime_points_to_remove)
    lifetime_earnings[user_id] = new_lifetime_points
    
    # For balance, we remove the same amount but ensure it doesn't go negative
    new_balance = max(0, current_points - lifetime_points_to_remove)
    contributions[user_id] = new_balance
    
    await save_contributions_async(contributions)
    await save_lifetime_earnings_async(lifetime_earnings)
    
    # Success message
    embed = discord.Embed(
        title="⬇️ DEV LEVEL DOWN ⬇️",
        description=f"**{member.display_name}** has been leveled down!",
        color=discord.Color.red()
    )
    
    embed.add_field(
        name="📊 Level Change",
        value=f"**{current_level}** → **{target_level}** (-{current_level - target_level} levels)",
        inline=True
    )
    
    embed.add_field(
        name="💰 Points Removed",
        value=f"-{current_points - new_balance:,} points",
        inline=True
    )
    
    embed.add_field(
        name="💎 New Total",
        value=f"{new_balance:,} points",
        inline=True
    )
    
    embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
    embed.set_footer(text="DEV Command - Level adjustment complete")
    
    await ctx.send(embed=embed)
    logger.info(f"DEV: {ctx.author} leveled down {member} by {levels} levels (-{current_points - new_balance:,} points)")

@bot.command()
async def devsetlevel(ctx, member: discord.Member, target_level: int):
    """
    [DEV/MOD ONLY] Set a user's level to a specific value.
    Usage: !devsetlevel @user 25
    """
    # Restrict to bot owner or moderation role
    if not PermissionHelper.has_dev_permissions(ctx.author):
        await ctx.send("❌ This command is restricted to bot owner or moderation role only.")
        return
    
    if target_level < 0:
        await ctx.send("❌ Level cannot be negative!")
        return
    
    if target_level > 500:
        await ctx.send("❌ Maximum level is 500 to prevent abuse!")
        return
    
    user_id = str(member.id)
    current_points = contributions.get(user_id, 0)  # Current balance
    current_lifetime = lifetime_earnings.get(user_id, 0)  # Lifetime earnings
    current_level = get_user_level(user_id)  # Level based on lifetime earnings
    
    # Calculate lifetime points needed for target level
    target_lifetime_points = (target_level ** 2) * 100  # Reverse of level formula
    lifetime_points_difference = target_lifetime_points - current_lifetime
    
    # Update both lifetime earnings and current balance
    lifetime_earnings[user_id] = target_lifetime_points
    contributions[user_id] = current_points + lifetime_points_difference  # Adjust balance by the same amount
    
    await save_contributions_async(contributions)
    await save_lifetime_earnings_async(lifetime_earnings)
    
    # Success message
    embed = discord.Embed(
        title="🎯 DEV SET LEVEL 🎯",
        description=f"**{member.display_name}**'s level has been set!",
        color=discord.Color.gold()
    )
    
    embed.add_field(
        name="📊 Level Change",
        value=f"**{current_level}** → **{target_level}**",
        inline=True
    )
    
    embed.add_field(
        name="💰 Points Adjusted",
        value=f"{'+' if lifetime_points_difference >= 0 else ''}{lifetime_points_difference:,} points",
        inline=True
    )
    
    embed.add_field(
        name="💎 New Lifetime Total",
        value=f"{target_lifetime_points:,} points",
        inline=True
    )
    
    embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
    embed.set_footer(text="DEV Command - Level set complete")
    
    await ctx.send(embed=embed)
    logger.info(f"DEV: {ctx.author} set {member}'s level to {target_level} ({target_lifetime_points:,} lifetime points)")


# DEV SHOW SCORES COMMAND ---------------------------------------------------
@bot.command(name='devshowscores')
async def dev_show_scores(ctx):
    """
    [DEV/MOD ONLY] Display the weekly top 10 contributors and automatically promote them to ⚡Star Contributor ⚡.
    Usage: !devshowscores
    """
    # Restrict to bot owner or moderation role
    if not PermissionHelper.has_dev_permissions(ctx.author):
        await ctx.send("❌ This command is restricted to bot owner or moderation role only.")
        return
    
    try:
        # Get the weekly leaderboard data
        weekly_top = WeeklyContributionManager.get_weekly_leaderboard(10)
        
        if not weekly_top:
            await ctx.send("❌ No weekly contribution data found!")
            return
        
        # Create the Star Contributor role if it doesn't exist
        star_role_name = "⚡Star Contributor ⚡"
        star_role = discord.utils.get(ctx.guild.roles, name=star_role_name)
        
        if not star_role:
            try:
                star_role = await ctx.guild.create_role(
                    name=star_role_name,
                    color=discord.Color.from_rgb(255, 215, 0),  # Gold color
                    mentionable=True,
                    reason="Auto-created for weekly top contributors"
                )
                await ctx.send(f"✅ Created new role: **{star_role_name}**")
            except discord.Forbidden:
                await ctx.send("❌ Cannot create roles! Missing permissions.")
                return
        
        # Prepare embed
        embed = discord.Embed(
            title="🏆 Weekly Top 10 Contributors 🏆",
            description="**Automatically promoting top contributors to ⚡Star Contributor ⚡**",
            color=discord.Color.gold()
        )
        
        # Process each top contributor
        promoted_users = []
        failed_promotions = []
        leaderboard_text = ""
        
        for i, (user_id_str, points) in enumerate(weekly_top, 1):
            try:
                user_id = int(user_id_str)
                member = ctx.guild.get_member(user_id)
                
                if member:
                    # Add to leaderboard display
                    medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"`#{i}`"
                    leaderboard_text += f"{medal} **{member.display_name}** - {points:,} points\n"
                    
                    # Check if user already has the role
                    if star_role not in member.roles:
                        try:
                            await member.add_roles(star_role, reason=f"Top {i} weekly contributor with {points:,} points")
                            promoted_users.append((member.display_name, points, i))
                        except discord.Forbidden:
                            failed_promotions.append((member.display_name, "Missing permissions"))
                        except discord.HTTPException as e:
                            failed_promotions.append((member.display_name, str(e)))
                    else:
                        # User already has role
                        promoted_users.append((member.display_name, points, i, True))  # True = already had role
                else:
                    # Member not found (maybe left server)
                    leaderboard_text += f"`#{i}` **User Left Server** (ID: {user_id_str}) - {points:,} points\n"
                    failed_promotions.append((f"User {user_id_str}", "User left server"))
            
            except Exception as e:
                logger.error(f"Error processing user {user_id_str}: {e}")
                leaderboard_text += f"`#{i}` **Error loading user** (ID: {user_id_str}) - {points:,} points\n"
                failed_promotions.append((f"User {user_id_str}", str(e)))
        
        # Add leaderboard to embed
        embed.add_field(
            name="📊 Weekly Leaderboard",
            value=leaderboard_text or "No contributors found!",
            inline=False
        )
        
        # Add promotion results
        if promoted_users:
            promotion_text = ""
            newly_promoted = []
            already_had_role = []
            
            for user_data in promoted_users:
                if len(user_data) == 4 and user_data[3]:  # Already had role
                    already_had_role.append(f"**{user_data[0]}** (#{user_data[2]})")
                else:  # Newly promoted
                    newly_promoted.append(f"**{user_data[0]}** (#{user_data[2]}) - {user_data[1]:,} points")
            
            if newly_promoted:
                promotion_text += "🆕 **Newly Promoted:**\n" + "\n".join(newly_promoted)
            
            if already_had_role:
                if promotion_text:
                    promotion_text += "\n\n"
                promotion_text += "✅ **Already Had Role:**\n" + "\n".join(already_had_role)
            
            embed.add_field(
                name="🎭 Role Promotions",
                value=promotion_text,
                inline=False
            )
        
        if failed_promotions:
            failed_text = "\n".join([f"**{name}**: {reason}" for name, reason in failed_promotions])
            embed.add_field(
                name="❌ Failed Promotions",
                value=failed_text,
                inline=False
            )
        
        # Add summary
        total_promoted = len([u for u in promoted_users if len(u) == 3 or not u[3]])
        total_already_had = len([u for u in promoted_users if len(u) == 4 and u[3]])
        total_failed = len(failed_promotions)
        
        summary = f"**✅ Newly Promoted:** {total_promoted}\n**🔄 Already Had Role:** {total_already_had}\n**❌ Failed:** {total_failed}"
        embed.add_field(
            name="📈 Summary",
            value=summary,
            inline=False
        )
        
        # Add timestamp
        embed.set_footer(text=f"Updated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Role: {star_role_name}")
        
        await ctx.send(embed=embed)
        
        # Log the promotion activity
        logger.info(f"DEV: {ctx.author} executed devshowscores - {total_promoted} newly promoted, {total_already_had} already had role, {total_failed} failed")
        
    except Exception as e:
        logger.error(f"Error in devshowscores command: {e}")
        await ctx.send(f"❌ An error occurred: {str(e)}")


# DEV ANNOUNCEMENT COMMAND ---------------------------------------------------
@bot.command(name='devannouncement', aliases=['devannounce'])
async def dev_announcement(ctx, *, message: str = None):
    """
    [DEV/MOD ONLY] Post an announcement to the designated announcement channel.
    Usage: !devannouncement <message>
    
    Configure your announcement channel ID in the code before using this command.
    """
    # Restrict to bot owner or moderation role
    if not PermissionHelper.has_dev_permissions(ctx.author):
        await ctx.send("❌ This command is restricted to bot owner or moderation role only.")
        return
    
    if not message:
        await ctx.send("❌ Please provide an announcement message.\nUsage: `!devannouncement <your message here>`")
        return
    
    try:
        # Get the announcement channel - replace with your announcement channel ID
        announcement_channel_id = 000000000000000000  # Replace with your announcement channel ID
        announcement_channel = bot.get_channel(announcement_channel_id)
        
        if not announcement_channel:
            await ctx.send(f"❌ Could not find announcement channel with ID: {announcement_channel_id}")
            return
        
        # Check if bot has permission to send messages in that channel
        if not announcement_channel.permissions_for(announcement_channel.guild.me).send_messages:
            await ctx.send(f"❌ Bot doesn't have permission to send messages in {announcement_channel.mention}")
            return
        
        # Create announcement embed
        embed = discord.Embed(
            title="📢 Official Announcement",
            description=message,
            color=discord.Color.gold()
        )
        
        embed.set_author(
            name=f"Announcement by {ctx.author.display_name}",
            icon_url=ctx.author.avatar.url if ctx.author.avatar else None
        )
        
        embed.set_footer(
            text=f"Posted via StarChan Bot • {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            icon_url=bot.user.avatar.url if bot.user.avatar else None
        )
        
        # Send the announcement
        announcement_msg = await announcement_channel.send(embed=embed)
        
        # Confirm to the user
        confirm_embed = discord.Embed(
            title="✅ Announcement Posted Successfully",
            description=f"Your announcement has been posted to {announcement_channel.mention}",
            color=discord.Color.green()
        )
        
        confirm_embed.add_field(
            name="📝 Message Content",
            value=message[:1000] + "..." if len(message) > 1000 else message,
            inline=False
        )
        
        confirm_embed.add_field(
            name="🔗 Jump to Message",
            value=f"[Click here to view]({announcement_msg.jump_url})",
            inline=False
        )
        
        await ctx.send(embed=confirm_embed)
        
        # Log the announcement
        logger.info(f"DEV ANNOUNCEMENT: {ctx.author} posted announcement to channel {announcement_channel_id}: {message[:100]}...")
        
    except Exception as e:
        logger.error(f"Error in devannouncement command: {e}")
        await ctx.send(f"❌ An error occurred while posting the announcement: {str(e)}")


# AWARD CONTRIBUTORS COMMAND ---------------------------------------------------
@bot.command(name='awardcontributors')
async def award_contributors(ctx):
    """
    [DEV/MOD ONLY] Award the top 10 weekly contributors with 2,000 points each.
    Usage: !awardcontributors
    
    Only works when the weekly top contributors file exists and awards are pending.
    """
    # Restrict to bot owner or moderation role
    if not PermissionHelper.has_dev_permissions(ctx.author):
        await ctx.send("❌ This command is restricted to bot owner or moderation role only.")
        return
    
    try:
        # Check if the file exists
        if not WeeklyContributionManager.check_awards_pending():
            embed = discord.Embed(
                title="❌ No Pending Awards",
                description="Either the weekly top contributors file doesn't exist, or awards have already been given.\n\n"
                           "The file is created automatically when the week resets (Monday 00:00 UTC).",
                color=discord.Color.red()
            )
            embed.add_field(
                name="⏰ Next Week Reset",
                value=WeeklyContributionManager.get_time_until_next_week(),
                inline=False
            )
            await ctx.send(embed=embed)
            return
        
        # Load the user IDs from the file
        user_ids = WeeklyContributionManager.load_top_contributors_file()
        if not user_ids:
            # Provide detailed debug information
            debug_info = WeeklyContributionManager.debug_contributors_file()
            
            embed = discord.Embed(
                title="❌ Could Not Load User IDs",
                description="Failed to load user IDs from the weekly top contributors file.",
                color=discord.Color.red()
            )
            embed.add_field(
                name="🔍 Debug Information",
                value=debug_info,
                inline=False
            )
            embed.add_field(
                name="💡 Possible Solutions",
                value="• Ensure the weekly contributors file was created properly\n"
                      "• Check that the file contains valid user ID entries\n"
                      "• Try running `!devshowscores` to regenerate the file\n"
                      "• Contact the bot owner if the issue persists",
                inline=False
            )
            await ctx.send(embed=embed)
            return
        
        # Award each user 2,000 points
        award_amount = 2000
        awarded_users = []
        failed_users = []
        
        for user_id in user_ids:
            try:
                # Add points to their total contributions (but NOT weekly - awards don't count for current week)
                current_points = contributions.get(user_id, 0)
                contributions[user_id] = current_points + award_amount
                # Update lifetime earnings too since this is earning points
                lifetime_earnings[user_id] = lifetime_earnings.get(user_id, 0) + award_amount
                awarded_users.append((user_id, current_points + award_amount))
            except Exception as e:
                logger.error(f"Error awarding points to {user_id}: {e}")
                failed_users.append(user_id)
        
        # Save the updated contributions and lifetime earnings
        await save_contributions_async(contributions)
        await save_lifetime_earnings_async(lifetime_earnings)
        
        # Mark awards as given in the file
        WeeklyContributionManager.mark_awards_given()
        
        # Create success embed
        embed = discord.Embed(
            title="🏆 Weekly Awards Given!",
            description=f"Successfully awarded **{award_amount:,}** points to **{len(awarded_users)}** top contributors!",
            color=discord.Color.green()
        )
        
        # Show awarded users (limit to fit in embed)
        if awarded_users:
            user_list = []
            for i, (user_id, new_total) in enumerate(awarded_users[:10], 1):
                user_list.append(f"{i}. <@{user_id}> - Now has {new_total:,} points")
            
            embed.add_field(
                name="🎁 Awarded Users",
                value="\n".join(user_list),
                inline=False
            )
        
        if failed_users:
            embed.add_field(
                name="⚠️ Failed Awards",
                value=f"{len(failed_users)} users could not be awarded",
                inline=False
            )
        
        embed.add_field(
            name="📊 Award Details",
            value=f"Amount: {award_amount:,} points each\nTotal awarded: {len(awarded_users) * award_amount:,} points",
            inline=False
        )
        
        embed.set_footer(text="✅ Awards completed and marked in file")
        await ctx.send(embed=embed)
        
        logger.info(f"DEV: {ctx.author} awarded {award_amount:,} points to {len(awarded_users)} weekly top contributors")
        
    except Exception as e:
        logger.error(f"Error in awardcontributors command: {e}")
        await ctx.send("❌ An error occurred while awarding contributors. Check the logs for details.")


@bot.command(name='debugcontributors', aliases=['debugawards', 'checkcontributors'])
async def debug_contributors_file(ctx):
    """
    [DEV/MOD ONLY] Debug the weekly top contributors file.
    Shows file status and contents for troubleshooting.
    """
    # Restrict to bot owner or moderation role
    if not PermissionHelper.has_dev_permissions(ctx.author):
        await ctx.send("❌ This command is restricted to bot owner or moderation role only.")
        return
    
    try:
        debug_info = WeeklyContributionManager.debug_contributors_file()
        
        embed = discord.Embed(
            title="🔍 Weekly Contributors File Debug",
            description="Diagnostic information for the weekly top contributors file.",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="📁 File Status",
            value=debug_info,
            inline=False
        )
        
        # Also show if awards are pending
        awards_pending = WeeklyContributionManager.check_awards_pending()
        embed.add_field(
            name="🏆 Award Status",
            value=f"{'✅ Awards are pending' if awards_pending else '❌ No pending awards'}",
            inline=False
        )
        
        # Try to load user IDs
        user_ids = WeeklyContributionManager.load_top_contributors_file()
        embed.add_field(
            name="👥 User ID Loading Test",
            value=f"{'✅ Successfully loaded' if user_ids else '❌ Failed to load'} user IDs\n"
                  f"Count: {len(user_ids) if user_ids else 0}",
            inline=False
        )
        
        embed.set_footer(text="Use this information to troubleshoot award issues")
        await ctx.send(embed=embed)
        
    except Exception as e:
        logger.error(f"Error in debug contributors command: {e}")
        await ctx.send(f"❌ Error running debug command: {str(e)}")


@bot.command(name="helpstar", aliases=["helpstarchan", "starhelp", "helpschan"])
@cooldown(1, 7200, BucketType.user)
async def helpstar(ctx):
    # No cooldown for the owner - reset it properly
    if ctx.author.id == BOT_CONFIG.get('owner_id'):
        # Reset the cooldown for the owner
        helpstar.reset_cooldown(ctx)
    
    try:
        await send_helpstar(ctx)
        
        # Track help command achievement
        try:
            # Get current usage count
            user_achievement = achievement_system.get_user_achievement(ctx.author.id, "helper")
            current_uses = user_achievement.progress.get("help_uses", 0) + 1
            
            # Check achievement with updated stats
            newly_unlocked = check_command_achievements(ctx.author.id, {"help_uses": current_uses})
            
            # Send notifications for any newly unlocked achievements
            for achievement in newly_unlocked:
                await send_achievement_notification(bot, ctx.author, achievement)
                if achievement.reward_points > 0:
                    await add_contribution(ctx.author.id, achievement.reward_points * 10, ctx.channel, ctx.author)
        except Exception as e:
            logger.error(f"Error tracking help achievement: {e}")
            
    except Exception as e:
        logger.error(f"Error in helpstar command: {e}")
        await ctx.send("❌ Error displaying help. Please try again later.")

async def send_helpstar(ctx):
    try:
        help_text = (
            "✨ **StarChan Complete Help Guide** ✨\n"
            "\n"
            "🎪 **Fun & Entertainment:**\n"
            "😺 `!cat` 🐶 `!doggo` 🤪 `!pun` 🔥 `!roast [@user]` 💖 `!praise [@user]`\n"
            "👋 `!slap @user`\n"
            "🎱 `!8ball <question>` 🎮 `!tictactoe [@user]` 🧪 `!testme`\n"
            "🔢 `!guessnumber` 🎯 `!hangman`\n"
            "\n"
            "🎯 **Leveling & Competition:**\n"
            "🔢 `!counting` ⏩ `!skipcount <n>`\n"
            "🏆 `!leaderboard` 🏆 `!leaderboardmax` 🥇 `!balance`\n"
            "🛒 `!shop` 💰 `!buy <role>` 💸 `!sell <role>`\n"
            "🃏 `!blackjack <bet>` (🎲 Win 10k+ bet for Gambler role!)\n"
            "\n"
            "🧩 **Weekly Challenges:**\n"
            "🧩 `!riddlemethis [answer]` 🏆 `!riddlestatus` (3,000 points prize!)\n"
            "\n"
            "🏆 **Achievements:**\n"
            "🏅 `!myachievements` 🎯 `!achievement <name>`\n"
            "📊 `!achievementstatus` 📋 `!listach [category]`\n"
            "🏆 `!viewach [@user]` 📈 `!achievementprogress <name>`\n"
            "\n"
            "📊 **Stats & Info:**\n"
            "🆔 `!whatismyid [@user]`\n"
            "⏰ `!pingservertime` - Check server time for daily resets\n"
            "\n"
            "🛠️ **Moderation & Admin:**\n"
            "🧹 `!purge [amount]` 📝 `!modpost <channel_id> <msg>`\n"
            "👢 `!kick @user [reason]` 👀 `!showlurkers`\n"
            "\n"
            "ℹ️ **System & Info:**\n"
            "🏆 `!credits` 📝 `!license`\n"
            "💡 **Tips:** Commands with [@user] are optional, [amount] means optional number\n"
            "🎲 **Special:** Win blackjack with 10k+ points to earn the exclusive Gambler role!\n"
        )
        
        # Add dev commands for bot owner and moderation role
        if PermissionHelper.has_dev_permissions(ctx.author):
            help_text += (
                "\n"
                "🔧 **DEV/MOD Commands:**\n"
                "⬆️ `!devlevelup @user <levels>` - Level up a user\n"
                "⬇️ `!devleveldown @user <levels>` - Level down a user\n"
                "🎯 `!devsetlevel @user <level>` - Set user's exact level\n"
                "📊 `!devshowscores` - Show weekly top contributors with role promotion\n"
                "📢 `!devannouncement <message>` - Post announcement to designated channel\n"
                "🏆 `!awardcontributors` - Award weekly top 10 with 2,000 points\n"
                "🔍 `!debugcontributors` - Debug weekly contributors file\n"
                "🏆 `!achleaderboard [category]` - Achievement leaderboards\n"
                "🧹 `!achcleanup` - Clean up achievement data for invalid users\n"
                "🔧 `!testachievement` - Test achievement system\n"
            )
        
        # Add debug commands for bot owner only
        if ctx.author.id == BOT_CONFIG.get('owner_id'):
            help_text += (
                "\n"
                "🐛 **DEBUG Commands (Owner Only):**\n"
                "🐛 `!debug <code>` - Execute Python code for debugging\n"
                "💾 `!debugsaveprogress` - Force save all data files\n"
                "🏆 `!debugachievements @user` - Show debug achievement info\n"
            )
        
        await ctx.send(help_text)
        logger.info(f"Help command executed successfully for {ctx.author}")
        
    except Exception as e:
        logger.error(f"Error in send_helpstar: {e}")
        raise e  # Re-raise so the main command can handle it


# ACHIEVEMENTS COMMANDS ---------------------------------------------------
@bot.command(name="viewach", aliases=["vach"])
async def achievement_info(ctx, member: discord.Member = None):
    """
    View your achievements or someone else's achievements.
    Usage: !achievements [@user]
    """
    target_user = member or ctx.author
    user_id = target_user.id
    
    try:
        # Get user stats
        stats = achievement_system.get_user_stats(user_id)
        unlocked_achievements = achievement_system.get_unlocked_achievements(user_id)
        
        # Create embed
        embed = discord.Embed(
            title=f"🏆 {target_user.display_name}'s Achievements",
            color=discord.Color.gold()
        )
        
        # Add stats
        embed.add_field(
            name="📊 Statistics",
            value=(
                f"**Unlocked:** {stats['unlocked_count']}/{stats['total_count']} "
                f"({stats['completion_percentage']:.1f}%)\n"
                f"**Achievement Points:** {stats['total_points']:,}"
            ),
            inline=False
        )
        
        # Add category progress
        if stats['categories']:
            category_text = ""
            for category, data in stats['categories'].items():
                percentage = (data['unlocked'] / data['total']) * 100 if data['total'] > 0 else 0
                category_text += f"**{category.title()}:** {data['unlocked']}/{data['total']} ({percentage:.0f}%)\n"
            
            embed.add_field(
                name="📂 By Category",
                value=category_text,
                inline=False
            )
        
        # Show recent unlocked achievements (max 5)
        if unlocked_achievements:
            recent_achievements = sorted(
                unlocked_achievements, 
                key=lambda a: achievement_system.get_user_achievement(user_id, a.id).unlock_date or "", 
                reverse=True
            )[:5]
            
            recent_text = ""
            for achievement in recent_achievements:
                recent_text += f"{achievement.emoji} **{achievement.name}**\n"
            
            embed.add_field(
                name="🏅 Recent Achievements",
                value=recent_text or "None yet!",
                inline=False
            )
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        logger.error(f"Error in achievements command: {e}")
        await ctx.send("❌ Error retrieving achievements data.")


@bot.command(aliases=["achprogress", "progress"])
async def achievementprogress(ctx, *, achievement_name: str = None):
    """
    View progress on a specific achievement.
    Usage: !achievementprogress <achievement name>
    """
    if not achievement_name:
        # Show available achievements
        available = achievement_system.get_available_achievements(ctx.author.id)
        
        if not available:
            await ctx.send("🎉 You've unlocked all available achievements!")
            return
        
        embed = discord.Embed(
            title="🎯 Available Achievements",
            description="Use `!achievementprogress <name>` to see progress on a specific achievement.",
            color=discord.Color.blue()
        )
        
        # Group by category
        by_category = {}
        for achievement in available:
            if achievement.category not in by_category:
                by_category[achievement.category] = []
            by_category[achievement.category].append(achievement)
        
        for category, achievements in by_category.items():
            achievement_list = ""
            for achievement in achievements[:5]:  # Limit to 5 per category
                achievement_list += f"{achievement.emoji} **{achievement.name}**\n"
            
            if len(achievements) > 5:
                achievement_list += f"... and {len(achievements) - 5} more"
            
            embed.add_field(
                name=f"📂 {category.title()}",
                value=achievement_list,
                inline=False
            )
        
        await ctx.send(embed=embed)
        return
    
    # Find achievement by name (partial match)
    achievement = None
    for ach in achievement_system.achievements.values():
        if achievement_name.lower() in ach.name.lower():
            achievement = ach
            break
    
    if not achievement:
        await ctx.send(f"❌ Achievement '{achievement_name}' not found.")
        return
    
    # Get current user stats for accurate progress tracking
    current_stats = {}
    
    try:
        # Get message count and level
        user_messages = contributions.get(str(ctx.author.id), 0)
        current_stats["messages"] = user_messages
        current_stats["level"] = get_user_level(str(ctx.author.id))
        
        # Get current time info
        current_hour = datetime.datetime.now().hour
        current_stats["early_message"] = 5 <= current_hour <= 7
        current_stats["night_message"] = current_hour >= 23 or current_hour <= 3
        current_stats["midnight_message"] = current_hour == 0
        
        # Add guild member time data for time-based achievements
        if ctx.guild and ctx.author in ctx.guild.members:
            member = ctx.guild.get_member(ctx.author.id)
            if member and member.joined_at:
                join_date = member.joined_at
                now = datetime.datetime.now(datetime.timezone.utc)
                days_in_server = (now - join_date).days
                current_stats["days_in_server"] = days_in_server
                current_stats["total_active_days"] = days_in_server
                current_stats["consecutive_days"] = min(days_in_server, 30)
                current_stats["weekend_messages"] = days_in_server >= 7
        
        # Get achievement progress from stored data (for command/game stats) 
        # combined with current stats (for message/level/time stats)
        for achievement_id in achievement_system.achievements:
            user_achievement = achievement_system.get_user_achievement(ctx.author.id, achievement_id)
            for key, value in user_achievement.progress.items():
                if key not in current_stats:  # Don't override current real-time stats
                    current_stats[key] = value
                    
    except Exception as e:
        logger.error(f"Error getting current user stats for progress: {e}")
    
    # Get progress with current stats
    progress_info = achievement_system.get_achievement_progress(ctx.author.id, achievement.id, current_stats)
    
    if progress_info["unlocked"]:
        embed = EmbedHelper.create_success_embed(
            f"🏆 {achievement.emoji} {achievement.name}",
            f"{achievement.description}\n\n✅ **Unlocked on:** {progress_info['unlock_date'][:10] if progress_info['unlock_date'] else 'Unknown'}"
        )
    else:
        embed = EmbedHelper.create_info_embed(
            f"🎯 {achievement.emoji} {achievement.name}",
            achievement.description
        )
        
        # Add progress bars
        progress_text = ""
        for req_key, req_data in progress_info["progress"].items():
            current = req_data["current"]
            required = req_data["required"]
            percentage = req_data["percentage"]
            
            # Create progress bar
            filled = int(percentage / 10)
            empty = 10 - filled
            bar = "█" * filled + "░" * empty
            
            if isinstance(required, bool):
                progress_text += f"**{req_key.replace('_', ' ').title()}:** {'✅' if current else '❌'}\n"
            else:
                progress_text += f"**{req_key.replace('_', ' ').title()}:** {current:,}/{required:,} ({percentage:.1f}%)\n{bar}\n\n"
        
        embed.add_field(
            name="📊 Progress",
            value=progress_text or "No progress tracking available.",
            inline=False
        )
        
        if achievement.reward_points > 0:
            embed.add_field(
                name="🎁 Reward",
                value=f"{achievement.reward_points} points" + (f" + {achievement.reward_role} role" if achievement.reward_role else ""),
                inline=False
            )
    
    await ctx.send(embed=embed)


@bot.event
async def on_message(message):
    if message.author.bot:
        return
    
    # Update last active timestamp
    last_active[str(message.author.id)] = time.time()
    save_last_active(last_active)
    
    # Add contribution for active users
    await add_contribution(message.author.id, 1, message.channel, message.author)
    
    # Check for achievement unlocks
    try:
        user_id = message.author.id
        current_messages = contributions.get(str(user_id), 0)
        current_level = get_user_level(str(user_id))
        current_hour = datetime.datetime.now().hour
        
        # Analyze message content for various features
        message_content = message.content
        has_emoji = bool(re.search(r'<:\w+:\d+>|[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]', message_content))
        has_exclamation = '!' in message_content
        has_question = '?' in message_content
        has_link = bool(re.search(r'https?://|www\.|\b\w+\.\w{2,}\b', message_content))
        has_attachment = len(message.attachments) > 0
        mention_count = len(message.mentions)
        
        newly_unlocked = check_message_achievements(
            user_id, current_messages, current_level, current_hour,
            has_emoji=has_emoji, has_exclamation=has_exclamation, 
            has_question=has_question, has_link=has_link,
            has_attachment=has_attachment, mention_count=mention_count
        )
        
        # Notify user of new achievements via dedicated channel
        for achievement in newly_unlocked:
            # Send to specific achievement channel
            await send_achievement_notification(bot, message.author, achievement)
            
            # Award achievement points
            if achievement.reward_points > 0:
                user_obj = bot.get_user(user_id) or message.author
                await add_contribution(user_id, achievement.reward_points, message.channel, user_obj)
                
            logger.info(f"Achievement {achievement.id} unlocked for user {user_id}")
    
    except Exception as e:
        logger.error(f"Error checking achievements: {e}")
    
    # Enhanced message analysis for special achievements
    try:
        message_content = message.content
        message_length = len(message_content)
        
        # Build special stats for this message
        special_stats = {}
        
        # Check for caps lock messages
        if message_content.isupper() and message_length > 1:
            user_achievement = achievement_system.get_user_achievement(message.author.id, "caps_lock_warrior")
            caps_count = user_achievement.progress.get("caps_messages", 0) + 1
            special_stats["caps_messages"] = caps_count
        
        # Check for short messages (5 or fewer characters)
        if message_length <= 5 and message_length > 0:
            user_achievement = achievement_system.get_user_achievement(message.author.id, "short_and_sweet")
            short_count = user_achievement.progress.get("short_messages", 0) + 1
            special_stats["short_messages"] = short_count
        
        # Check for long messages (500+ characters)
        if message_length >= 500:
            special_stats["long_message"] = True
        
        # Check for question messages (contains ?)
        if "?" in message_content:
            user_achievement = achievement_system.get_user_achievement(message.author.id, "question_master")
            question_count = user_achievement.progress.get("question_messages", 0) + 1
            special_stats["question_messages"] = question_count
        
        # Check for birthday messages (contains "happy birthday" or birthday emojis)
        birthday_keywords = ["happy birthday", "bday", "🎂", "🎉", "🥳", "🎈", "🎁"]
        message_lower = message_content.lower()
        has_birthday_content = any(keyword in message_lower for keyword in birthday_keywords)
        
        if has_birthday_content:
            user_achievement = achievement_system.get_user_achievement(message.author.id, "birthday_celebration")
            birthday_count = user_achievement.progress.get("birthday_messages", 0) + 1
            special_stats["birthday_messages"] = birthday_count
        
        # Check special achievements if we have any stats
        if special_stats:
            newly_unlocked = check_special_achievements(message.author.id, special_stats)
            
            for achievement in newly_unlocked:
                # Send to specific achievement channel
                await send_achievement_notification(bot, message.author, achievement)
                
                if achievement.reward_points > 0:
                    await add_contribution(message.author.id, achievement.reward_points, message.channel, message.author)
        
        # Check social achievements if we have birthday messages
        if "birthday_messages" in special_stats:
            social_stats = {"birthday_messages": special_stats["birthday_messages"]}
            newly_unlocked = check_social_achievements(message.author.id, social_stats)
            
            for achievement in newly_unlocked:
                # Send to specific achievement channel
                await send_achievement_notification(bot, message.author, achievement)
                
                if achievement.reward_points > 0:
                    await add_contribution(message.author.id, achievement.reward_points, message.channel, message.author)
    
    except Exception as e:
        logger.error(f"Error checking special achievements: {e}")
    
    
    # Handle counting game - check if it's in the configured counting channel
    counting_channel_id = counting_state.get("channel_id", 000000000000000000)  # Get from state or use placeholder
    if (counting_state["channel_id"] == message.channel.id and
        message.channel.id == counting_channel_id and  # Ensure it's the specific counting channel
        message.content.isdigit()):
        
        number = int(message.content)
        expected = counting_state["current"] + 1
        
        if (number == expected and 
            counting_state["last_user"] != message.author.id):
            
            counting_state["current"] = number
            counting_state["last_user"] = message.author.id
            save_counting_state(counting_state)
            
            # Bonus points for counting
            await add_contribution(message.author.id, 2, message.channel, message.author)
            
            # Track counting achievements
            try:
                # Get the current user achievement for counting_contributor
                user_achievement = achievement_system.get_user_achievement(message.author.id, "counting_contributor")
                current_contributions = user_achievement.progress.get("counting_contributions", 0) + 1
                
                # Update the achievement progress FIRST
                achievement_system.get_user_achievement(message.author.id, "counting_contributor").progress["counting_contributions"] = current_contributions
                # Mark that progress was updated
                achievement_system._progress_updated = True
                
                counting_stats = {"counting_contributions": current_contributions}
                
                # Enhanced milestone detection for perfectionist achievement
                is_milestone = (
                    number % 100 == 0 or     # Every 100
                    number % 500 == 0 or     # Every 500
                    number % 1000 == 0 or    # Every 1000
                    number in [50, 69, 250, 420, 666, 750, 777, 888, 999]  # Special milestones
                )
                
                if is_milestone:
                    counting_stats["counting_milestone"] = True
                    # Track how many milestones this user has hit
                    milestone_achievement = achievement_system.get_user_achievement(message.author.id, "milestone_hunter")
                    milestones_hit = milestone_achievement.progress.get("milestones_hit", 0) + 1
                    counting_stats["milestones_hit"] = milestones_hit
                    # Update milestone progress too
                    achievement_system.get_user_achievement(message.author.id, "milestone_hunter").progress["milestones_hit"] = milestones_hit
                    # Mark that progress was updated
                    achievement_system._progress_updated = True
                
                # Save the updated progress
                achievement_system.force_save_progress()
                
                newly_unlocked = check_counting_achievements(message.author.id, counting_stats)
                
                for achievement in newly_unlocked:
                    await send_achievement_notification(bot, message.author, achievement)
                    
                    if achievement.reward_points > 0:
                        await add_contribution(message.author.id, achievement.reward_points, message.channel, message.author)
                
                # Log the counting contribution for debugging
                logger.info(f"User {message.author.id} counting contribution {current_contributions}/10 (number {number})")
            
            except Exception as e:
                logger.error(f"Error tracking counting achievement: {e}")
                logger.error(traceback.format_exc())
            
            # Milestone rewards
            if number % 100 == 0:
                bonus = 50
                await add_contribution(message.author.id, bonus, message.channel, message.author)
                await message.add_reaction("🎉")
                await message.channel.send(f"🎉 **Milestone reached!** {message.author.mention} hit {number}! Bonus: {bonus} points!")
            elif number % 50 == 0:
                await message.add_reaction("🎊")
            elif number % 10 == 0:
                await message.add_reaction("✨")
            else:
                await message.add_reaction("✅")
                
        elif number != expected:
            # Wrong number - reset counting
            counting_state["current"] = 0
            counting_state["last_user"] = None
            save_counting_state(counting_state)
            await message.add_reaction("❌")
            await message.channel.send(f"💥 **Counting failed!** Expected {expected}, got {number}. Restarting from 1!")
        elif counting_state["last_user"] == message.author.id:
            # Same user counting twice
            await message.add_reaction("⏸️")
            await message.channel.send(f"⏸️ {message.author.mention}, you can't count twice in a row! Someone else must count {expected}.")
    
    # Chatterbot response logic
    try:
        if not message.content.startswith('!'):  # Don't respond to commands
            # Check if the bot is mentioned in the message
            bot_mentioned = bot.user in message.mentions
            if bot_mentioned:
                response = chat_bot.get_response(
                    message.content, 
                    str(message.author.id), 
                    message.author.display_name, 
                    str(message.channel.id),
                    mentions_bot=True
                )
                if response:
                    await message.channel.send(response)
    except Exception as e:
        logger.error(f"Chatterbot error: {e}")
    
    # IMPORTANT: Process commands after handling the message
    await bot.process_commands(message)
  
# SHOP COMMAND ---------------------------------------------------
@bot.command()
async def shop(ctx):
    """
    Interactive tiered shop system - Browse roles by category!
    Usage: !shop
    """
    try:
        # Get user's current points and roles
        user_id = str(ctx.author.id)
        user_points = contributions.get(user_id, 0)
        user_roles = [role.name for role in ctx.author.roles if role.name != "@everyone"]
        
        # Create tier selection embed
        embed = ShopHelper.create_tier_selection_embed(user_points)
        
        # Send initial message
        message = await ctx.send(embed=embed)
        
        # Add reaction buttons for tier selection
        emojis = ShopHelper.get_reaction_emojis()
        tier_reactions = [emojis["tier_1"], emojis["tier_2"], emojis["tier_3"], 
                         emojis["tier_4"], emojis["tier_5"], emojis["tier_6"], emojis["cancel"]]
        
        for emoji in tier_reactions:
            await message.add_reaction(emoji)
        
        # Wait for user reactions
        def check(reaction, user):
            return (user == ctx.author and 
                   str(reaction.emoji) in tier_reactions and 
                   reaction.message.id == message.id)
        
        # State management for navigation
        current_state = "tier_selection"
        selected_tier = None
        timeout = 60  # 1 minute timeout
        
        while True:
            try:
                reaction, user = await bot.wait_for('reaction_add', timeout=timeout, check=check)
                
                # Remove user's reaction
                try:
                    await message.remove_reaction(reaction.emoji, user)
                except:
                    pass
                
                emoji_str = str(reaction.emoji)
                
                # Handle cancellation
                if emoji_str == emojis["cancel"]:
                    await message.delete()
                    break
                
                # Handle tier selection
                if current_state == "tier_selection":
                    tier_map = {
                        emojis["tier_1"]: "Legendary",
                        emojis["tier_2"]: "Epic", 
                        emojis["tier_3"]: "Rare",
                        emojis["tier_4"]: "Common",
                        emojis["tier_5"]: "Starter",
                        emojis["tier_6"]: "Special Achievement"
                    }
                    
                    if emoji_str in tier_map:
                        selected_tier = tier_map[emoji_str]
                        
                        # Create tier browse embed
                        embed = ShopHelper.create_tier_browse_embed(selected_tier, user_points, user_roles)
                        await message.edit(embed=embed)
                        
                        # Clear old reactions and add new ones
                        await message.clear_reactions()
                        
                        # Add number reactions for role selection (1-10) + navigation
                        selection_reactions = [emojis["select_1"], emojis["select_2"], emojis["select_3"],
                                             emojis["select_4"], emojis["select_5"], emojis["select_6"],
                                             emojis["select_7"], emojis["select_8"], emojis["select_9"],
                                             emojis["select_10"], emojis["back"], emojis["cancel"]]
                        
                        for emoji in selection_reactions:
                            await message.add_reaction(emoji)
                        
                        current_state = "role_selection"
                        
                        # Update check function for role selection
                        def check(reaction, user):
                            return (user == ctx.author and 
                                   str(reaction.emoji) in selection_reactions and 
                                   reaction.message.id == message.id)
                
                # Handle role selection
                elif current_state == "role_selection":
                    if emoji_str == emojis["back"]:
                        # Go back to tier selection
                        embed = ShopHelper.create_tier_selection_embed(user_points)
                        await message.edit(embed=embed)
                        
                        # Clear reactions and add tier selection reactions
                        await message.clear_reactions()
                        for emoji in tier_reactions:
                            await message.add_reaction(emoji)
                        
                        current_state = "tier_selection"
                        selected_tier = None
                        
                        # Reset check function
                        def check(reaction, user):
                            return (user == ctx.author and 
                                   str(reaction.emoji) in tier_reactions and 
                                   reaction.message.id == message.id)
                    
                    else:
                        # Handle role number selection
                        number_map = {
                            emojis["select_1"]: 1, emojis["select_2"]: 2, emojis["select_3"]: 3,
                            emojis["select_4"]: 4, emojis["select_5"]: 5, emojis["select_6"]: 6,
                            emojis["select_7"]: 7, emojis["select_8"]: 8, emojis["select_9"]: 9,
                            emojis["select_10"]: 10
                        }
                        
                        if emoji_str in number_map:
                            role_index = number_map[emoji_str] - 1  # Convert to 0-based index
                            
                            # Get roles in selected tier
                            tiers = ShopHelper.get_shop_tiers()
                            roles_in_tier = tiers.get(selected_tier, [])
                            
                            if role_index < len(roles_in_tier):
                                role_name, role_details = roles_in_tier[role_index]
                                
                                # Create purchase embed
                                embed = ShopHelper.create_role_purchase_embed(role_name, role_details, user_points, user_roles)
                                await message.edit(embed=embed)
                                
                                # Clear reactions and add navigation only
                                await message.clear_reactions()
                                nav_reactions = [emojis["back"], emojis["cancel"]]
                                for emoji in nav_reactions:
                                    await message.add_reaction(emoji)
                                
                                current_state = "purchase_view"
                                
                                # Update check function for purchase view
                                def check(reaction, user):
                                    return (user == ctx.author and 
                                           str(reaction.emoji) in nav_reactions and 
                                           reaction.message.id == message.id)
                
                # Handle purchase view navigation
                elif current_state == "purchase_view":
                    if emoji_str == emojis["back"]:
                        # Go back to tier browse
                        embed = ShopHelper.create_tier_browse_embed(selected_tier, user_points, user_roles)
                        await message.edit(embed=embed)
                        
                        # Reset to role selection state
                        await message.clear_reactions()
                        selection_reactions = [emojis["select_1"], emojis["select_2"], emojis["select_3"],
                                             emojis["select_4"], emojis["select_5"], emojis["select_6"],
                                             emojis["select_7"], emojis["select_8"], emojis["select_9"],
                                             emojis["select_10"], emojis["back"], emojis["cancel"]]
                        
                        for emoji in selection_reactions:
                            await message.add_reaction(emoji)
                        
                        current_state = "role_selection"
                        
                        # Reset check function
                        def check(reaction, user):
                            return (user == ctx.author and 
                                   str(reaction.emoji) in selection_reactions and 
                                   reaction.message.id == message.id)
                
            except asyncio.TimeoutError:
                # Timeout - remove reactions and add timeout message
                await message.clear_reactions()
                timeout_embed = discord.Embed(
                    title="⏰ Shop Session Expired",
                    description="Shop interface timed out due to inactivity.\nUse `!shop` to browse again!",
                    color=discord.Color.orange()
                )
                await message.edit(embed=timeout_embed)
                break
        
        logger.info(f"Interactive shop session completed for {ctx.author}")
        
    except Exception as e:
        logger.error(f"Error in interactive shop command: {e}")
        try:
            error_embed = discord.Embed(
                title="❌ Shop Error",
                description="An error occurred while loading the shop.\nPlease try again later.",
                color=discord.Color.red()
            )
            await ctx.send(embed=error_embed)
        except:
            await ctx.send("❌ Error displaying shop. Please try again later.")


@bot.command(name='reload_data')
async def reload_data_command(ctx):
    """
    Reload all data from .txt files.
    Usage: !reload_data
    
    ⚠️ OWNER ONLY - Manually reload data from database files
    """
    # Security check - only allow bot owner
    owner_id = BOT_CONFIG.get('owner_id')
    if not owner_id or ctx.author.id != owner_id:
        await ctx.send("❌ This command is restricted to the bot owner only!")
        return
    
    try:
        await ctx.send("🔄 Reloading data from .txt files...")
        
        # Reload all data
        load_contributions()
        load_lifetime_earnings()
        
        embed = discord.Embed(
            title="✅ Data Reloaded Successfully",
            description="All data has been reloaded from .txt files.",
            color=discord.Color.green()
        )
        
        embed.add_field(
            name="📊 Statistics",
            value=f"Contributions: {len(contributions)} users\nLifetime Earnings: {len(lifetime_earnings)} users",
            inline=False
        )
        
        await ctx.send(embed=embed)
        logger.info("Data manually reloaded from .txt files")
        
    except Exception as e:
        error_embed = discord.Embed(
            title="❌ Data Reload Failed",
            description=f"Error: {str(e)}",
            color=discord.Color.red()
        )
        await ctx.send(embed=error_embed)
        logger.error(f"Manual data reload failed: {e}")


@bot.command(name='test_data')
async def test_data_loading(ctx):
    """
    Test data loading from existing .txt files.
    Usage: !test_data
    
    ⚠️ OWNER ONLY - Debug command to verify data integration
    """
    # Security check - only allow bot owner
    owner_id = BOT_CONFIG.get('owner_id')
    if not owner_id or ctx.author.id != owner_id:
        await ctx.send("❌ This command is restricted to the bot owner only!")
        return
    
    try:
        # Create backup of current data
        current_contributions = contributions.copy()
        current_lifetime_earnings = lifetime_earnings.copy()
        
        # Test loading from .txt files
        await ctx.send("🔄 Testing data loading from .txt files...")
        
        # Load contributions
        load_contributions()
        contrib_count = len(contributions)
        contrib_total = sum(contributions.values())
        
        # Load lifetime earnings
        load_lifetime_earnings()
        earnings_count = len(lifetime_earnings)
        earnings_total = sum(lifetime_earnings.values())
        
        # Create result embed
        embed = discord.Embed(
            title="📊 Data Loading Test Results",
            color=discord.Color.green()
        )
        
        embed.add_field(
            name="📈 Contributions Data",
            value=f"Users loaded: {contrib_count}\nTotal points: {contrib_total:,}",
            inline=True
        )
        
        embed.add_field(
            name="💰 Lifetime Earnings Data",
            value=f"Users loaded: {earnings_count}\nTotal earnings: {earnings_total:,}",
            inline=True
        )
        
        # Show sample data if available
        if contributions:
            sample_user = list(contributions.keys())[0]
            sample_points = contributions[sample_user]
            embed.add_field(
                name="📝 Sample Contribution",
                value=f"User: {sample_user}\nPoints: {sample_points}",
                inline=False
            )
        
        if lifetime_earnings:
            sample_user = list(lifetime_earnings.keys())[0]
            sample_earnings = lifetime_earnings[sample_user]
            embed.add_field(
                name="💼 Sample Earnings",
                value=f"User: {sample_user}\nEarnings: {sample_earnings}",
                inline=False
            )
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        error_embed = discord.Embed(
            title="❌ Data Loading Test Failed",
            description=f"Error: {str(e)}",
            color=discord.Color.red()
        )
        await ctx.send(embed=error_embed)


@bot.command(name='debug')
async def debug_command(ctx, *, code: str = None):
    """
    Execute Python code for debugging purposes.
    Usage: !debug <python_code>
    
    ⚠️ OWNER ONLY - This command can execute arbitrary Python code!
    """
    # Security check - only allow bot owner
    owner_id = BOT_CONFIG.get('owner_id')
    if not owner_id or ctx.author.id != owner_id:
        await ctx.send("❌ This command is restricted to the bot owner only!")
        return
    
    if not code:
        embed = discord.Embed(
            title="🐛 Debug Command",
            description="Execute Python code for debugging purposes.",
            color=discord.Color.orange()
        )
        embed.add_field(
            name="Usage Examples",
            value="```\n!debug print('Hello World')\n!debug ctx.author.id\n!debug len(contributions)\n!debug bot.guilds[0].member_count\n```",
            inline=False
        )
        embed.add_field(
            name="Available Variables",
            value="```\nctx - Command context\nbot - Bot instance\ncontributions - User contributions dict\ncounting_state - Counting game state\nlast_active - User activity dict\ndiscord - Discord module\nasyncio - Asyncio module\nlogger - Bot logger\ndatetime - Datetime module\nrandom - Random module\nachievement_system - Achievement system\nBOT_CONFIG - Bot configuration\nWeeklyContributionManager - Weekly leaderboard manager\nDataManager - Data file manager\nDATA_FILES - File paths dictionary\nload_contributions() - Reload contribution data\nload_lifetime_earnings() - Reload earnings data\nsave_contributions() - Save contribution data\nsave_lifetime_earnings() - Save earnings data\n```",
            inline=False
        )
        embed.add_field(
            name="⚠️ Security Warning",
            value="This command can execute **any** Python code. Use with extreme caution!\nOnly the bot owner can use this command.",
            inline=False
        )
        await ctx.send(embed=embed)
        return
    
    try:
        # Import necessary modules for code execution
        import io
        import contextlib
        
        # Create a safe execution environment with common variables
        safe_globals = {
            '__builtins__': {
                'print': print,
                'len': len,
                'str': str,
                'int': int,
                'float': float,
                'bool': bool,
                'list': list,
                'dict': dict,
                'set': set,
                'tuple': tuple,
                'range': range,
                'enumerate': enumerate,
                'zip': zip,
                'sum': sum,
                'max': max,
                'min': min,
                'abs': abs,
                'round': round,
                'sorted': sorted,
                'reversed': reversed,
                'any': any,
                'all': all,
                'type': type,
                'isinstance': isinstance,
                'hasattr': hasattr,
                'getattr': getattr,
                'setattr': setattr,
            },
            'ctx': ctx,
            'bot': bot,
            'contributions': contributions,
            'counting_state': counting_state,
            'last_active': last_active,
            'discord': discord,
            'asyncio': asyncio,
            'logger': logger,
            'datetime': datetime,
            'random': random,
            'achievement_system': achievement_system,
            'BOT_CONFIG': BOT_CONFIG,
            'add_contribution': add_contribution,
            'save_contributions': save_contributions,
            'get_level': get_level,
            'WeeklyContributionManager': WeeklyContributionManager,
            'DataManager': DataManager,
            'DATA_FILES': DATA_FILES,
        }
        
        # Capture output
        output_buffer = io.StringIO()
        
        # Try to evaluate as expression first (for simple values)
        try:
            with contextlib.redirect_stdout(output_buffer):
                result = eval(code, safe_globals)
                if result is not None:
                    print(repr(result))
        except SyntaxError:
            # If it's not an expression, try to execute as statement
            output_buffer = io.StringIO()
            with contextlib.redirect_stdout(output_buffer):
                exec(code, safe_globals)
        
        # Get the output
        output = output_buffer.getvalue()
        
        # Format the response
        embed = discord.Embed(
            title="🐛 Debug Command Executed",
            color=discord.Color.green()
        )
        
        # Show the code that was executed (truncate if too long)
        code_display = code
        if len(code) > 500:
            code_display = code[:500] + "\n... (truncated)"
        
        embed.add_field(
            name="📝 Code",
            value=f"```python\n{code_display}\n```",
            inline=False
        )
        
        # Show the output
        if output.strip():
            # Truncate long output to fit Discord limits
            output_display = output.strip()
            if len(output_display) > 1000:
                output_display = output_display[:1000] + "\n... (truncated)"
            embed.add_field(
                name="📤 Output",
                value=f"```\n{output_display}\n```",
                inline=False
            )
        else:
            embed.add_field(
                name="📤 Output",
                value="```\n(No output)\n```",
                inline=False
            )
        
        embed.set_footer(text="✅ Executed successfully")
        await ctx.send(embed=embed)
        
        # Log the debug command usage
        logger.info(f"Debug command executed by {ctx.author}: {code[:100]}...")
        
    except Exception as e:
        # Handle errors gracefully
        embed = discord.Embed(
            title="🐛 Debug Command Error",
            color=discord.Color.red()
        )
        
        # Show the code that caused the error (truncate if too long)
        code_display = code
        if len(code) > 500:
            code_display = code[:500] + "\n... (truncated)"
        
        embed.add_field(
            name="📝 Code",
            value=f"```python\n{code_display}\n```",
            inline=False
        )
        
        error_msg = f"{type(e).__name__}: {str(e)}"
        if len(error_msg) > 1000:
            error_msg = error_msg[:1000] + "... (truncated)"
        
        embed.add_field(
            name="❌ Error",
            value=f"```\n{error_msg}\n```",
            inline=False
        )
        
        embed.set_footer(text="❌ Execution failed")
        await ctx.send(embed=embed)
        
        # Log the error
        logger.error(f"Debug command error by {ctx.author}: {code[:100]}... - {e}")


@bot.command(name="debugsaveprogress")
@commands.is_owner()
async def debug_save_progress(ctx):
    """Force save any pending achievement progress updates."""
    try:
        achievement_system.force_save_progress()
        await ctx.send("✅ **Achievement progress forcibly saved!**")
        logger.info(f"DEV: {ctx.author} forced achievement progress save")
    except Exception as e:
        await ctx.send(f"❌ **Error saving progress:** {str(e)}")
        logger.error(f"Error in debug save progress: {e}")


@bot.command(name='debugachievements', aliases=['debugach'])
async def debug_achievements_command(ctx, category: str = "time", user: discord.Member = None):
    """
    Debug command to manually check and unlock achievements for users.
    Usage: 
    - !debugach time [@user] - Check time-based achievements (default)
    - !debugach message [@user] - Check message-based achievements  
    - !debugach social [@user] - Check social achievements
    - !debugach milestone [@user] - Check milestone achievements
    - !debugach all [@user] - Check ALL achievement types
    - !debugach easy [@user] - Check easy-to-obtain achievements
    
    ⚠️ OWNER ONLY - Force checks achievements for users.
    """
    # Security check - only allow bot owner
    owner_id = BOT_CONFIG.get('owner_id')
    if not owner_id or ctx.author.id != owner_id:
        await ctx.send("❌ This command is restricted to the bot owner only!")
        return

    valid_categories = ["time", "message", "social", "milestone", "all", "easy"]
    if category.lower() not in valid_categories:
        await ctx.send(f"❌ Invalid category! Valid options: {', '.join(valid_categories)}")
        return
    
    category = category.lower()
    
    if user:
        # Check specific user
        users_to_check = [user]
        action_text = f"Checking **{category}** achievements for **{user.display_name}**"
    else:
        # Check ALL users in the server (limit to 50 for safety)
        all_members = [member for member in ctx.guild.members if not member.bot]
        users_to_check = all_members[:50]  # Safety limit
        action_text = f"Checking **{category}** achievements for **{len(users_to_check)}** users"
    
    embed = discord.Embed(
        title=f"🐛 Debug Achievements - {category.title()} Category",
        description=action_text,
        color=discord.Color.orange()
    )
    
    await ctx.send(embed=embed)
    
    total_newly_unlocked = []
    users_with_new_achievements = 0
    processed_users = 0
    
    # Send progress update
    progress_msg = await ctx.send(f"🔄 Processing users: 0/{len(users_to_check)}")
    
    try:
        for i, target_user in enumerate(users_to_check):
            guild_member = ctx.guild.get_member(target_user.id)
            if not guild_member:
                continue
                
            newly_unlocked = []
            
            if category == "time" or category == "all":
                newly_unlocked.extend(debug_check_time_achievements(target_user.id, guild_member))
            
            if category == "message" or category == "all":
                newly_unlocked.extend(debug_check_message_achievements(target_user.id, guild_member))
                
            if category == "social" or category == "all":
                newly_unlocked.extend(debug_check_social_achievements(target_user.id, guild_member))
                
            if category == "milestone" or category == "all":
                newly_unlocked.extend(debug_check_milestone_achievements(target_user.id, guild_member))
                
            if category == "easy" or category == "all":
                newly_unlocked.extend(debug_check_easy_achievements(target_user.id, guild_member))

            if newly_unlocked:
                users_with_new_achievements += 1
                total_newly_unlocked.extend(newly_unlocked)
                
                # Send achievement notifications
                for achievement in newly_unlocked:
                    try:
                        await send_achievement_notification(bot, target_user, achievement)
                        
                        if achievement.reward_points > 0:
                            await add_contribution(target_user.id, achievement.reward_points * 10, ctx.channel)
                            
                    except Exception as notif_error:
                        logger.error(f"Error sending achievement notification: {notif_error}")
                
                logger.info(f"Debug achievements: {target_user.display_name} unlocked {len(newly_unlocked)} achievements")
            
            processed_users += 1
            
            # Update progress every 10 users or at the end
            if (i + 1) % 10 == 0 or i == len(users_to_check) - 1:
                try:
                    await progress_msg.edit(content=f"🔄 Processing users: {processed_users}/{len(users_to_check)}")
                except:
                    pass
        
        # Final results
        results_embed = discord.Embed(
            title=f"✅ Debug {category.title()} Achievements - Complete!",
            color=discord.Color.green()
        )
        
        results_embed.add_field(
            name="📊 Summary",
            value=f"**Users Processed:** {processed_users}\n"
                  f"**Users with New Achievements:** {users_with_new_achievements}\n"
                  f"**Total Achievements Unlocked:** {len(total_newly_unlocked)}",
            inline=False
        )
        
        if total_newly_unlocked:
            # Count achievements by type
            achievement_counts = {}
            for achievement in total_newly_unlocked:
                if achievement.name not in achievement_counts:
                    achievement_counts[achievement.name] = 0
                achievement_counts[achievement.name] += 1
            
            # Show top unlocked achievements
            top_achievements = sorted(achievement_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            achievement_text = "\n".join([f"• **{name}**: {count} users" for name, count in top_achievements])
            
            if len(achievement_counts) > 10:
                achievement_text += f"\n... and {len(achievement_counts) - 10} more types"
            
            results_embed.add_field(
                name="🏆 Most Unlocked Achievements",
                value=achievement_text,
                inline=False
            )
        else:
            results_embed.add_field(
                name="ℹ️ Results",
                value=f"No new {category} achievements were unlocked. All users are up to date!",
                inline=False
            )
        
        await ctx.send(embed=results_embed)
        
        # Clean up progress message
        try:
            await progress_msg.delete()
        except:
            pass
            
    except Exception as e:
        error_embed = discord.Embed(
            title="❌ Debug Command Error",
            description=f"Error during bulk achievement check: {str(e)}",
            color=discord.Color.red()
        )
        await ctx.send(embed=error_embed)
        logger.error(f"Debug achievements bulk command error: {e}")


@bot.command(name='testachievements', aliases=['testmultipleach'])
async def test_simple_achievements(ctx, user: discord.Member = None):
    """
    Test command to unlock a few easy achievements for testing.
    Usage: !testachievements [@user] - Test achievements for user or yourself
    
    ⚠️ OWNER ONLY - For testing the achievement system
    """
    # Security check
    owner_id = BOT_CONFIG.get('owner_id')
    if not owner_id or ctx.author.id != owner_id:
        await ctx.send("❌ This command is restricted to the bot owner only!")
        return
    
    target_user = user or ctx.author
    
    embed = discord.Embed(
        title="🧪 Testing Achievement System",
        description=f"Running achievement tests for **{target_user.display_name}**",
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed)
    
    try:
        newly_unlocked = []
        
        # Test easy message achievements
        hour = datetime.datetime.now().hour
        test_message_achievements = check_message_achievements(
            target_user.id, 1, 1, hour,
            has_emoji=True, has_exclamation=True, has_question=True,
            has_link=True, has_attachment=True, mention_count=1
        )
        newly_unlocked.extend(test_message_achievements)
        
        # Test easy social achievements  
        test_social_stats = {
            "reactions_added": 1,
            "quick_responses": 1, 
            "birthday_messages": 1,
            "mentions_sent": 1
        }
        test_social_achievements = check_social_achievements(target_user.id, test_social_stats)
        newly_unlocked.extend(test_social_achievements)
        
        # Test time achievements based on current time
        now = datetime.datetime.now()
        test_time_stats = {
            "morning_message": 6 <= now.hour <= 9,
            "afternoon_message": 12 <= now.hour <= 15,
            "evening_message": 18 <= now.hour <= 21,
            "weekend_messages": now.weekday() >= 5
        }
        test_time_achievements = check_time_achievements(target_user.id, test_time_stats)
        newly_unlocked.extend(test_time_achievements)
        
        # Send results
        if newly_unlocked:
            result_embed = discord.Embed(
                title="✅ Achievement Test Results",
                description=f"**{len(newly_unlocked)}** achievements unlocked for {target_user.display_name}!",
                color=discord.Color.green()
            )
            
            achievement_list = []
            total_points = 0
            for achievement in newly_unlocked:
                achievement_list.append(f"{achievement.emoji} **{achievement.name}** ({achievement.reward_points} pts)")
                total_points += achievement.reward_points
                
                # Send notifications
                try:
                    await send_achievement_notification(bot, target_user, achievement)
                    if achievement.reward_points > 0:
                        await add_contribution(target_user.id, achievement.reward_points * 10, ctx.channel)
                except Exception as e:
                    logger.error(f"Error sending test achievement notification: {e}")
            
            result_embed.add_field(
                name="🏆 Unlocked Achievements",
                value="\n".join(achievement_list[:10]),  # Limit to 10 for embed size
                inline=False
            )
            
            result_embed.add_field(
                name="💰 Total Rewards",
                value=f"**{total_points:,}** base points\n**{total_points * 10:,}** contribution points awarded",
                inline=False
            )
            
            await ctx.send(embed=result_embed)
            
        else:
            no_results_embed = discord.Embed(
                title="ℹ️ No New Achievements", 
                description=f"{target_user.display_name} already has all the testable achievements!",
                color=discord.Color.blue()
            )
            await ctx.send(embed=no_results_embed)
            
    except Exception as e:
        error_embed = discord.Embed(
            title="❌ Test Error",
            description=f"Error during achievement test: {str(e)}",
            color=discord.Color.red()
        )
        await ctx.send(embed=error_embed)
        logger.error(f"Achievement test error: {e}")


# CHATTERBOT ADMIN COMMANDS ---------------------------------------------------

@bot.command()
@commands.has_permissions(administrator=True)
async def chatterbot(ctx, action: str = None, *, value: str = None):
    """
    Manage the experimental chatterbot system
    Usage: !chatterbot <action> [value]
    Actions: toggle, status, intelligence, cooldown
    """
    try:
        if action == "toggle":
            chat_bot.toggle()
            status = "enabled ✅" if chat_bot.enabled else "disabled ❌"
            embed = discord.Embed(
                title="🤖 ChatterBot Status",
                description=f"ChatterBot is now **{status}**",
                color=discord.Color.green() if chat_bot.enabled else discord.Color.red()
            )
            await ctx.send(embed=embed)
            
        elif action == "status":
            embed = discord.Embed(
                title="🤖 ChatterBot Status",
                color=discord.Color.blue()
            )
            embed.add_field(name="Status", value="✅ Enabled" if chat_bot.enabled else "❌ Disabled", inline=False)
            embed.add_field(name="Access", value="👑 Owner Only (when bot is @mentioned)", inline=False)
            embed.add_field(name="Cooldown", value=f"{chat_bot.cooldown_seconds}s", inline=True)
            embed.add_field(name="History Length", value=f"{len(chat_bot.conversation_history)}", inline=True)
            
            # Add intelligence stats
            stats = chat_bot.get_intelligence_stats()
            embed.add_field(name="🧠 Intelligence Stats", value=f"Conversations: {stats['total_conversations']}\nMemories: {stats['memories_stored']}\nRelationship Level: {stats['avg_conversations_per_user']:.1f} avg", inline=False)
            await ctx.send(embed=embed)
            
        elif action == "intelligence":
            stats = chat_bot.get_intelligence_stats()
            embed = discord.Embed(
                title="🧠 ChatterBot Intelligence Report",
                color=discord.Color.purple()
            )
            embed.add_field(name="📊 Conversation Stats", value=f"Total Conversations: **{stats['total_conversations']}**\nUnique Users: **{stats['unique_users']}**\nAvg per User: **{stats['avg_conversations_per_user']:.1f}**", inline=False)
            embed.add_field(name="🧠 Memory & Learning", value=f"Memories Stored: **{stats['memories_stored']}**\nUsers with Preferences: **{stats['users_with_preferences']}**", inline=False)
            
            # Show user preferences if available
            if chat_bot.user_preferences:
                owner_prefs = chat_bot.user_preferences.get(str(ctx.author.id), {})
                if owner_prefs:
                    fav_games = owner_prefs.get("favorite_games", [])
                    comm_style = owner_prefs.get("communication_style", "casual")
                    embed.add_field(name="👤 Your Profile", value=f"Communication Style: **{comm_style}**\nFavorite Games: **{', '.join(fav_games[:3]) if fav_games else 'None detected yet'}**", inline=False)
            
            await ctx.send(embed=embed)
            
        elif action == "cooldown":
            if value:
                try:
                    cooldown = int(value)
                    if cooldown >= 0:
                        chat_bot.cooldown_seconds = cooldown
                        embed = discord.Embed(
                            title="🤖 Cooldown Updated",
                            description=f"ChatterBot cooldown set to **{cooldown} seconds**",
                            color=discord.Color.green()
                        )
                    else:
                        raise ValueError("Cooldown must be non-negative")
                except ValueError as e:
                    embed = discord.Embed(
                        title="❌ Invalid Cooldown",
                        description="Please provide a non-negative number",
                        color=discord.Color.red()
                    )
            else:
                embed = discord.Embed(
                    title="🤖 Current Cooldown",
                    description=f"**{chat_bot.cooldown_seconds} seconds**",
                    color=discord.Color.blue()
                )
            await ctx.send(embed=embed)
            
        else:
            embed = discord.Embed(
                title="🤖 ChatterBot Management",
                description="Available actions:",
                color=discord.Color.blue()
            )
            embed.add_field(name="toggle", value="Enable/disable the chatterbot", inline=False)
            embed.add_field(name="status", value="Show current configuration and basic stats", inline=False)
            embed.add_field(name="intelligence", value="Show detailed intelligence and learning stats", inline=False)
            embed.add_field(name="cooldown [seconds]", value="Set/view cooldown period", inline=False)
            await ctx.send(embed=embed)
            
    except Exception as e:
        embed = discord.Embed(
            title="❌ ChatterBot Error",
            description=f"Error managing chatterbot: {str(e)}",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        logger.error(f"ChatterBot management error: {e}")

@bot.command()
@commands.has_permissions(administrator=True)
async def clearhistory(ctx):
    """
    Clear chatterbot conversation history
    Usage: !clearhistory
    """
    try:
        chat_bot.conversation_history.clear()
        embed = discord.Embed(
            title="🧹 History Cleared",
            description="Cleared all conversation history",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
        
    except Exception as e:
        embed = discord.Embed(
            title="❌ Clear History Error",
            description=f"Error clearing history: {str(e)}",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        logger.error(f"Clear history error: {e}")


# Global flag to track if data is fully loaded
data_loaded = False

# Start the bot
bot.run('INSERTYOURBOTTOKENHERE')
