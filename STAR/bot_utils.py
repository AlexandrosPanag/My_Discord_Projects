"""
StarChan Bot Utilities Module
Contains utility functions, configurations, and helper classes for the Discord bot.
"""

import json
import logging
import time
import random
import os
import datetime
from typing import Dict, Any, Optional, List
import discord
from discord.ext import commands

# Set up module logger
logger = logging.getLogger('StarChan.Utils')

# Bot Configuration - PLACEHOLDER VALUES FOR OPEN SOURCE
# Replace these with your actual server/channel IDs when deploying
BOT_CONFIG = {
    "MAIN_SERVER_IDS": {000000000000000000, 000000000000000000},  # Replace with your server IDs
    "main_server_id": 000000000000000000,  # Replace with your primary server ID
    "FORBIDDEN_CHANNEL_IDS": [
        000000000000000000,  # Replace with channels where bot shouldn't work (like rules)
        000000000000000000   # Add more forbidden channel IDs as needed
    ],
    "FORCED_LEVELUP_CHANNEL_ID": 000000000000000000,  # Replace with level-up announcement channel
    "ACHIEVEMENT_CHANNEL_ID": 000000000000000000,  # Replace with achievement notification channel
    "BOT_OWNER_ID": 000000000000000000,  # Replace with your Discord user ID
    "owner_id": 000000000000000000,  # For debug command compatibility
    "ROLE_PRICE": 5000,
    "COUNTING_MILESTONE_BONUS": 50,
    "VIP_ROLE_NAME": "⚜️ VIP ⚜️",  # Legacy - role no longer used
    "RIDDLE_RESET_DAY": 0,  # Monday (0=Monday, 6=Sunday)
}

# File paths
DATA_FILES = {
    "CONTRIBUTIONS": "contributions.txt",
    "LIFETIME_EARNINGS": "lifetime_earnings.txt",  # Total points earned (for level calculation)
    "COUNTING_STATE": "counting_state.txt", 
    "LAST_ACTIVE": "last_active.txt",
    "ACHIEVEMENTS": "achievements_data.txt",
    "RIDDLE_STATE": "riddle_state.txt",  # Weekly riddle state
    "WEEKLY_CONTRIBUTIONS": "weekly_contributions.txt",  # Weekly contribution tracking
    "WEEKLY_TOP_CONTRIBUTORS": "weekly_top_contributors.txt"  # Weekly top 10 for awards
}

# Buyable roles configuration
BUYABLE_ROLES = {
    # Legendary Tier (5000+ points)
    "electric samurai": "⛩️ Electric Samurai⛩️",
    "phoenix ascendant": "🐦‍🔥 Phoenix Ascendant 🐦‍🔥",
    "cosmic guardian": "🌌 Cosmic Guardian 🌌",
    "dragon lord": "🐲 Dragon Lord 🐲",
    "shadow assassin": "🗡️ Shadow Assassin 🗡️",
    "crimson monarch": "👑Crimson Monarch 👑",  # New Legendary Role
    "gambler": "🎲Gambler🎲",  # Special Achievement Role - High Stakes Blackjack Winner
    
    # Epic Tier (3000-4999 points)
    "ashened one": "🔥 Ashened One 🔥",
    "marked one": "☢️ Marked one ☢️",
    "frost warden": "❄️ Frost Warden ❄️",
    "void walker": "🌑 Void Walker 🌑",
    "storm caller": "⚡ Storm Caller ⚡",
    "mystic sage": "🔮 Mystic Sage 🔮",
    
    # Rare Tier (1500-2999 points)
    "pixel prodigy": "🌴Pixel Prodigy 🌴",
    "colonizer": "💂 Colonizer💂",
    "cyber knight": "🤖 Cyber Knight 🤖",
    "neon runner": "🏃‍♂️ Neon Runner 🏃‍♂️",
    "crystal miner": "💎 Crystal Miner 💎",
    "code wizard": "🧙‍♂️ Code Wizard 🧙‍♂️",
    
    # Common Tier (500-1499 points)
    "night owl": "🦉 Night Owl 🦉",
    "coffee addict": "☕ Coffee Addict ☕",
    "meme lord": "😂 Meme Lord 😂",
    "game master": "🎮 Game Master 🎮",
    "music lover": "🎵 Music Lover 🎵",
    "book worm": "📚 Book Worm 📚",
    "artist": "🎨 Artist 🎨",
    "chef": "👨‍🍳 Chef 👨‍🍳",

    # Starter Tier (100-499 points)
    "newcomer": "🌱 Newcomer 🌱",
    "enthusiast": "✨ Enthusiast ✨",
    "explorer": "🗺️ Explorer 🗺️",
    "dreamer": "💭 Dreamer 💭",
    "helper": "🤝 Helper 🤝"
}

# Shop roles with details
SHOP_ROLES = {
    # === LEGENDARY TIER (20000+ POINTS) ===
    "⛩️ Electric Samurai⛩️": {
        "price": 20000,
        "description": "A legendary samurai wielding the power of electricity",
        "rarity": "Legendary",
        "emoji": "⚡"
    },
    "🐦‍🔥 Phoenix Ascendant 🐦‍🔥": {
        "price": 20000,
        "description": "Rise from the ashes with fiery phoenix wings",
        "rarity": "Legendary", 
        "emoji": "🔥"
    },
    "🌌 Cosmic Guardian 🌌": {
        "price": 24000,
        "description": "Protector of the universe and keeper of cosmic secrets",
        "rarity": "Legendary",
        "emoji": "🌌"
    },
    "🐲 Dragon Lord 🐲": {
        "price": 28000,
        "description": "Command the ancient power of dragons",
        "rarity": "Legendary",
        "emoji": "🐲"
    },
    "🗡️ Shadow Assassin 🗡️": {
        "price": 22000,
        "description": "Master of stealth and the art of shadows",
        "rarity": "Legendary",
        "emoji": "🗡️"
    },
    "👑Crimson Monarch 👑": {
        "price": 32000,
        "description": "Supreme ruler with the power of crimson majesty",
        "rarity": "Legendary",
        "emoji": "👑"
    },

    # === SPECIAL ACHIEVEMENT ROLES (NOT PURCHASABLE) ===
    "🎲Gambler🎲": {
        "price": 1999998,  # Doubled impossibly high price to prevent purchase
        "description": "Master of high-stakes gambling - Won blackjack with 10k+ bet",
        "rarity": "Special Achievement",
        "emoji": "🎲"
    },

    # === EPIC TIER (12000-19999 POINTS) ===
    "🔥 Ashened One 🔥": {
        "price": 16000,
        "description": "Born from fire and forged in flames",
        "rarity": "Epic",
        "emoji": "🔥"
    },
    "☢️ Marked one ☢️": {
        "price": 18000,
        "description": "Bearer of the mysterious radioactive mark",
        "rarity": "Epic",
        "emoji": "☢️"
    },
    "❄️ Frost Warden ❄️": {
        "price": 14000,
        "description": "Guardian of the eternal winter realm",
        "rarity": "Epic",
        "emoji": "❄️"
    },
    "🌑 Void Walker 🌑": {
        "price": 16000,
        "description": "Traveler between dimensions and realities",
        "rarity": "Epic",
        "emoji": "🌑"
    },
    "⚡ Storm Caller ⚡": {
        "price": 15200,
        "description": "Master of thunder and lightning",
        "rarity": "Epic",
        "emoji": "⚡"
    },
    "🔮 Mystic Sage 🔮": {
        "price": 16800,
        "description": "Wise keeper of ancient magical knowledge",
        "rarity": "Epic",
        "emoji": "🔮"
    },

    # === RARE TIER (6000-11999 POINTS) ===
    "🌴Pixel Prodigy 🌴": {
        "price": 10000,
        "description": "Master of digital arts and pixel perfection",
        "rarity": "Rare",
        "emoji": "🎨"
    },
    "💂 Colonizer💂": {
        "price": 8000,
        "description": "A distinguished royal guard title",
        "rarity": "Rare",
        "emoji": "👑"
    },
    "🤖 Cyber Knight 🤖": {
        "price": 11200,
        "description": "Futuristic warrior of the digital age",
        "rarity": "Rare",
        "emoji": "🤖"
    },
    "🏃‍♂️ Neon Runner 🏃‍♂️": {
        "price": 8800,
        "description": "Speed demon of the cyberpunk streets",
        "rarity": "Rare",
        "emoji": "💨"
    },
    "💎 Crystal Miner 💎": {
        "price": 7200,
        "description": "Expert at finding the rarest gems",
        "rarity": "Rare",
        "emoji": "💎"
    },
    "⭐ Star Navigator ⭐": {
        "price": 9600,
        "description": "Guide through the cosmic highways",
        "rarity": "Rare",
        "emoji": "⭐"
    },
    "🧙‍♂️ Code Wizard 🧙‍♂️": {
        "price": 10400,
        "description": "Conjurer of elegant algorithms and clean code",
        "rarity": "Rare",
        "emoji": "💻"
    },

    # === COMMON TIER (2000-5999 POINTS) ===
    "🦉 Night Owl 🦉": {
        "price": 3200,
        "description": "Active when the world sleeps",
        "rarity": "Common",
        "emoji": "🌙"
    },
    "☕ Coffee Addict ☕": {
        "price": 2400,
        "description": "Powered by caffeine and determination",
        "rarity": "Common",
        "emoji": "☕"
    },
    "😂 Meme Lord 😂": {
        "price": 4000,
        "description": "Master of internet culture and humor",
        "rarity": "Common",
        "emoji": "😂"
    },
    "🎮 Game Master 🎮": {
        "price": 4800,
        "description": "Ruler of all virtual worlds",
        "rarity": "Common",
        "emoji": "🎮"
    },
    "🎵 Music Lover 🎵": {
        "price": 2800,
        "description": "Life is better with a soundtrack",
        "rarity": "Common",
        "emoji": "🎵"
    },
    "📚 Book Worm 📚": {
        "price": 3600,
        "description": "Knowledge seeker and story enthusiast",
        "rarity": "Common",
        "emoji": "📚"
    },
    "🎨 Artist 🎨": {
        "price": 4400,
        "description": "Creator of beauty and visual wonder",
        "rarity": "Common",
        "emoji": "🎨"
    },
    "👨‍🍳 Chef 👨‍🍳": {
        "price": 3400,
        "description": "Master of culinary arts",
        "rarity": "Common",
        "emoji": "👨‍🍳"
    },

    # === STARTER TIER (400-1999 POINTS) ===
    "🌱 Newcomer 🌱": {
        "price": 600,
        "description": "Fresh face ready to grow",
        "rarity": "Starter",
        "emoji": "🌱"
    },
    "✨ Enthusiast ✨": {
        "price": 1000,
        "description": "Full of energy and excitement",
        "rarity": "Starter",
        "emoji": "✨"
    },
    "🗺️ Explorer 🗺️": {
        "price": 1200,
        "description": "Always seeking new adventures",
        "rarity": "Starter",
        "emoji": "🗺️"
    },
    "💭 Dreamer 💭": {
        "price": 800,
        "description": "Imagination knows no bounds",
        "rarity": "Starter",
        "emoji": "💭"
    },
    "🤝 Helper 🤝": {
        "price": 1600,
        "description": "Always ready to lend a hand",
        "rarity": "Starter",
        "emoji": "🤝"
    }
}

# Game content
PUN_LIST = [
    "I told my wife she was drawing her eyebrows too high. She looked surprised!",
    "Why don't scientists trust atoms? Because they make up everything!",
    "I'm terrified of elevators, so I'm going to start taking steps to avoid them.",
    "Did you hear about the mathematician who's afraid of negative numbers? He'll stop at nothing to avoid them!",
    "I used to hate facial hair, but then it grew on me.",
    "Why don't eggs tell jokes? They'd crack each other up!",
    "I'm reading a book about anti-gravity. It's about time!",
    "The graveyard is so crowded, people are dying to get in!",
    "I wasn't originally going to get a brain transplant, but then I changed my mind.",
    "Why do bees have sticky hair? Because they use honeycombs!",
    "Time flies like an arrow; fruit flies like a banana.",
    "I stayed up all night wondering where the sun went. Then it dawned on me.",
    "What do you call a bear with no teeth? A gummy bear!",
    "I'm friends with 25 letters of the alphabet. I don't know Y.",
    "Why did the bicycle fall over? It was two tired!",
    "I used to be a banker, but I lost interest.",
    "What do you call a fish wearing a crown? A king fish!",
    "I'm trying to organize a hide and seek tournament, but it's really hard to find good players.",
    "Why don't skeletons ever go trick or treating? Because they have no body to go with!",
    "I told a chemistry joke, but there was no reaction.",
    "What did the ocean say to the beach? Nothing, it just waved!",
    "Why did the cookie go to the doctor? Because it felt crumbly!",
    "I'm reading a book on the history of glue. I just can't seem to put it down!",
    "What do you call a sleeping bull? A bulldozer!",
    "Why don't oysters donate? Because they're shellfish!",
    "I used to be addicted to soap, but I'm clean now.",
    "What do you call a dinosaur that crashes his car? Tyrannosaurus Wrecks!",
    "Why did the tomato turn red? Because it saw the salad dressing!",
    "I'm great at multitasking. I can waste time, be unproductive, and procrastinate all at once!",
    "What do you call a belt made of watches? A waist of time!",
    "Why don't some couples go to the gym? Because some relationships don't work out!",
    "I bought some shoes from a drug dealer. I don't know what he laced them with, but I've been tripping all day!",
    "What do you call a fake noodle? An impasta! (Wait, that's a classic!)",
    "Why did the golfer bring two pairs of pants? In case he got a hole in one!",
    "I'm writing a book about hurricanes. It's a real page-turner!",
    "What do you call a cow with no legs? Ground beef!",
    "Why don't scientists trust stairs? Because they're always up to something!",
    "I told my cat a joke about dogs. He didn't find it a-mew-sing!",
    "What do you call a bird that's afraid of heights? A chicken!"
]

EIGHTBALL_RESPONSES = [
    "It is certain.", "It is decidedly so.", "Without a doubt.", "Yes – definitely.",
    "You may rely on it.", "As I see it, yes.", "Most likely.", "Outlook good.",
    "Reply hazy, try again.", "Ask again later.", "Cannot predict now.",
    "Don't count on it.", "My reply is no.", "Outlook not so good.", "Very doubtful."
]

# Weekly riddles collection
WEEKLY_RIDDLES = [
    {
        "riddle": "I have keys but no locks. I have space but no room. You can enter, but you can't go outside. What am I?",
        "answer": ["keyboard", "a keyboard", "computer keyboard"],
        "hint": "You use me to type messages like this one!"
    },
    {
        "riddle": "The more you take, the more you leave behind. What am I?",
        "answer": ["footsteps", "steps", "footprints"],
        "hint": "Think about what you create when you walk."
    },
    {
        "riddle": "I'm tall when I'm young, and short when I'm old. What am I?",
        "answer": ["candle", "a candle"],
        "hint": "I provide light and slowly disappear as I'm used."
    },
    {
        "riddle": "What has hands but cannot clap?",
        "answer": ["clock", "a clock", "watch", "a watch"],
        "hint": "I help you keep track of time."
    },
    {
        "riddle": "I have cities, but no houses. I have mountains, but no trees. I have water, but no fish. What am I?",
        "answer": ["map", "a map"],
        "hint": "I help you navigate and find your way."
    },
    {
        "riddle": "What gets wet while drying?",
        "answer": ["towel", "a towel"],
        "hint": "You use me after taking a shower."
    },
    {
        "riddle": "I'm light as a feather, yet the strongest person can't hold me for five minutes. What am I?",
        "answer": ["breath", "your breath"],
        "hint": "You do this automatically to stay alive."
    },
    {
        "riddle": "What has a head, a tail, is brown, and has no legs?",
        "answer": ["coin", "a coin", "penny"],
        "hint": "I'm something you might find in your pocket or purse."
    },
    {
        "riddle": "What can you break, even if you never pick it up or touch it?",
        "answer": ["promise", "a promise"],
        "hint": "It's something you make with words."
    },
    {
        "riddle": "I have branches, but no fruit, trunk, or leaves. What am I?",
        "answer": ["bank", "a bank"],
        "hint": "You might visit me to deposit money."
    },
    {
        "riddle": "What goes up but never comes down?",
        "answer": ["age", "your age"],
        "hint": "It increases every year on your birthday."
    },
    {
        "riddle": "I'm found in socks, scarves, and mittens; and often in the paws of playful kittens. What am I?",
        "answer": ["yarn", "thread", "string"],
        "hint": "I'm used for knitting and cats love to play with me."
    },
    {
        "riddle": "What has 88 keys but can't open a single door?",
        "answer": ["piano", "a piano"],
        "hint": "I make beautiful music when my keys are pressed."
    },
    {
        "riddle": "I can be cracked, made, told, and played. What am I?",
        "answer": ["joke", "a joke"],
        "hint": "I'm meant to make people laugh."
    },
    {
        "riddle": "What has teeth but cannot bite?",
        "answer": ["zipper", "a zipper", "comb", "a comb", "saw", "a saw", "gear", "a gear"],
        "hint": "I have many teeth but I'm not alive."
    },
    {
        "riddle": "I have a golden head and a golden tail, but no body. What am I?",
        "answer": ["coin", "a coin"],
        "hint": "I have heads and tails but I'm not an animal."
    },
    {
        "riddle": "What can travel around the world while staying in a corner?",
        "answer": ["stamp", "a stamp", "postage stamp"],
        "hint": "I help letters reach their destination."
    },
    {
        "riddle": "I get smaller every time I take a bath. What am I?",
        "answer": ["soap", "a bar of soap"],
        "hint": "You use me to get clean."
    },
    {
        "riddle": "What has a bottom at the top?",
        "answer": ["leg", "your leg", "legs", "your legs"],
        "hint": "Think about body parts and where they're positioned."
    },
    {
        "riddle": "I have no body, but I come alive with wind. What am I?",
        "answer": ["echo", "an echo", "sound"],
        "hint": "You might hear me in a canyon or empty room."
    }
]

GIF_COLLECTIONS = {
    "slap": [
        "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExcjR0bXRmY2thYmN1cmVyNjFoMmV3dTd4cXMzdGgzdnZldGQzZjYzbCZlcD12MV9naWZzX3NlYXJjaCZjdD1n/mEtSQlxqBtWWA/giphy.gif",
        "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExcjR0bXRmY2thYmN1cmVyNjFoMmV3dTd4cXMzdGgzdnZldGQzZjYzbCZlcD12MV9naWZzX3NlYXJjaCZjdD1n/Qumf2QovTD4QxHPjy5/giphy.gif",
        "https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3cDNvY2hwM2JoNTZycnFkNW9xN3ZleHluY3U1aDVpZ2p1empkY293YyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/RXGNsyRb1hDJm/giphy.gif",
        "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExYmF2Z2s4NnNqMHdrcnhwYWMyc3VtZGNic3V3b3RyMGM4b2ljcmlkNiZlcD12MV9naWZzX3NlYXJjaCZjdD1n/CnRmpfxlPutVAFChvm/giphy.gif",
        "https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3dmN3eDdyajgzeWNleTd4OGN4aHFyOTlsMmJldjN5a3JzYWJpc2pyMSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/tX9Myr2kUio7Q1JYSs/giphy.gif",
        "https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3NGljZTJkOG54MHB5bzExMGtzdmtxaGNmeTdkNnRndmF0dmJkbzEyaCZlcD12MV9naWZzX3NlYXJjaCZjdD1n/qNtqBSTTwXyuI/giphy.gif"
    ],
    "dog": [
        "https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExd2hwcHRqOG1sdzRyODBmdm5ra2d5d25pNHoyaGkxeng2cG1kdDNqeCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/FTJfA8RiHaOfS/giphy.gif",
        "https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExMTVhZnNtam9saWQ3MHZ6ZmJ5cGE4bWo4ZGdlNDVqdDdncmttNXQyYyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/nQ8XtX3ctBCkE/giphy.gif",
        "https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3b2xrMGZndTRqMjc5Yzc3bW5wa2Q0ZHQwNGp5OG9icnJ2b2NkMDY3ZSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/nLkYoleEY5iJW/giphy.gif",
        "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExa2RmZHBsc3hzYndyNGRodTdxNDJrc3VqMGl5bXpvb2d2anBnYzRhdiZlcD12MV9naWZzX3NlYXJjaCZjdD1n/jp2KXzsPtoKFG/giphy.gif",
        "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExa2RmZHBsc3hzYndyNGRodTdxNDJrc3VqMGl5bXpvb2d2anBnYzRhdiZlcD12MV9naWZzX3NlYXJjaCZjdD1n/6u38x5BzPipQ4/giphy.gif"
    ],
    "cat": [
        "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExOTJyOG1penN3NWpxbDYxdDhlb3FicjJlcWw0MGg5cjU5bzlvOTNqdSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/Zu6AATBpCeUzm/giphy.gif",
        "https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3Yzc4ODNnenBrMTllNXVtOTJ2ZnFwd25wZnY2dWczc3pxbGZ3YnNsdCZlcD12MV9naWZzX3NlYXJjaCZjdD1n/0T2MxTqlKE5Lftk9Ba/giphy.gif",
        "https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3cGh3Mm05dXF4NjFvczhhZXg3bXk0cjZvZ3Y3ZXdmMnZ0OTU5dGdlbSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/FG6EQNhs3s7ug/giphy.gif",
        "https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3bDEyc3cwbTkxejVyd2k4b3ZtMWhxZWZjajAyMHl6a3dybmhqMmY2cSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/slDJbFAKnNtEQ/giphy.gif",
        "https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3am01YWFiMHZmcXFvenFqdWllY21mYTM4bHBpN2w4YXM3ZHFuZHdvdyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/aiUaKRV3kwRs6NjBgr/giphy.gif",
        "https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExdnJpbGU1MTJ3dHFqYXQxdGgxemVjeHU0MzE4eTBianpsMnFibmhsNSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/xezrdgsvQ0zx7oPiGp/giphy.gif"





    ],
}

class DataManager:
    """Handles all data loading and saving operations."""
    
    @staticmethod
    def load_json_file(filename: str, default_data: Any) -> Any:
        """Load data from a JSON file with error handling."""
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.warning(f"Could not load {filename}: {e}. Using default data.")
            return default_data
    
    @staticmethod
    def save_json_file(filename: str, data: Any) -> bool:
        """Save data to a JSON file with error handling."""
        try:
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving {filename}: {e}")
            return False
    
    @staticmethod
    def load_counting_state() -> Dict[str, Any]:
        """Load counting state from file."""
        return DataManager.load_json_file(
            DATA_FILES["COUNTING_STATE"],
            {"channel_id": None, "current": 0, "last_user": None}
        )
    
    @staticmethod
    def load_contributions() -> Dict[str, int]:
        """Load contributions from file."""
        return DataManager.load_json_file(DATA_FILES["CONTRIBUTIONS"], {})
    
    @staticmethod
    def load_last_active() -> Dict[str, float]:
        """Load last active timestamps from file."""
        return DataManager.load_json_file(DATA_FILES["LAST_ACTIVE"], {})
    
    @staticmethod
    def load_riddle_state() -> Dict[str, Any]:
        """Load riddle state from file."""
        return DataManager.load_json_file(
            DATA_FILES["RIDDLE_STATE"],
            {
                "current_riddle_index": 0,
                "week_start": 0,
                "current_winner": None,
                "attempts": {},  # {user_id: attempt_count}
                "solved": False,
                "hints_given": 0
            }
        )
    
    @staticmethod
    def load_weekly_contributions() -> Dict[str, Any]:
        """Load weekly contributions from file."""
        return DataManager.load_json_file(
            DATA_FILES["WEEKLY_CONTRIBUTIONS"],
            {
                "week_start": 0,
                "contributions": {}  # {user_id: points}
            }
        )
    
    @staticmethod
    def load_lifetime_earnings() -> Dict[str, int]:
        """Load lifetime earnings from file."""
        return DataManager.load_json_file(DATA_FILES["LIFETIME_EARNINGS"], {})

class RiddleManager:
    """Manages the daily riddle system."""
    
    @staticmethod
    def get_day_start_timestamp() -> int:
        """Get the timestamp for the start of the current day (00:00 UTC)."""
        import datetime
        now = datetime.datetime.utcnow()
        day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        return int(day_start.timestamp())
    
    @staticmethod
    def is_new_day(last_day_start: int) -> bool:
        """Check if it's a new day since the last riddle."""
        current_day_start = RiddleManager.get_day_start_timestamp()
        return current_day_start > last_day_start
    
    @staticmethod
    def get_current_riddle(riddle_state: Dict[str, Any]) -> Dict[str, Any]:
        """Get the current day's riddle, updating if it's a new day."""
        current_day_start = RiddleManager.get_day_start_timestamp()
        
        # Check if we need a new riddle for the day
        if RiddleManager.is_new_day(riddle_state.get("day_start", 0)):
            # Reset for new day
            riddle_state["day_start"] = current_day_start
            riddle_state["current_riddle_index"] = (riddle_state.get("current_riddle_index", 0) + 1) % len(WEEKLY_RIDDLES)
            riddle_state["current_winner"] = None
            riddle_state["previous_winner"] = riddle_state.get("current_winner")  # Store previous winner for VIP role removal
            riddle_state["attempts"] = {}
            riddle_state["solved"] = False
            riddle_state["hints_given"] = 0
            
            # Save the updated state
            DataManager.save_json_file(DATA_FILES["RIDDLE_STATE"], riddle_state)
        
        return WEEKLY_RIDDLES[riddle_state["current_riddle_index"]]
    
    @staticmethod
    def check_answer(user_answer: str, correct_answers: List[str]) -> bool:
        """Check if the user's answer matches any of the correct answers."""
        user_answer = user_answer.lower().strip()
        return any(user_answer == answer.lower().strip() for answer in correct_answers)
    
    @staticmethod
    def can_attempt(user_id: int, riddle_state: Dict[str, Any]) -> tuple[bool, int]:
        """Check if user can attempt the riddle and return remaining attempts."""
        max_attempts = 3
        user_attempts = riddle_state["attempts"].get(str(user_id), 0)
        return user_attempts < max_attempts, max_attempts - user_attempts
    
    @staticmethod
    def record_attempt(user_id: int, riddle_state: Dict[str, Any]) -> None:
        """Record a riddle attempt for the user."""
        riddle_state["attempts"][str(user_id)] = riddle_state["attempts"].get(str(user_id), 0) + 1
        DataManager.save_json_file(DATA_FILES["RIDDLE_STATE"], riddle_state)
    
    @staticmethod
    def get_time_until_next_riddle() -> str:
        """Get formatted time until next day (midnight UTC)."""
        import datetime
        now = datetime.datetime.utcnow()
        next_day = now.replace(hour=0, minute=0, second=0, microsecond=0) + datetime.timedelta(days=1)
        time_diff = next_day - now
        
        hours, remainder = divmod(time_diff.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        
        return f"{hours}h {minutes}m"

class LevelSystem:
    """Handles level calculations and management based on lifetime earnings."""
    
    @staticmethod
    def get_level(lifetime_points: int) -> int:
        """Calculate level based on lifetime points earned with input validation."""
        try:
            if not isinstance(lifetime_points, (int, float)) or lifetime_points < 0:
                logger.warning(f"Invalid lifetime points value: {lifetime_points}")
                return 0
            # Exponential level curve: Level = int((lifetime_points / 100) ** 0.5)
            return int((lifetime_points / 100) ** 0.5)
        except Exception as e:
            logger.error(f"Error calculating level for lifetime points {lifetime_points}: {e}")
            return 0
    
    @staticmethod
    def get_points_for_level(level: int) -> int:
        """Calculate lifetime points needed for a specific level."""
        return (level ** 2) * 100
    
    @staticmethod
    def calculate_level_up_points(current_lifetime_points: int, levels_to_add: int) -> int:
        """Calculate how many lifetime points to add for leveling up."""
        current_level = LevelSystem.get_level(current_lifetime_points)
        target_level = current_level + levels_to_add
        target_points = LevelSystem.get_points_for_level(target_level)
        return target_points - current_lifetime_points

class GameHelpers:
    """Helper functions for games."""
    
    @staticmethod
    def get_random_pun() -> str:
        """Get a random pun from the collection."""
        return random.choice(PUN_LIST)
    
    @staticmethod
    def get_8ball_response() -> str:
        """Get a random 8-ball response."""
        return random.choice(EIGHTBALL_RESPONSES)
    
    @staticmethod
    def get_random_gif(category: str) -> str:
        """Get a random gif from the specified category."""
        if category in GIF_COLLECTIONS:
            return random.choice(GIF_COLLECTIONS[category])
        return ""

class PermissionHelper:
    """Helper functions for permission checks."""
    
    @staticmethod
    def is_bot_owner(user_id: int) -> bool:
        """Check if user is the bot owner."""
        return user_id == BOT_CONFIG["BOT_OWNER_ID"]
    
    @staticmethod
    def is_main_server(guild_id: int) -> bool:
        """Check if guild is a main server."""
        return guild_id in BOT_CONFIG["MAIN_SERVER_IDS"]
    
    @staticmethod
    def is_forbidden_channel(channel_id: int) -> bool:
        """Check if channel is in the forbidden list."""
        return channel_id in BOT_CONFIG["FORBIDDEN_CHANNEL_IDS"]
    
    @staticmethod
    def is_vip_member(member: discord.Member) -> bool:
        """Check if member has the VIP role."""
        vip_role_name = BOT_CONFIG["VIP_ROLE_NAME"]
        return any(role.name == vip_role_name for role in member.roles)
    
    @staticmethod
    def get_vip_role(guild: discord.Guild) -> Optional[discord.Role]:
        """Get the VIP role from the guild."""
        vip_role_name = BOT_CONFIG["VIP_ROLE_NAME"]
        return discord.utils.get(guild.roles, name=vip_role_name)

class EmbedHelper:
    """Helper functions for creating Discord embeds."""
    
    @staticmethod
    def create_success_embed(title: str, description: str) -> discord.Embed:
        """Create a success embed with green color."""
        return discord.Embed(
            title=title,
            description=description,
            color=discord.Color.green()
        )
    
    @staticmethod
    def create_error_embed(title: str, description: str) -> discord.Embed:
        """Create an error embed with red color."""
        return discord.Embed(
            title=title,
            description=description,
            color=discord.Color.red()
        )
    
    @staticmethod
    def create_info_embed(title: str, description: str) -> discord.Embed:
        """Create an info embed with blue color."""
        return discord.Embed(
            title=title,
            description=description,
            color=discord.Color.blue()
        )
    
    @staticmethod
    def create_warning_embed(title: str, description: str) -> discord.Embed:
        """Create a warning embed with orange color."""
        return discord.Embed(
            title=title,
            description=description,
            color=discord.Color.orange()
        )

class ChannelHelper:
    """Helper functions for channel management."""
    
    @staticmethod
    async def find_suitable_channel(
        guild: discord.Guild, 
        member: discord.Member, 
        preferred_channel: Optional[discord.TextChannel] = None
    ) -> Optional[discord.TextChannel]:
        """Find a suitable channel to send messages with error handling."""
        try:
            # Use preferred channel if valid
            if (preferred_channel and 
                hasattr(preferred_channel, "send") and 
                preferred_channel.permissions_for(guild.me).send_messages):
                return preferred_channel
            
            # Try to find the most recent channel the user spoke in
            try:
                for text_channel in guild.text_channels:
                    if (not text_channel.permissions_for(guild.me).read_message_history or
                        PermissionHelper.is_forbidden_channel(text_channel.id)):
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
                    not PermissionHelper.is_forbidden_channel(channel.id)):
                    return channel
            
            # Last resort: system or rules channel (but not the forbidden channels)
            for channel in [guild.system_channel, guild.rules_channel]:
                if (channel and 
                    channel.permissions_for(guild.me).send_messages and
                    not PermissionHelper.is_forbidden_channel(channel.id)):
                    return channel
                    
            return None
            
        except Exception as e:
            logger.error(f"Error finding suitable channel: {e}")
            return None

def format_time_remaining(seconds: int) -> str:
    """Format remaining time in hours and minutes."""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    return f"{hours}h {minutes}m"

class WeeklyContributionManager:
    """Manages weekly contribution tracking for leaderboards."""
    
    @staticmethod
    def get_week_start_timestamp() -> int:
        """Get the timestamp for the start of the current week (Monday 00:00 UTC)."""
        import datetime
        now = datetime.datetime.utcnow()
        days_since_monday = now.weekday()  # Monday is 0
        week_start = now.replace(hour=0, minute=0, second=0, microsecond=0) - datetime.timedelta(days=days_since_monday)
        return int(week_start.timestamp())
    
    @staticmethod
    def is_new_week(last_week_start) -> bool:
        """Check if it's a new week since the last tracking."""
        current_week_start = WeeklyContributionManager.get_week_start_timestamp()
        
        # Handle different types for last_week_start
        if isinstance(last_week_start, str):
            try:
                # Try to convert string timestamp to int
                last_week_start = int(float(last_week_start))
            except (ValueError, TypeError):
                # If it's a date string like "2025-08-26", convert to timestamp
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(last_week_start.replace('Z', '+00:00'))
                    last_week_start = int(dt.timestamp())
                except:
                    # If all else fails, assume it's a new week
                    return True
        elif last_week_start is None:
            return True
        
        return current_week_start > last_week_start
    
    @staticmethod
    def get_weekly_data() -> Dict[str, Any]:
        """Get current weekly contribution data, resetting if it's a new week."""
        try:
            weekly_data = DataManager.load_weekly_contributions()
            current_week_start = WeeklyContributionManager.get_week_start_timestamp()
            
            # Ensure the data structure is correct
            if not isinstance(weekly_data, dict):
                weekly_data = {"week_start": 0, "contributions": {}}
            if "contributions" not in weekly_data:
                weekly_data["contributions"] = {}
            
            # Check if we need to reset for a new week
            if WeeklyContributionManager.is_new_week(weekly_data.get("week_start", 0)):
                # Save the top 10 contributors from the previous week before resetting
                if weekly_data.get("contributions"):
                    WeeklyContributionManager.save_top_contributors(weekly_data["contributions"])
                
                # Reset for new week
                weekly_data = {
                    "week_start": current_week_start,
                    "contributions": {}
                }
                # Save the reset data
                DataManager.save_json_file(DATA_FILES["WEEKLY_CONTRIBUTIONS"], weekly_data)
            
            return weekly_data
            
        except Exception as e:
            logger.error(f"Error in get_weekly_data: {e}")
            # Return safe default data
            current_week_start = WeeklyContributionManager.get_week_start_timestamp()
            return {
                "week_start": current_week_start,
                "contributions": {}
            }
    
    @staticmethod
    def add_weekly_points(user_id: str, points: int) -> None:
        """Add points to user's weekly contribution total."""
        weekly_data = WeeklyContributionManager.get_weekly_data()
        weekly_data["contributions"][user_id] = weekly_data["contributions"].get(user_id, 0) + points
        DataManager.save_json_file(DATA_FILES["WEEKLY_CONTRIBUTIONS"], weekly_data)
    
    @staticmethod
    def get_weekly_leaderboard(limit: int = 10) -> List[tuple]:
        """Get weekly leaderboard data."""
        weekly_data = WeeklyContributionManager.get_weekly_data()
        contributions = weekly_data.get("contributions", {})
        return sorted(contributions.items(), key=lambda x: x[1], reverse=True)[:limit]
    
    @staticmethod
    def get_time_until_next_week() -> str:
        """Get formatted time until next Monday."""
        import datetime
        now = datetime.datetime.utcnow()
        days_until_monday = (7 - now.weekday()) % 7
        if days_until_monday == 0:  # If it's Monday
            days_until_monday = 7
        
        next_monday = now.replace(hour=0, minute=0, second=0, microsecond=0) + datetime.timedelta(days=days_until_monday)
        time_diff = next_monday - now
        
        days = time_diff.days
        hours, remainder = divmod(time_diff.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        
        if days > 0:
            return f"{days}d {hours}h {minutes}m"
        else:
            return f"{hours}h {minutes}m"
    
    @staticmethod
    def save_top_contributors(contributions: Dict[str, int]) -> None:
        """Save the top 10 contributors to a text file for weekly awards."""
        import datetime
        
        # Get top 10 contributors
        top_contributors = sorted(contributions.items(), key=lambda x: x[1], reverse=True)[:10]
        
        if not top_contributors:
            return  # No contributors to save
        
        # Create the content for the file
        content_lines = []
        content_lines.append("WEEKLY TOP CONTRIBUTORS")
        content_lines.append("=" * 50)
        content_lines.append(f"Week ending: {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
        content_lines.append(f"Total contributors this week: {len(contributions)}")
        content_lines.append("")
        content_lines.append("TOP 10 CONTRIBUTORS:")
        content_lines.append("-" * 30)
        
        for rank, (user_id, points) in enumerate(top_contributors, 1):
            content_lines.append(f"{rank:2d}. User ID: {user_id} - {points:,} points")
        
        content_lines.append("")
        content_lines.append("Award Status: PENDING")
        content_lines.append("Awards: 2,000 contribution points each")
        
        # Save to file
        content = "\n".join(content_lines)
        try:
            with open(DATA_FILES["WEEKLY_TOP_CONTRIBUTORS"], 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"Saved top {len(top_contributors)} contributors to weekly awards file")
        except Exception as e:
            logger.error(f"Error saving weekly top contributors: {e}")
    
    @staticmethod
    def load_top_contributors_file() -> Optional[List[str]]:
        """Load the weekly top contributors file and return user IDs if it exists."""
        try:
            if not os.path.exists(DATA_FILES["WEEKLY_TOP_CONTRIBUTORS"]):
                logger.warning("Weekly top contributors file does not exist")
                return None
                
            with open(DATA_FILES["WEEKLY_TOP_CONTRIBUTORS"], 'r', encoding='utf-8') as f:
                content = f.read()
            
            if not content.strip():
                logger.warning("Weekly top contributors file is empty")
                return None
            
            # Extract user IDs from the file
            user_ids = []
            lines = content.split('\n')
            
            logger.debug(f"Processing {len(lines)} lines from contributors file")
            
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                if not line:
                    continue
                    
                # Look for lines like "1. User ID: 123456789 - 1,500 points"
                if "User ID:" in line and " - " in line and "points" in line:
                    try:
                        # Split by "User ID:" first
                        parts = line.split("User ID:")
                        if len(parts) < 2:
                            continue
                            
                        # Get the part after "User ID:" and before " - "
                        user_id_section = parts[1].strip()
                        if " - " in user_id_section:
                            user_id_part = user_id_section.split(" - ")[0].strip()
                            
                            # Validate it's a proper Discord user ID (numeric, 17-19 digits)
                            if user_id_part.isdigit() and 17 <= len(user_id_part) <= 19:
                                user_ids.append(user_id_part)
                                logger.debug(f"Found valid user ID: {user_id_part}")
                            else:
                                logger.warning(f"Invalid user ID format on line {line_num}: '{user_id_part}'")
                    except Exception as e:
                        logger.error(f"Error parsing line {line_num} '{line}': {e}")
                        continue
            
            if user_ids:
                logger.info(f"Successfully loaded {len(user_ids)} user IDs from contributors file")
                return user_ids
            else:
                logger.warning("No valid user IDs found in contributors file")
                return None
            
        except FileNotFoundError:
            logger.warning("Weekly top contributors file not found")
            return None
        except PermissionError:
            logger.error("Permission denied accessing weekly top contributors file")
            return None
        except Exception as e:
            logger.error(f"Error loading weekly top contributors file: {e}")
            return None
    
    @staticmethod
    def mark_awards_given() -> bool:
        """Mark the weekly awards as given in the file."""
        try:
            if not os.path.exists(DATA_FILES["WEEKLY_TOP_CONTRIBUTORS"]):
                logger.error("Cannot mark awards as given - file does not exist")
                return False
                
            with open(DATA_FILES["WEEKLY_TOP_CONTRIBUTORS"], 'r', encoding='utf-8') as f:
                content = f.read()
            
            if not content.strip():
                logger.error("Cannot mark awards as given - file is empty")
                return False
            
            # Replace PENDING with COMPLETED
            if "Award Status: PENDING" not in content:
                logger.warning("Awards already marked as completed or status not found")
                return True  # Consider this successful since awards are not pending
            
            updated_content = content.replace("Award Status: PENDING", "Award Status: COMPLETED")
            
            with open(DATA_FILES["WEEKLY_TOP_CONTRIBUTORS"], 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            logger.info("Successfully marked weekly awards as completed")
            return True
            
        except PermissionError:
            logger.error("Permission denied when trying to mark awards as given")
            return False
        except Exception as e:
            logger.error(f"Error marking weekly awards as given: {e}")
            return False
    
    @staticmethod
    def check_awards_pending() -> bool:
        """Check if there are pending awards to be given."""
        try:
            if not os.path.exists(DATA_FILES["WEEKLY_TOP_CONTRIBUTORS"]):
                logger.info("Weekly top contributors file does not exist - no pending awards")
                return False
                
            with open(DATA_FILES["WEEKLY_TOP_CONTRIBUTORS"], 'r', encoding='utf-8') as f:
                content = f.read()
                
            if not content.strip():
                logger.warning("Weekly top contributors file is empty")
                return False
                
            has_pending = "Award Status: PENDING" in content
            logger.info(f"Award status check: {'PENDING' if has_pending else 'COMPLETED or not found'}")
            return has_pending
            
        except FileNotFoundError:
            logger.info("Weekly top contributors file not found - no pending awards")
            return False
        except PermissionError:
            logger.error("Permission denied accessing weekly top contributors file")
            return False
        except Exception as e:
            logger.error(f"Error checking award status: {e}")
            return False
    
    @staticmethod
    def debug_contributors_file() -> str:
        """Debug function to show the contents of the contributors file."""
        try:
            if not os.path.exists(DATA_FILES["WEEKLY_TOP_CONTRIBUTORS"]):
                return "❌ Weekly top contributors file does not exist"
            
            with open(DATA_FILES["WEEKLY_TOP_CONTRIBUTORS"], 'r', encoding='utf-8') as f:
                content = f.read()
            
            if not content.strip():
                return "⚠️ Weekly top contributors file exists but is empty"
            
            lines = content.split('\n')
            user_id_lines = [line for line in lines if "User ID:" in line]
            
            debug_info = f"📁 **File Debug Information:**\n"
            debug_info += f"• File exists: ✅\n"
            debug_info += f"• File size: {len(content)} characters\n"
            debug_info += f"• Total lines: {len(lines)}\n"
            debug_info += f"• User ID lines found: {len(user_id_lines)}\n"
            debug_info += f"• Award status: {'PENDING' if 'Award Status: PENDING' in content else 'COMPLETED or NOT FOUND'}\n"
            
            if user_id_lines:
                debug_info += f"\n📋 **User ID Lines:**\n"
                for i, line in enumerate(user_id_lines[:5], 1):  # Show first 5 lines
                    debug_info += f"• `{line.strip()}`\n"
                if len(user_id_lines) > 5:
                    debug_info += f"• ... and {len(user_id_lines) - 5} more lines\n"
            
            return debug_info
            
        except Exception as e:
            return f"❌ Error reading file: {str(e)}"

class ShopHelper:
    """Helper class for interactive shop system with tiered selection."""
    
    @staticmethod
    def get_shop_tiers() -> Dict[str, List[tuple]]:
        """Organize shop roles by rarity tiers."""
        tiers = {
            "Legendary": [],
            "Epic": [],
            "Rare": [],
            "Common": [],
            "Starter": [],
            "Special Achievement": []
        }
        
        for role_name, details in SHOP_ROLES.items():
            rarity = details["rarity"]
            if rarity in tiers:
                tiers[rarity].append((role_name, details))
        
        # Sort each tier by price (ascending)
        for tier in tiers:
            tiers[tier].sort(key=lambda x: x[1]["price"])
        
        return tiers
    
    @staticmethod
    def create_tier_selection_embed(user_points: int) -> discord.Embed:
        """Create the main tier selection embed."""
        embed = discord.Embed(
            title="🏪✨ StarChan Title Shop ✨🏪",
            description=f"**Welcome to the exclusive title collection!**\n\n"
                       f"💰 **Your Balance:** {user_points:,} points\n\n"
                       f"📋 **Select a tier to browse:**",
            color=discord.Color.gold()
        )
        
        tiers = ShopHelper.get_shop_tiers()
        tier_info = [
            ("🌟 **1️⃣ Legendary Tier**", f"10,000+ points • {len(tiers['Legendary'])} exclusive titles"),
            ("⚡ **2️⃣ Epic Tier**", f"6,000-9,999 points • {len(tiers['Epic'])} powerful titles"),
            ("💎 **3️⃣ Rare Tier**", f"3,000-5,999 points • {len(tiers['Rare'])} unique titles"),
            ("🎮 **4️⃣ Common Tier**", f"1,000-2,999 points • {len(tiers['Common'])} popular titles"),
            ("🌱 **5️⃣ Starter Tier**", f"200-999 points • {len(tiers['Starter'])} beginner titles"),
            ("🏆 **6️⃣ Special Achievements**", f"Unlock through gameplay • {len(tiers['Special Achievement'])} exclusive rewards")
        ]
        
        for title, desc in tier_info:
            embed.add_field(name=title, value=desc, inline=False)
        
        embed.add_field(
            name="📝 **How to Navigate:**",
            value="React with the number (1️⃣-6️⃣) to browse that tier!\n"
                  "Use 🔙 to go back to tier selection anytime.",
            inline=False
        )
        
        embed.set_footer(text="✨ Choose your tier to explore exclusive titles! ✨")
        return embed
    
    @staticmethod
    def create_tier_browse_embed(tier_name: str, user_points: int, user_roles: List[str]) -> discord.Embed:
        """Create tier browsing embed with role selection."""
        tiers = ShopHelper.get_shop_tiers()
        roles_in_tier = tiers.get(tier_name, [])
        
        tier_emojis = {
            "Legendary": "🌟",
            "Epic": "⚡",
            "Rare": "💎",
            "Common": "🎮",
            "Starter": "🌱",
            "Special Achievement": "🏆"
        }
        
        tier_emoji = tier_emojis.get(tier_name, "✨")
        
        embed = discord.Embed(
            title=f"{tier_emoji} {tier_name} Tier Selection",
            description=f"**Choose from {len(roles_in_tier)} exclusive {tier_name.lower()} titles:**\n\n"
                       f"💰 **Your Balance:** {user_points:,} points",
            color=discord.Color.gold()
        )
        
        if not roles_in_tier:
            embed.add_field(
                name="❌ No Roles Available",
                value="This tier currently has no available roles.",
                inline=False
            )
            return embed
        
        # Display roles with numbers for selection
        role_text = ""
        for i, (role_name, details) in enumerate(roles_in_tier[:10], 1):  # Limit to 10 per page
            # Check affordability and ownership
            affordable = user_points >= details["price"]
            owned = role_name in user_roles
            
            if tier_name == "Special Achievement":
                status = "🏆 **Earned!**" if owned else "🎯 **Not Earned**"
                price_text = "Achievement Required"
            else:
                if owned:
                    status = "✅ **Owned**"
                elif affordable:
                    status = "💚 **Affordable**"
                else:
                    status = "❌ **Too Expensive**"
                price_text = f"{details['price']:,} points"
            
            role_text += f"**{i}️⃣ {role_name}**\n"
            role_text += f"└ *{details['description']}*\n"
            role_text += f"└ 💰 {price_text} | {status}\n\n"
        
        embed.add_field(
            name=f"📋 Available {tier_name} Titles:",
            value=role_text.strip(),
            inline=False
        )
        
        if tier_name != "Special Achievement":
            embed.add_field(
                name="🛒 **How to Purchase:**",
                value="React with the number (1️⃣-🔟) of the title you want!\n"
                      "Then use the command shown to complete your purchase.",
                inline=False
            )
        
        embed.add_field(
            name="🗂️ **Navigation:**",
            value="🔙 **Back** - Return to tier selection\n"
                  "❌ **Cancel** - Close shop",
            inline=False
        )
        
        embed.set_footer(text=f"✨ {tier_name} Tier • Select a number to view purchase info!")
        return embed
    
    @staticmethod 
    def create_role_purchase_embed(role_name: str, details: Dict, user_points: int, user_roles: List[str]) -> discord.Embed:
        """Create final purchase confirmation embed."""
        owned = role_name in user_roles
        affordable = user_points >= details["price"]
        
        if details["rarity"] == "Special Achievement":
            embed = discord.Embed(
                title=f"🏆 Special Achievement Role",
                description=f"**{role_name}**\n*{details['description']}*",
                color=discord.Color.purple()
            )
            
            embed.add_field(
                name="🎯 How to Earn:",
                value="This role cannot be purchased with points.\n"
                      "Complete the required achievement to unlock it!",
                inline=False
            )
            
            if owned:
                embed.add_field(
                    name="✅ Status:",
                    value="🏆 **You have earned this role!**",
                    inline=False
                )
            else:
                embed.add_field(
                    name="❌ Status:",
                    value="🎯 **Achievement not completed yet**",
                    inline=False
                )
        else:
            color = discord.Color.green() if affordable else discord.Color.red()
            embed = discord.Embed(
                title=f"{details['emoji']} Purchase Confirmation",
                description=f"**{role_name}**\n*{details['description']}*",
                color=color
            )
            
            embed.add_field(
                name="💰 Price:",
                value=f"{details['price']:,} points",
                inline=True
            )
            
            embed.add_field(
                name="💎 Your Balance:",
                value=f"{user_points:,} points",
                inline=True
            )
            
            embed.add_field(
                name="🏷️ Rarity:",
                value=f"{details['rarity']} {details['emoji']}",
                inline=True
            )
            
            if owned:
                embed.add_field(
                    name="❌ Already Owned:",
                    value="You already have this role!",
                    inline=False
                )
            elif affordable:
                # Get the buyable role key for the command
                buy_command = None
                for key, full_name in BUYABLE_ROLES.items():
                    if full_name == role_name:
                        buy_command = f"!buy {key}"
                        break
                
                embed.add_field(
                    name="✅ Ready to Purchase:",
                    value=f"**Command:** `{buy_command}`\n"
                          f"**Remaining after purchase:** {user_points - details['price']:,} points",
                    inline=False
                )
            else:
                needed = details['price'] - user_points
                embed.add_field(
                    name="❌ Insufficient Points:",
                    value=f"You need **{needed:,} more points** to purchase this role.\n"
                          f"Keep being active to earn more points!",
                    inline=False
                )
        
        embed.set_footer(text="🔙 Back to browse • ❌ Cancel • Copy the command above to purchase!")
        return embed
    
    @staticmethod
    def get_reaction_emojis() -> Dict[str, str]:
        """Get the standard reaction emojis for shop navigation."""
        return {
            "tier_1": "1️⃣", "tier_2": "2️⃣", "tier_3": "3️⃣", 
            "tier_4": "4️⃣", "tier_5": "5️⃣", "tier_6": "6️⃣",
            "select_1": "1️⃣", "select_2": "2️⃣", "select_3": "3️⃣",
            "select_4": "4️⃣", "select_5": "5️⃣", "select_6": "6️⃣",
            "select_7": "7️⃣", "select_8": "8️⃣", "select_9": "9️⃣", "select_10": "🔟",
            "back": "🔙", "cancel": "❌"
        }

def clean_member_list(data: Dict[str, Any], guild_members: List[discord.Member]) -> Dict[str, Any]:
    """Remove data for members who are no longer in the guild."""
    valid_ids = {str(member.id) for member in guild_members}
    cleaned_data = {uid: value for uid, value in data.items() if uid in valid_ids}
    return cleaned_data

def get_help_text(is_owner: bool = False) -> str:
    """Generate help text based on user permissions."""
    help_text = (
        "✨ **StarChan Complete Help Guide** ✨\n"
        "\n"
        "🎪 **Fun & Entertainment:**\n"
        "😺 `!cat` 🐶 `!doggo` 🤪 `!pun` 🪓 `!bonk [@user]`\n"
        "👋 `!slap @user`\n"
        "🎱 `!8ball <question>` 🎮 `!tictactoe @user`\n"
        "🔢`!guessnumber` 🧩 `!riddlemethis` - Weekly riddle challenge!\n"
        "\n"
        "🎯 **Leveling & Competition:**\n"
        "🔢 `!counting` ⏩ `!skipcount <n>`\n"
        "🏆 `!leaderboard` 🏆 `!leaderboardmax` 🥇 `!balance`\n"
        "� *Leaderboards show weekly activity (resets Mondays)*\n"
        "�🛒 `!shop` 💰 `!buy <role>` 💰 `!sell <role>`\n"
        "🎰 `!blackjack <bet>`\n"
        "🏅 `!achievements [@user]` 🎯 `!achievementprogress [name]`\n"
        "\n"
        "📊 **Stats & Info:**\n"
        "🧑‍💻 `!userinfo [@user]` 🆔 `!whatismyid [@user]`\n"
        "🕐 `!pingservertime` - Check server time\n"
        "\n"
        "🛠️ **Moderation & Admin:**\n"
        "🧹 `!purge [amount]` 📝 `!modpost <channel_id> <msg>`\n"
        "👢 `!kick @user [reason]`\n"
        "👀 `!showlurkers` \n"
        "\n"
        "ℹ️ **System & Info:**\n"
        "🆕 🏅 `!credits` 📜 `!license`\n"
        "💡 **Tip:** Commands with [@user] are optional, [amount] means optional number\n"
    )
    
    # Add dev commands for bot owner only
    if is_owner:
        help_text += (
            "\n"
            "🔧 **DEV Commands (Owner Only):**\n"
            "⬆️ `!devlevelup @user <levels>` - Level up a user\n"
            "⬇️ `!devleveldown @user <levels>` - Level down a user\n"
            "🎯 `!devsetlevel @user <level>` - Set user's exact level\n"
        )
    
    return help_text

async def send_achievement_notification(bot, user, achievement):
    """Send achievement notification to the designated achievement channel and user DM with fail-safes."""
    logger.info(f"🎯 STARTING achievement notification for {user.display_name} ({user.id}) - {achievement.name}")
    
    success = False
    
    try:
        # Get the achievement channel from config
        achievement_channel_id = BOT_CONFIG.get("ACHIEVEMENT_CHANNEL_ID")
        if not achievement_channel_id or achievement_channel_id == 000000000000000000:
            logger.warning("❌ Achievement channel ID not configured! Please set ACHIEVEMENT_CHANNEL_ID in BOT_CONFIG.")
            return False
            
        achievement_channel = bot.get_channel(achievement_channel_id)
        
        if not achievement_channel:
            logger.error(f"❌ Achievement channel {achievement_channel_id} not found! Bot may not have access.")
            # Try to list available channels for debugging
            if hasattr(bot, 'guilds') and bot.guilds:
                for guild in bot.guilds:
                    logger.info(f"Available channels in {guild.name}: {[f'{ch.name}({ch.id})' for ch in guild.text_channels[:5]]}")
        else:
            # Create achievement embed
            embed = EmbedHelper.create_success_embed(
                f"🏆 Achievement Unlocked! {achievement.emoji}",
                f"**{achievement.name}**\n{achievement.description}\n\n🎁 **Reward:** {achievement.reward_points * 10:,} contribution points (10x bonus!)!"
            )
            
            embed.set_author(name=user.display_name, icon_url=user.display_avatar.url if user.display_avatar else None)
            embed.set_footer(text=f"User ID: {user.id} | Achievement ID: {achievement.id}")
            
            # Send to achievement channel for ALL users - NO CONDITIONS
            await achievement_channel.send(f"🎉 {user.mention} unlocked an achievement!", embed=embed)
            logger.info(f"✅ Achievement notification sent to channel #{achievement_channel.name} ({achievement_channel_id}) for {user.display_name} - {achievement.name}")
            success = True
        
        # Also try to send to user via DM (but don't fail if this doesn't work)
        try:
            # Use same embed for DM
            embed_dm = EmbedHelper.create_success_embed(
                f"🏆 Achievement Unlocked! {achievement.emoji}",
                f"**{achievement.name}**\n{achievement.description}\n\n🎁 **Reward:** {achievement.reward_points * 10:,} contribution points (10x bonus!)!"
            )
            embed_dm.set_footer(text=f"Achievement ID: {achievement.id}")
            
            await user.send(embed=embed_dm)
            logger.info(f"✅ Achievement DM sent to {user.display_name}")
        except Exception as dm_error:
            logger.warning(f"⚠️ Could not send achievement DM to {user.display_name}: {dm_error}")
        
        return success
        
    except Exception as e:
        logger.error(f"❌ CRITICAL ERROR in achievement notification for {user.display_name} - {achievement.name}: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return False


# =============================================================================
# HUMOR COMMANDS - ROAST AND PRAISE
# =============================================================================

async def roast_command(ctx, bot, member: discord.Member = None):
    """Playfully roast someone! Usage: !roast @user or !roast for self-roast"""
    
    funny_roasts = [
        "I'd agree with you, but then we'd both be wrong.",
        "You're not stupid; you just have bad luck thinking.",
        "I'm not insulting you, I'm describing you.",
        "You bring everyone a lot of joy... when you leave the room.",
        "I'd explain it to you, but I don't have any crayons with me.",
        "You're like Monday mornings - nobody really likes you.",
        "If you were any more inbred, you'd be a sandwich.",
        "You're about as useful as a screen door on a submarine.",
        "I'm not saying you're dumb, but you make me look like Einstein.",
        "You're the human equivalent of a participation trophy.",
        "If brains were dynamite, you wouldn't have enough to blow your nose.",
        "You're like a broken clock - occasionally right, but mostly just annoying.",
        "I'd call you a tool, but that would imply you're actually useful.",
        "You're proof that evolution can go in reverse.",
        "You have the perfect face for radio.",
        "If ignorance is bliss, you must be the happiest person alive.",
        "You're like a software update - whenever I see you, I think 'not now'.",
        "I'd roast you harder, but my mom said I shouldn't burn trash.",
        "You're the reason aliens won't visit us.",
        "If you were any slower, you'd be going backwards.",
        "You're like a participation award in human form.",
        "I'd call you average, but that would be an insult to average people.",
        "You're the kind of person who would get lost in their own backyard.",
        "If stupidity was a superpower, you'd be invincible.",
        "You're like a dictionary - you give meaning to my life by showing me what I don't want to be.",
        "I'm not saying you're short, but you'd drown in a puddle.",
        "You're like a broken pencil - pointless.",
        "If you were any more basic, you'd be pH 14.",
        "You're the human equivalent of Comic Sans font.",
        "I'd make fun of your outfit, but I don't want to make fun of the homeless."
    ]
    
    if member and member != ctx.author:
        # Roasting someone else
        roast = random.choice(funny_roasts)
        target_name = member.display_name
        await ctx.send(f"🔥 **ROASTED!** 🔥\n\n{target_name}, {roast}")
    else:
        # Self-roast or no target specified
        self_roasts = [
            "You asked me to roast you, but life already did that for me.",
            "I'd roast you, but I don't want to repeat what the mirror tells you every morning.",
            "You're brave for asking to be roasted - too bad bravery doesn't fix everything else.",
            "I'd make fun of you, but I believe in recycling, not roasting trash.",
            "You're like a self-checkout machine - always need help and nobody really wants to use you.",
            "Asking for a self-roast? That's the most self-aware thing you'll do all day.",
            "I respect the confidence to ask for a roast when reality already provides a daily serving.",
            "You're like a Discord bot - trying your best but nobody really appreciates you.",
        ]
        roast = random.choice(self_roasts)
        await ctx.send(f"🔥 **SELF-ROAST ACTIVATED!** 🔥\n\n{ctx.author.mention}, {roast}")


async def praise_command(ctx, bot, member: discord.Member = None):
    """Give someone a nice compliment! Usage: !praise @user or !praise for self-love"""
    
    compliments = [
        "You're absolutely wonderful and bring joy to everyone around you! ✨",
        "Your positive energy is contagious! Keep being amazing! 🌟",
        "You have a great sense of humor and make everyone smile! 😄",
        "You're incredibly thoughtful and caring towards others! 💝",
        "Your creativity and imagination are truly inspiring! 🎨",
        "You have amazing problem-solving skills! 🧠",
        "You're a fantastic friend and always there when people need you! 🤗",
        "Your kindness makes the world a better place! 🌍",
        "You have excellent taste in... well, everything! 👌",
        "You're stronger than you realize and can overcome anything! 💪",
        "Your smile can light up any room! 😊",
        "You're incredibly talented and should be proud of your achievements! 🏆",
        "You have a beautiful soul and a generous heart! 💖",
        "You're wise beyond your years! 🦉",
        "Your determination and perseverance are admirable! 🔥",
        "You bring out the best in everyone you meet! ✨",
        "You're an absolute legend and don't let anyone tell you otherwise! 👑",
        "Your laugh is music to everyone's ears! 🎵",
        "You have impeccable timing and always know what to say! ⏰",
        "You're proof that awesome people exist! 🌈",
        "Your presence makes any gathering more fun! 🎉",
        "You have a heart of gold! 💛",
        "You're incredibly resilient and handle challenges with grace! 🌸",
        "Your intelligence and wit are impressive! 🎓",
        "You make the world brighter just by being in it! ☀️",
        "You're a rare gem in this world! 💎",
        "Your passion for life is inspiring! 🔥",
        "You have the most wonderful personality! ⭐",
        "You're incredibly genuine and authentic! 🦋",
        "You deserve all the good things life has to offer! 🌺"
    ]
    
    if member and member != ctx.author:
        # Complimenting someone else
        compliment = random.choice(compliments)
        target_name = member.display_name
        await ctx.send(f"💖 **COMPLIMENT INCOMING!** 💖\n\n{target_name}, {compliment}")
    else:
        # Self-compliment or no target specified
        self_compliments = [
            "You had the wisdom to ask for a compliment - that shows great self-care! 💚",
            "You're brave enough to practice self-love, and that's beautiful! 🌸",
            "Taking care of your mental health by asking for positivity? That's amazing! ✨",
            "You're smart enough to know you deserve kind words! 🧠💖",
            "Self-love isn't selfish - you're setting a great example! 🌟",
            "You're wonderful exactly as you are! 💝",
            "You deserve all the compliments in the world! 👑",
            "You're taking steps to be kinder to yourself, and that's incredible progress! 🦋"
        ]
        compliment = random.choice(self_compliments)
        await ctx.send(f"💖 **SELF-LOVE ACTIVATED!** 💖\n\n{ctx.author.mention}, {compliment}")


async def dadjoke_command(ctx, bot):
    """Send a random dad joke! Usage: !dadjokes"""
    import random
    
    dad_jokes = [
        "Why don't scientists trust atoms? Because they make up everything!",
        "I invented a new word: Plagiarism!",
        "Did you hear the rumor about butter? Well, I'm not going to spread it!",
        "Why can't a bicycle stand up by itself? It's two tired!",
        "What do you call a sleeping bull? A bulldozer!",
        "I only know 25 letters of the alphabet. I don't know y.",
        "What do you call a fake noodle? An Impasta!",
        "How do you organize a space party? You planet!",
        "Want to hear a joke about construction? I'm still working on it!",
        "What's the best thing about Switzerland? I don't know, but the flag is a big plus.",
        "I used to hate facial hair, but then it grew on me.",
        "Why do fathers take an extra pair of socks when they go golfing? In case they get a hole in one!",
        "What's the difference between a fish and a piano? You can't tuna fish!",
        "How does a penguin build its house? Igloos it together!",
        "Why don't scientists trust stairs? Because they're always up to something!",
        "What do you call a bear with no teeth? A gummy bear!",
        "Why did the coffee file a police report? It got mugged!",
        "What do you call a dinosaur that crashes his car? Tyrannosaurus Wrecks!",
        "Why did the math book look so sad? Because of all of its problems!",
        "What do you call a fish wearing a bowtie? Sofishticated!",
        "I'm reading a book on anti-gravity. It's impossible to put down!",
        "What do you call a factory that sells okay products? A satisfactory!",
        "Dear Math, grow up and solve your own problems.",
        "Why did the scarecrow win an award? He was outstanding in his field!",
        "What do you call a dog magician? A labracadabrador!",
        "Why don't eggs tell jokes? They'd crack each other up!",
        "What's orange and sounds like a parrot? A carrot!",
        "How do you make a tissue dance? You put a little boogie in it!",
        "What do you call a pig that does karate? A pork chop!",
        "Why did the cookie go to the doctor? Because it felt crumbly!",
        "What do you call a cow with no legs? Ground beef!",
        "Why don't melons get married? Because they cantaloupe!",
        "What do you call a sleeping bull in a hammock? A bulldozer taking a power nap!",
        "I told my wife she should embrace her mistakes. She hugged me.",
        "Why did the golfer bring two pairs of pants? In case he got a hole in one!",
        "What do you call a belt made of watches? A waist of time!",
        "Why don't scientists trust atoms? Because they make up everything and split when things get heated!",
        "What's the best way to watch a fly fishing tournament? Live stream!",
        "Why did the bicycle fall over? Because it was two-tired!",
        "What do you call a group of disorganized cats? A cat-astrophe!",
        "I'm terrified of elevators, so I'll take steps to avoid them.",
        "What do you call a fish that needs help with his or her vocals? Auto-tuna!",
        "Why don't some couples go to the gym? Because some relationships don't work out!",
        "What do you call a bee that can't make up its mind? A maybe!",
        "I lost my job at the bank. A woman asked me to check her balance, so I pushed her over.",
        "Why did the invisible man turn down the job offer? He couldn't see himself doing it.",
        "What did the ocean say to the beach? Nothing, it just waved.",
        "I haven't spoken to my wife in years. I didn't want to interrupt her.",
        "Why don't programmers like nature? It has too many bugs.",
        "I was going to tell a time-traveling joke, but you guys didn't like it.",
        "What do you call a fake stone in Ireland? A sham rock!",
        "I'm so good at sleeping, I can do it with my eyes closed!",
        "Why did the tomato turn red? Because it saw the salad dressing!",
        "What do you call a cow in an earthquake? A milkshake!",
        "I bought a dog from a blacksmith. As soon as I got home, he made a bolt for the door!",
        "I'm reading a horror book in braille. Something bad is about to happen, I can feel it.",
        "What do you call a fish wearing a crown? Your royal high-ness!",
        "Why did the cookie cry? Because his mom was a wafer too long!",
        "What do you call a dinosaur that loves to sleep? A dino-snore!",
        "I told my dad a joke about unemployment, but it needs work.",
        "Why do dads always seem to have the best jokes? Because they're not just regular jokes, they're 'dad-joke-certified'!"
    ]
    
    joke = random.choice(dad_jokes)
    await ctx.send(f"🧔 **Dad Joke Alert!** 🧔\n\n{joke}")
    
    # Track command usage achievement
    try:
        from achievements import achievement_system
        
        # Update the user's pun usage count and check for achievements (dad jokes count as puns)
        user_achievement = achievement_system.get_user_achievement(ctx.author.id, "pun_lover")
        current_uses = user_achievement.progress.get("pun_uses", 0) + 1
        
        # Always update progress first
        user_achievement.progress["pun_uses"] = current_uses
        achievement_system._progress_updated = True
        achievement_system._save_progress_updates()  # Force save immediately
        
        # Update progress and check if achievement should be unlocked
        if achievement_system.check_achievement(ctx.author.id, "pun_lover", {"pun_uses": current_uses}):
            achievement = achievement_system.achievements["pun_lover"]
            await send_achievement_notification(bot, ctx.author, achievement)
            # Note: Points will be awarded by the calling function in app.py if needed
    
    except Exception as e:
        import logging
        logger = logging.getLogger('StarChan.Utils')
        logger.error(f"Error tracking dad joke achievement: {e}")


# === CHATTERBOT SYSTEM ===

class ChatterBotConfig:
    """Configuration for the chatterbot system."""
    
    # Personality settings
    PERSONALITY_TRAITS = {
        "humor_level": 0.7,  # 0-1, how often to be funny
        "sarcasm_level": 0.3,  # 0-1, how sarcastic to be
        "helpfulness": 0.8,  # 0-1, how helpful to try to be
        "casualness": 0.6,  # 0-1, how casual/formal language
        "gaming_focus": 0.8,  # 0-1, focus on gaming topics
    }
    
    # Content filtering - topics to avoid or redirect
    FILTERED_TOPICS = [
        "politics", "political", "election", "democrat", "republican", "liberal",
        "woke", "sjw", "feminist", "racism", "sexism", "gender", "pronouns", "lgbtq",
        "climate change", "global warming", "vaccine", "covid", "conspiracy", "religion",
        "abortion", "immigration", "blm", "antifa", "biden"
    ]
    
    # Safe redirect responses when filtered topics come up
    REDIRECT_RESPONSES = [
        "Let's talk about something more fun! Got any gaming questions?",
        "How about we chat about Discord server stuff instead?",
        "I prefer to keep things light and gaming-focused! What games are you playing?",
        "Let's stick to fun topics! Need help with bot commands?",
        "I'm better at talking about games and Discord features!",
        "How about we discuss something more entertaining?",
    ]
    
    # Response templates for different contexts
    RESPONSE_TEMPLATES = {
        "greeting": [
            "Hey there! What's up?",
            "Hello! How can I help?",
            "Hi! Ready for some gaming talk?",
            "Yo! What's going on?",
        ],
        "help": [
            "I'm here to help! What do you need?",
            "Sure thing! What's the question?",
            "Happy to assist! Fire away!",
            "Let me help you out! What's up?",
        ],
        "gaming": [
            "Nice! I love talking about games!",
            "Gaming is awesome! Tell me more!",
            "Sweet! What's your favorite game?",
            "Games are the best! What are you playing?",
        ],
        "discord": [
            "Discord stuff is my specialty!",
            "I know all about Discord features!",
            "Discord is awesome! What do you want to know?",
            "Let me help you with Discord!",
        ],
        "confusion": [
            "I'm not sure I understand. Could you rephrase that?",
            "Hmm, I didn't quite get that. Try asking differently?",
            "Could you be more specific?",
            "I'm a bit confused. What exactly are you asking?",
        ],
        "fallback": [
            "That's interesting! Tell me more.",
            "Cool! What else?",
            "Neat! Anything else on your mind?",
            "Nice! What do you think about it?",
        ]
    }

class ContentFilter:
    """Filter system to avoid controversial topics."""
    
    @staticmethod
    def contains_filtered_content(text: str) -> bool:
        """Check if text contains filtered topics."""
        text_lower = text.lower()
        for topic in ChatterBotConfig.FILTERED_TOPICS:
            if topic in text_lower:
                return True
        return False
    
    @staticmethod
    def get_redirect_response() -> str:
        """Get a random redirect response."""
        return random.choice(ChatterBotConfig.REDIRECT_RESPONSES)

class ResponseGenerator:
    """Enhanced AI response generator with advanced context awareness."""
    
    # Advanced response templates with more variety and intelligence
    ADVANCED_TEMPLATES = {
        "greeting": {
            "casual": ["Hey! What's going on?", "Yo! How's it hanging?", "Sup! Ready to chat?"],
            "friendly": ["Hello there! How are you doing today?", "Hi! Great to see you again!", "Hey! Hope you're having an awesome day!"],
            "gaming": ["Hey gamer! What's the latest?", "Yo! Ready to talk games?", "Hey! Discovered any cool games lately?"],
            "contextual": ["Welcome back! Last time we were talking about {topic} - how did that go?", "Hey! Ready to continue where we left off?", "Hi again! I've been thinking about what you said earlier."]
        },
        "help": {
            "direct": ["I'm here to help! What's the question?", "Sure thing! Fire away!", "Absolutely! What do you need?"],
            "encouraging": ["I'd love to help you out! What's up?", "No problem at all! What can I assist with?", "I'm on it! Tell me what you need!"],
            "technical": ["I can help with that! What specific issue are you facing?", "Let me assist you! What's the technical challenge?"],
            "analytical": ["Let me break this down for you. What's the main issue?", "I'll help you work through this systematically. What's step one?", "Good question! Let's think about this logically."]
        },
        "gaming": {
            "enthusiastic": ["Gaming! My favorite topic! Tell me more!", "Awesome! I love talking games! What are you playing?", "Sweet! Games are the best! What's your current obsession?"],
            "curious": ["Interesting game choice! How are you finding it?", "Nice! I've heard good things about that. What do you think?", "Cool game! What's your favorite part about it?"],
            "experienced": ["Ah, a classic choice! I remember that one well.", "Great game! The mechanics in that one are really well done.", "Solid pick! That game has amazing replay value."],
            "analytical": ["That's a fascinating game design choice. What drew you to it?", "Interesting! That game has some unique mechanics. Which ones stand out to you?", "Good choice! What aspects of the gameplay do you find most engaging?"]
        },
        "conversation": {
            "thoughtful": ["That's a really insightful perspective! I hadn't considered it that way.", "You raise an excellent point there. It makes me think about...", "That's fascinating! Your viewpoint really adds depth to this topic."],
            "curious": ["I'm genuinely curious about your experience with that. Could you elaborate?", "That sounds like there's an interesting story behind it. Care to share more?", "Your approach to that is intriguing. What led you to that conclusion?"],
            "building": ["Building on what you said, I think there's also the aspect of...", "That connects to something interesting - have you considered...", "Your point reminds me of a broader pattern I've noticed..."]
        },
        "emotional": {
            "excited": ["That sounds amazing! I'm excited for you! 🎉", "Wow! That's so cool! Tell me everything!", "No way! That's incredible! 🎮"],
            "supportive": ["I'm here for you! Want to talk about it?", "That sounds tough. How are you handling it?", "I understand. Sometimes gaming helps me too."],
            "celebratory": ["Congratulations! That's awesome! 🎊", "Way to go! You should be proud!", "That's fantastic news! Well done!"],
            "empathetic": ["I can really understand why you'd feel that way.", "That makes perfect sense given the situation.", "Your reaction is completely understandable."]
        },
        "contextual": {
            "follow_up": ["That reminds me of what you mentioned before!", "Building on our last conversation...", "Speaking of which, how did that work out?"],
            "memory": ["I remember you telling me about that!", "Didn't you say something similar last time?", "That connects to what we discussed!"],
            "synthesis": ["Connecting the dots from our previous chats, it seems like...", "This ties into that pattern we've been discussing...", "I'm seeing a theme emerge from our conversations..."]
        }
    }
    
    # Enhanced gaming knowledge with more nuanced understanding
    GAMING_KNOWLEDGE = {
        "fps": {
            "games": ["Call of Duty", "Counter-Strike", "Valorant", "Overwatch", "Apex Legends", "Fortnite", "Doom", "Titanfall"],
            "characteristics": ["fast-paced", "competitive", "skill-based", "team coordination", "aim-intensive"],
            "discussions": ["aim training", "map knowledge", "team strategy", "weapon meta", "competitive rankings"]
        },
        "rpg": {
            "games": ["Skyrim", "Witcher", "Final Fantasy", "Persona", "Baldur's Gate", "Cyberpunk", "Mass Effect", "Dragon Age"],
            "characteristics": ["story-driven", "character development", "immersive worlds", "choice consequences"],
            "discussions": ["character builds", "story choices", "side quests", "world exploration", "narrative depth"]
        },
        "mmo": {
            "games": ["World of Warcraft", "Final Fantasy XIV", "Guild Wars", "Elder Scrolls Online", "Lost Ark"],
            "characteristics": ["social gameplay", "long-term progression", "guild cooperation", "endgame content"],
            "discussions": ["guild dynamics", "raid strategies", "progression systems", "community events"]
        },
        "strategy": {
            "games": ["Age of Empires", "Civilization", "StarCraft", "Total War", "Chess", "Crusader Kings"],
            "characteristics": ["tactical thinking", "resource management", "long-term planning", "complex systems"],
            "discussions": ["strategic depth", "decision making", "resource optimization", "competitive meta"]
        },
        "indie": {
            "games": ["Hades", "Celeste", "Hollow Knight", "Stardew Valley", "Undertale", "Ori", "Dead Cells"],
            "characteristics": ["innovative gameplay", "artistic expression", "unique mechanics", "personal stories"],
            "discussions": ["creative design", "emotional impact", "gameplay innovation", "artistic vision"]
        }
    }
    
    # Conversation patterns for smarter responses
    SMART_PATTERNS = {
        "elaboration_prompts": [
            "That's interesting! What specifically about {topic} caught your attention?",
            "I'd love to hear more about your experience with {topic}. What stood out?",
            "That sounds fascinating! Could you walk me through your thought process on {topic}?",
            "Your perspective on {topic} is intriguing. What led you to that viewpoint?"
        ],
        "connection_builders": [
            "That actually connects to something you mentioned before about {previous_topic}.",
            "Interesting how that relates to our earlier discussion on {previous_topic}!",
            "I'm seeing a pattern here with your interest in {theme}. Tell me more!",
            "That's consistent with what I've learned about your preferences for {category}."
        ],
        "analytical_responses": [
            "From what I understand, you seem to enjoy {pattern}. Is that accurate?",
            "Based on our conversations, I'm noticing you gravitate toward {theme}. What draws you to that?",
            "It sounds like {aspect} is particularly important to you in {context}. Why is that?",
            "I'm curious about the underlying appeal of {element} for you. What makes it compelling?"
        ]
    }
    
    # Advanced emotion detection
    EMOTION_KEYWORDS = {
        "excited": ["awesome", "amazing", "incredible", "fantastic", "love", "best", "perfect", "!!", "omg"],
        "frustrated": ["annoying", "stupid", "hate", "worst", "terrible", "awful", "ugh", "damn"],
        "happy": ["happy", "good", "great", "nice", "cool", "fun", "enjoy", "like", "yes"],
        "sad": ["sad", "down", "depressed", "awful", "terrible", "bad day", "worst"],
        "curious": ["how", "what", "why", "when", "where", "?", "wondering", "curious"],
        "achievement": ["won", "beat", "completed", "finished", "achieved", "got", "unlocked", "level up"]
    }
    
    # Gaming knowledge base for smarter responses
    GAMING_KNOWLEDGE = {
        "fps": ["Call of Duty", "Counter-Strike", "Valorant", "Overwatch", "Apex Legends", "Fortnite"],
        "rpg": ["Skyrim", "Witcher", "Final Fantasy", "Persona", "Baldur's Gate", "Cyberpunk"],
        "mmo": ["World of Warcraft", "Final Fantasy XIV", "Guild Wars", "Elder Scrolls Online"],
        "strategy": ["Age of Empires", "Civilization", "StarCraft", "Total War", "Chess"],
        "indie": ["Hades", "Celeste", "Hollow Knight", "Stardew Valley", "Undertale"],
        "platforms": ["Steam", "Epic", "PlayStation", "Xbox", "Nintendo Switch", "PC"]
    }
    
    @staticmethod
    def analyze_intent(message: str) -> str:
        """Enhanced intent analysis with emotion detection."""
        message_lower = message.lower()
        
        # Greeting detection (more sophisticated)
        greetings = ["hi", "hello", "hey", "yo", "sup", "what's up", "howdy", "good morning", "good evening"]
        if any(greeting in message_lower for greeting in greetings) and len(message.split()) <= 3:
            return "greeting"
        
        # Help/Question detection (more nuanced)
        help_indicators = ["help", "how do i", "can you", "what is", "where", "when", "why", "how to"]
        if any(indicator in message_lower for indicator in help_indicators):
            return "help"
        
        # Gaming detection (expanded)
        gaming_terms = ["game", "gaming", "play", "steam", "xbox", "playstation", "nintendo", "pc", 
                       "fps", "rpg", "mmo", "level", "quest", "boss", "character", "multiplayer"]
        if any(term in message_lower for term in gaming_terms):
            return "gaming"
        
        # Discord/Bot detection
        discord_terms = ["discord", "server", "channel", "role", "bot", "command", "slash command"]
        if any(term in message_lower for term in discord_terms):
            return "discord"
        
        # Achievement/Success detection
        achievement_terms = ["won", "beat", "completed", "finished", "got", "unlocked", "achieved"]
        if any(term in message_lower for term in achievement_terms):
            return "achievement"
        
        # Question detection
        if "?" in message or message_lower.startswith(("what", "how", "why", "when", "where", "who")):
            return "help"
        
        return "conversation"
    
    @staticmethod
    def detect_emotion(message: str) -> str:
        """Detect emotional tone of the message."""
        message_lower = message.lower()
        emotion_scores = {}
        
        for emotion, keywords in ResponseGenerator.EMOTION_KEYWORDS.items():
            score = sum(1 for keyword in keywords if keyword in message_lower)
            if score > 0:
                emotion_scores[emotion] = score
        
        # Return the emotion with highest score, or 'neutral' if none detected
        return max(emotion_scores, key=emotion_scores.get) if emotion_scores else "neutral"
    
    @staticmethod
    def generate_response(message: str, user_id: str, context: Dict[str, Any]) -> str:
        """Generate intelligent, contextual response."""
        
        # Filter check first
        if ContentFilter.contains_filtered_content(message):
            return ContentFilter.get_redirect_response()
        
        # Analyze intent and emotion
        intent = ResponseGenerator.analyze_intent(message)
        emotion = ResponseGenerator.detect_emotion(message)
        
        # Get conversation history for context
        history = context.get("recent_messages", [])
        user_preferences = context.get("preferences", {})
        
        # Generate contextual response
        response = ResponseGenerator._generate_contextual_response(
            message, intent, emotion, history, user_preferences
        )
        
        # Add personality and polish
        response = ResponseGenerator._enhance_with_personality(response, emotion, context)
        
        return response
    
    @staticmethod
    def _generate_contextual_response(message: str, intent: str, emotion: str, history: List, preferences: Dict) -> str:
        """Generate highly intelligent response based on context and deep understanding."""
        
        # Handle different intents with enhanced intelligence
        if intent == "greeting":
            if emotion == "excited":
                return random.choice(ResponseGenerator.ADVANCED_TEMPLATES["greeting"]["gaming"])
            elif len(history) > 0:
                # Smart contextual greeting referencing previous conversations
                last_topic = history[-1].get("intent", "") if history else ""
                if last_topic == "gaming":
                    return "Hey! Good to see you back! How's the gaming going?"
                else:
                    return random.choice(ResponseGenerator.ADVANCED_TEMPLATES["greeting"]["contextual"])
            else:
                return random.choice(ResponseGenerator.ADVANCED_TEMPLATES["greeting"]["friendly"])
        
        elif intent == "gaming":
            message_lower = message.lower()
            detected_games = []
            detected_category = None
            
            # Enhanced game detection with category understanding
            for category, game_data in ResponseGenerator.GAMING_KNOWLEDGE.items():
                games = game_data.get("games", []) if isinstance(game_data, dict) else game_data
                for game in games:
                    if game.lower() in message_lower:
                        detected_games.append(game)
                        detected_category = category
                        break
            
            if detected_games and detected_category:
                game = detected_games[0]
                category_info = ResponseGenerator.GAMING_KNOWLEDGE[detected_category]
                
                if isinstance(category_info, dict):
                    characteristics = category_info.get("characteristics", [])
                    discussions = category_info.get("discussions", [])
                    
                    # Generate intelligent game-specific response
                    if emotion == "excited":
                        char = random.choice(characteristics) if characteristics else "engaging"
                        return f"Oh wow! {game} is incredible! I love how {char} it is. What's been your favorite moment so far?"
                    elif emotion == "frustrated":
                        disc = random.choice(discussions) if discussions else "the gameplay"
                        return f"I can understand the frustration with {game}. Are you having issues with {disc}? I might be able to help!"
                    else:
                        responses = [
                            f"Excellent choice with {game}! That's a fantastic {detected_category.upper()} game. What drew you to it initially?",
                            f"{game}! Great taste. I'm curious - what aspect of the {char if 'char' in locals() else 'gameplay'} appeals to you most?",
                            f"Nice! {game} has such {random.choice(characteristics) if characteristics else 'engaging'} gameplay. How long have you been playing?"
                        ]
                        return random.choice(responses)
            
            # Fallback gaming responses with more intelligence
            if emotion == "excited":
                return random.choice(ResponseGenerator.ADVANCED_TEMPLATES["gaming"]["enthusiastic"])
            elif emotion == "curious":
                return random.choice(ResponseGenerator.ADVANCED_TEMPLATES["gaming"]["analytical"])
            else:
                return random.choice(ResponseGenerator.ADVANCED_TEMPLATES["gaming"]["curious"])
        
        elif intent == "help":
            if emotion == "frustrated":
                return random.choice([
                    "I can see this is frustrating! Let me help you work through this systematically.",
                    "Don't worry, we'll get this figured out! What's the main challenge you're facing?",
                    "I understand the frustration. Let's break this down into manageable pieces."
                ])
            elif "?" in message:
                return random.choice(ResponseGenerator.ADVANCED_TEMPLATES["help"]["analytical"])
            else:
                return random.choice(ResponseGenerator.ADVANCED_TEMPLATES["help"]["encouraging"])
        
        elif intent == "achievement":
            # Enhanced celebration with context
            if "beat" in message.lower() or "completed" in message.lower():
                return random.choice([
                    "Congratulations on that achievement! 🎊 That must feel amazing. What was the most challenging part?",
                    "Way to go! 🎉 Completing that takes real dedication. How long did it take you?",
                    "That's fantastic! 🎮 You should be really proud. What's next on your gaming list?"
                ])
            else:
                return random.choice(ResponseGenerator.ADVANCED_TEMPLATES["emotional"]["celebratory"])
        
        elif intent == "conversation":
            # Enhanced conversation intelligence with pattern recognition
            if len(history) > 2:
                # Look for conversation patterns
                recent_topics = [entry.get("intent", "") for entry in history[-3:]]
                if recent_topics.count("gaming") >= 2:
                    return random.choice([
                        "I'm noticing we keep coming back to gaming topics! I love that. What is it about games that draws you in?",
                        "You're clearly passionate about gaming! That enthusiasm is infectious. What got you into gaming originally?",
                        "Our conversations always seem to circle back to games - not that I'm complaining! What's your gaming origin story?"
                    ])
            
            # Smart conversational responses based on emotion and context
            if emotion == "excited":
                return random.choice(ResponseGenerator.ADVANCED_TEMPLATES["conversation"]["thoughtful"])
            elif emotion == "curious":
                return random.choice(ResponseGenerator.ADVANCED_TEMPLATES["conversation"]["curious"])
            else:
                return random.choice(ResponseGenerator.ADVANCED_TEMPLATES["conversation"]["building"])
        
        # Enhanced fallback with contextual intelligence
        if len(history) > 0:
            last_emotion = history[-1].get("emotion", "neutral") if history else "neutral"
            if last_emotion == emotion and emotion != "neutral":
                return random.choice([
                    f"I can sense you're feeling {emotion} about this. Want to dive deeper into what's behind that?",
                    f"Your {emotion} energy is really coming through! Tell me more about what's driving that feeling.",
                    f"I'm picking up on some strong {emotion} vibes here. What's the story behind that?"
                ])
        
        # Ultra-smart fallback responses
        smart_fallbacks = [
            "That's a really thought-provoking point! I'm curious about the deeper implications. What's your take?",
            "You've got me thinking now! There are so many angles to consider here. Which aspect interests you most?",
            "Fascinating perspective! I love how you approach these topics. What experiences shaped that viewpoint?",
            "That's the kind of insight that makes conversations worthwhile! Could you elaborate on that idea?",
            "Your way of looking at things is really refreshing! What other thoughts do you have on this?"
        ]
        return random.choice(smart_fallbacks)
    
    @staticmethod
    def _enhance_with_personality(response: str, emotion: str, context: Dict) -> str:
        """Add highly intelligent personality based on context and emotional understanding."""
        config = ChatterBotConfig.PERSONALITY_TRAITS
        
        # Advanced emotional responsiveness
        if emotion == "excited" and random.random() < 0.7:
            emojis = ["🎮", "🎉", "🔥", "⭐", "✨", "🎊"]
            response += " " + random.choice(emojis)
        elif emotion == "happy" and random.random() < 0.5:
            response += random.choice([" 😊", " 👍", " 🙂"])
        elif emotion == "curious" and random.random() < 0.4:
            response += random.choice([" 🤔", " 💭", " ❓"])
        
        # Smart conversational enhancement based on context
        conversation_count = context.get("conversation_count", 0)
        relationship_level = context.get("relationship_level", "new")
        
        # Relationship-aware conversation starters
        if random.random() < config["helpfulness"] * 0.6:
            if relationship_level == "close_friend" and not response.endswith("?"):
                friendly_additions = [
                    " What are your thoughts on that?",
                    " I'm really curious what you think about this!",
                    " How does that align with your experience?",
                    " What's your gut feeling on this?"
                ]
                response += random.choice(friendly_additions)
            elif relationship_level in ["friend", "acquaintance"] and not response.endswith("?"):
                polite_additions = [
                    " What do you think?",
                    " How's that working out for you?",
                    " What's been your experience?",
                    " Any thoughts on that?"
                ]
                response += random.choice(polite_additions)
        
        # Advanced casual language based on relationship
        if random.random() < config["casualness"]:
            # More casual with closer relationships
            casualness_factor = 1.0 if relationship_level == "close_friend" else 0.7
            if random.random() < casualness_factor:
                casual_replacements = {
                    "Hello": "Hey", "Yes": "Yeah", "I am": "I'm", 
                    "You are": "You're", "cannot": "can't", "do not": "don't",
                    "That is": "That's", "It is": "It's", "We are": "We're"
                }
                for formal, casual in casual_replacements.items():
                    response = response.replace(formal, casual)
        
        # Smart humor injection based on context
        if random.random() < config["humor_level"] * 0.4:
            preferences = context.get("preferences", {})
            comm_style = preferences.get("communication_style", "casual")
            
            if comm_style == "humorous" or emotion == "excited":
                humor_additions = [" 😄", " lol", " haha", " 😂", " 🎮"]
                response += random.choice(humor_additions)
        
        # Context-aware topic bridging
        recent_messages = context.get("recent_messages", [])
        if len(recent_messages) > 1 and random.random() < 0.15:
            # Occasionally reference previous conversation topics intelligently
            prev_intent = recent_messages[-2].get("intent", "") if len(recent_messages) >= 2 else ""
            current_intent = recent_messages[-1].get("intent", "") if recent_messages else ""
            
            if prev_intent == "gaming" and current_intent != "gaming" and random.random() < 0.3:
                gaming_bridges = [
                    " (This kind of reminds me of game design philosophy!)",
                    " (There's actually a parallel to this in gaming!)",
                    " (This is like strategic thinking in games!)"
                ]
                response += random.choice(gaming_bridges)
        
        return response

class ChatterBot:
    """Enhanced AI chatterbot with advanced memory and context awareness."""
    
    def __init__(self):
        self.conversation_history: Dict[str, List[Dict[str, Any]]] = {}
        self.last_response_time: Dict[str, datetime.datetime] = {}
        self.cooldown_seconds = 5  # Prevent spam
        self.enabled = False  # Start disabled
        
        # Advanced features
        self.user_preferences: Dict[str, Dict[str, Any]] = {}
        self.conversation_context: Dict[str, Dict[str, Any]] = {}
        self.memory_bank: Dict[str, List[str]] = {}  # Remember interesting things users say
        self.max_history_length = 10  # Keep last 10 messages for context
        
    def is_enabled(self) -> bool:
        """Check if chatterbot is enabled."""
        return self.enabled
    
    def toggle(self) -> bool:
        """Toggle chatterbot on/off."""
        self.enabled = not self.enabled
        return self.enabled
        
    def should_respond(self, user_id: str, message: str, channel_id: str, mentions_bot: bool = False) -> bool:
        """Determine if the bot should respond to this message."""
        
        if not self.enabled:
            return False
        
        # EXCLUSIVE: Only respond to the bot owner
        owner_id = BOT_CONFIG.get("BOT_OWNER_ID", 000000000000000000)
        if int(user_id) != owner_id:
            return False
        
        # ONLY respond when the bot is mentioned/tagged
        if not mentions_bot:
            return False
            
        # Check cooldown
        now = datetime.datetime.now()
        if user_id in self.last_response_time:
            if now - self.last_response_time[user_id] < datetime.timedelta(seconds=self.cooldown_seconds):
                return False
        
        # Don't respond to commands (starting with !)
        if message.strip().startswith("!"):
            return False
        
        # If we get here, it's you mentioning the bot - always respond
        return True
    
    def _learn_from_message(self, user_id: str, message: str) -> None:
        """Learn interesting things from user messages for better context."""
        message_lower = message.lower()
        
        # Initialize user preferences if not exists
        if user_id not in self.user_preferences:
            self.user_preferences[user_id] = {
                "favorite_games": [],
                "interests": [],
                "communication_style": "casual",
                "emotional_tone": "neutral"
            }
        
        # Learn about games user plays
        for category, games in ResponseGenerator.GAMING_KNOWLEDGE.items():
            for game in games:
                if game.lower() in message_lower and game not in self.user_preferences[user_id]["favorite_games"]:
                    self.user_preferences[user_id]["favorite_games"].append(game)
                    
                    # Remember this in memory bank
                    if user_id not in self.memory_bank:
                        self.memory_bank[user_id] = []
                    self.memory_bank[user_id].append(f"Plays {game}")
        
        # Learn communication style
        if any(word in message_lower for word in ["lol", "lmao", "haha", "😄", "😂"]):
            self.user_preferences[user_id]["communication_style"] = "humorous"
        elif any(word in message_lower for word in ["awesome", "amazing", "love", "!"]):
            self.user_preferences[user_id]["emotional_tone"] = "enthusiastic"
    
    def _get_context(self, user_id: str) -> Dict[str, Any]:
        """Enhanced context gathering with memory and preferences."""
        context = {
            "recent_messages": self.conversation_history.get(user_id, [])[-5:],  # Last 5 messages
            "preferences": self.user_preferences.get(user_id, {}),
            "memory": self.memory_bank.get(user_id, []),
            "conversation_count": len(self.conversation_history.get(user_id, [])),
            "relationship_level": self._assess_relationship_level(user_id)
        }
        return context
    
    def _assess_relationship_level(self, user_id: str) -> str:
        """Assess how well we know this user."""
        conversation_count = len(self.conversation_history.get(user_id, []))
        memory_count = len(self.memory_bank.get(user_id, []))
        
        if conversation_count > 20 and memory_count > 5:
            return "close_friend"
        elif conversation_count > 10:
            return "friend"
        elif conversation_count > 3:
            return "acquaintance"
        else:
            return "new"
    
    def _update_history(self, user_id: str, user_message: str, bot_response: str) -> None:
        """Update conversation history with enhanced tracking."""
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []
        
        # Add new conversation entry
        entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "user_message": user_message,
            "bot_response": bot_response,
            "message_length": len(user_message),
            "response_length": len(bot_response),
            "intent": ResponseGenerator.analyze_intent(user_message),
            "emotion": ResponseGenerator.detect_emotion(user_message)
        }
        
        self.conversation_history[user_id].append(entry)
        
        # Keep only recent history (memory management)
        if len(self.conversation_history[user_id]) > self.max_history_length:
            self.conversation_history[user_id] = self.conversation_history[user_id][-self.max_history_length:]
    
    def get_response(self, message: str, user_id: str, username: str, channel_id: str, mentions_bot: bool = False) -> Optional[str]:
        """Get an intelligent response with advanced context awareness."""
        
        if not self.should_respond(user_id, message, channel_id, mentions_bot):
            return None
        
        # Update response time
        self.last_response_time[user_id] = datetime.datetime.now()
        
        # Learn from this message
        self._learn_from_message(user_id, message)
        
        # Get enhanced context
        context = self._get_context(user_id)
        
        # Generate intelligent response
        response = ResponseGenerator.generate_response(message, user_id, context)
        
        # Add relationship-aware personalization
        response = self._personalize_response(response, user_id, context)
        
        # Update conversation history
        self._update_history(user_id, message, response)
        
        return response
    
    def _personalize_response(self, response: str, user_id: str, context: Dict[str, Any]) -> str:
        """Personalize response based on relationship and history."""
        relationship = context.get("relationship_level", "new")
        preferences = context.get("preferences", {})
        
        # Add relationship-appropriate elements
        if relationship == "close_friend":
            # More casual and reference shared history
            if random.random() < 0.3:
                memory = context.get("memory", [])
                if memory:
                    memory_ref = random.choice(memory)
                    response = f"{response} (Speaking of which, remember how you {memory_ref.lower()}?)"
        
        elif relationship == "friend":
            # Friendly but not too casual
            if random.random() < 0.2:
                response = f"{response} You always have interesting thoughts on this stuff!"
        
        # Adapt to communication style
        comm_style = preferences.get("communication_style", "casual")
        if comm_style == "humorous" and random.random() < 0.4:
            humor_additions = [" 😄", " lol", " haha", " 😂"]
            response += random.choice(humor_additions)
        
        # Reference favorite games occasionally
        favorite_games = preferences.get("favorite_games", [])
        if favorite_games and "game" in response.lower() and random.random() < 0.2:
            game = random.choice(favorite_games)
            response += f" (BTW, how's {game} going?)"
        
        return response
    
    def get_intelligence_stats(self) -> Dict[str, Any]:
        """Get statistics about the bot's learning and intelligence."""
        total_conversations = sum(len(history) for history in self.conversation_history.values())
        total_users = len(self.conversation_history)
        total_memories = sum(len(memories) for memories in self.memory_bank.values())
        total_preferences = len(self.user_preferences)
        
        return {
            "total_conversations": total_conversations,
            "unique_users": total_users,
            "memories_stored": total_memories,
            "users_with_preferences": total_preferences,
            "avg_conversations_per_user": total_conversations / max(total_users, 1)
        }

# Global chatterbot instance
chatter_bot = ChatterBot()

# === END CHATTERBOT SYSTEM ===