"""
StarChan Bot Achievements System
Handles achievement definitions, tracking, and persistent storage.
"""

import json
import logging
import time
import os
import shutil
import datetime
import discord
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, asdict

# Set up module logger
logger = logging.getLogger('StarChan.Achievements')

@dataclass
class Achievement:
    """Represents a single achievement."""
    id: str
    name: str
    description: str
    category: str
    emoji: str
    reward_points: int = 0
    reward_role: Optional[str] = None
    hidden: bool = False
    requirements: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.requirements is None:
            self.requirements = {}

@dataclass
class UserAchievement:
    """Represents a user's achievement progress."""
    achievement_id: str
    user_id: int
    unlocked: bool = False
    progress: Dict[str, Any] = None
    unlock_date: Optional[str] = None
    
    def __post_init__(self):
        if self.progress is None:
            self.progress = {}

class AchievementSystem:
    """Main achievements system class."""
    
    def __init__(self, data_file: str = "achievements_data.txt"):
        self.data_file = data_file
        self.achievements: Dict[str, Achievement] = {}
        self.user_data: Dict[int, Dict[str, UserAchievement]] = {}
        self._progress_updated = False  # Flag to track if progress needs saving
        self._last_progress_save = time.time()  # Timestamp of last progress save
        self._initialize_achievements()
        self._load_user_data()
    
    def _initialize_achievements(self):
        """Initialize all available achievements."""
        
        # Messaging achievements
        self.achievements["first_message"] = Achievement(
            id="first_message",
            name="Hello World!",
            description="Send your first message in the server",
            category="messaging",
            emoji="👋",
            reward_points=10,
            requirements={"messages": 1}
        )
        
        self.achievements["chatty"] = Achievement(
            id="chatty",
            name="Chatty Member",
            description="Send 100 messages",
            category="messaging",
            emoji="💬",
            reward_points=50,
            requirements={"messages": 100}
        )
        
        self.achievements["chatterbox"] = Achievement(
            id="chatterbox",
            name="Chatterbox",
            description="Send 1,000 messages",
            category="messaging",
            emoji="📢",
            reward_points=200,
            requirements={"messages": 1000}
        )
        
        self.achievements["conversation_master"] = Achievement(
            id="conversation_master",
            name="Conversation Master",
            description="Send 5,000 messages",
            category="messaging",
            emoji="🗣️",
            reward_points=500,
            reward_role="🗣️ Conversation Master 🗣️",
            requirements={"messages": 5000}
        )
        
        # Level achievements
        self.achievements["level_up"] = Achievement(
            id="level_up",
            name="Rising Star",
            description="Reach level 5",
            category="leveling",
            emoji="⭐",
            reward_points=25,
            requirements={"level": 5}
        )
        
        self.achievements["level_10"] = Achievement(
            id="level_10",
            name="Dedicated Member",
            description="Reach level 10",
            category="leveling",
            emoji="🌟",
            reward_points=100,
            requirements={"level": 10}
        )
        
        self.achievements["level_25"] = Achievement(
            id="level_25",
            name="Veteran",
            description="Reach level 25",
            category="leveling",
            emoji="🏆",
            reward_points=250,
            reward_role="🏆 Veteran 🏆",
            requirements={"level": 25}
        )
        
        self.achievements["level_50"] = Achievement(
            id="level_50",
            name="Elite Member",
            description="Reach level 50",
            category="leveling",
            emoji="👑",
            reward_points=500,
            reward_role="👑 Elite Member 👑",
            requirements={"level": 50}
        )
        
        # Gaming achievements
        self.achievements["first_tictactoe"] = Achievement(
            id="first_tictactoe",
            name="Tic-Tac-Toe Novice",
            description="Play your first tic-tac-toe game",
            category="gaming",
            emoji="❌",
            reward_points=15,
            requirements={"tictactoe_games": 1}
        )
        
        self.achievements["tictactoe_winner"] = Achievement(
            id="tictactoe_winner",
            name="X Marks the Spot",
            description="Win 5 tic-tac-toe games",
            category="gaming",
            emoji="🎯",
            reward_points=75,
            requirements={"tictactoe_wins": 5}
        )
        
        self.achievements["blackjack_winner"] = Achievement(
            id="blackjack_winner",
            name="Card Shark",
            description="Win 10 blackjack games",
            category="gaming",
            emoji="🃏",
            reward_points=100,
            requirements={"blackjack_wins": 10}
        )
        
        self.achievements["jackpot_winner"] = Achievement(
            id="jackpot_winner",
            name="Lucky Strike",
            description="Win the jackpot",
            category="gaming",
            emoji="💰",
            reward_points=200,
            requirements={"jackpot_wins": 1}
        )
        
        # Social achievements
        self.achievements["hugger"] = Achievement(
            id="hugger",
            name="Spread the Love",
            description="Give 50 hugs",
            category="social",
            emoji="🤗",
            reward_points=100,
            requirements={"hugs_given": 50}
        )
        
        self.achievements["patter"] = Achievement(
            id="patter",
            name="Head Patter",
            description="Give 25 pats",
            category="social",
            emoji="🖐️",
            reward_points=50,
            requirements={"pats_given": 25}
        )
        
        # Economy achievements
        self.achievements["first_purchase"] = Achievement(
            id="first_purchase",
            name="First Purchase",
            description="Buy your first role from the shop",
            category="economy",
            emoji="🛒",
            reward_points=50,
            requirements={"purchases": 1}
        )
        
        self.achievements["big_spender"] = Achievement(
            id="big_spender",
            name="Big Spender",
            description="Spend 25,000 points in the shop",
            category="economy",
            emoji="💸",
            reward_points=300,
            requirements={"total_spent": 25000}
        )
        
        # Special/Hidden achievements
        self.achievements["early_bird"] = Achievement(
            id="early_bird",
            name="Early Bird",
            description="Send a message between 5-7 AM",
            category="special",
            emoji="🌅",
            reward_points=30,
            hidden=True,
            requirements={"early_message": True}
        )
        
        self.achievements["night_owl"] = Achievement(
            id="night_owl",
            name="Night Owl",
            description="Send a message between 11 PM - 3 AM",
            category="special",
            emoji="🦉",
            reward_points=30,
            hidden=True,
            requirements={"night_message": True}
        )
        
        self.achievements["counting_contributor"] = Achievement(
            id="counting_contributor",
            name="Counter",
            description="Contribute to the counting game 10 times",
            category="counting",  # Changed from "special" to "counting"
            emoji="🔢",
            reward_points=75,
            requirements={"counting_contributions": 10}
        )
        
        self.achievements["perfectionist"] = Achievement(
            id="perfectionist",
            name="Perfectionist",
            description="Reach a counting milestone (100, 200, 500, etc.) in the counting channel",
            category="counting",  # Changed from "special" to "counting"
            emoji="💯",
            reward_points=150,
            hidden=True,
            requirements={"counting_milestone": True}
        )
        
        # More messaging achievements
        self.achievements["mega_chatter"] = Achievement(
            id="mega_chatter",
            name="Mega Chatter",
            description="Send 10,000 messages",
            category="messaging",
            emoji="📣",
            reward_points=1000,
            reward_role="📣 Mega Chatter 📣",
            requirements={"messages": 10000}
        )
        
        self.achievements["legendary_speaker"] = Achievement(
            id="legendary_speaker",
            name="Legendary Speaker",
            description="Send 25,000 messages",
            category="messaging",
            emoji="🎤",
            reward_points=2500,
            reward_role="🎤 Legendary Speaker 🎤",
            requirements={"messages": 25000}
        )
        
        # More leveling achievements
        self.achievements["level_75"] = Achievement(
            id="level_75",
            name="Master",
            description="Reach level 75",
            category="leveling",
            emoji="🎖️",
            reward_points=750,
            reward_role="🎖️ Master 🎖️",
            requirements={"level": 75}
        )
        
        self.achievements["level_100"] = Achievement(
            id="level_100",
            name="Grandmaster",
            description="Reach level 100",
            category="leveling",
            emoji="💎",
            reward_points=1500,
            reward_role="💎 Grandmaster 💎",
            requirements={"level": 100}
        )
        
        self.achievements["level_150"] = Achievement(
            id="level_150",
            name="Legend",
            description="Reach level 150",
            category="leveling",
            emoji="🏅",
            reward_points=3000,
            reward_role="🏅 Legend 🏅",
            requirements={"level": 150}
        )
        
        # More gaming achievements
        self.achievements["tictactoe_master"] = Achievement(
            id="tictactoe_master",
            name="Tic-Tac-Toe Master",
            description="Win 25 tic-tac-toe games",
            category="gaming",
            emoji="🏆",
            reward_points=200,
            requirements={"tictactoe_wins": 25}
        )
        
        self.achievements["blackjack_master"] = Achievement(
            id="blackjack_master",
            name="Casino Royale",
            description="Win 50 blackjack games",
            category="gaming",
            emoji="🎰",
            reward_points=500,
            reward_role="🎰 Casino Royale 🎰",
            requirements={"blackjack_wins": 50}
        )
        
        self.achievements["gaming_addict"] = Achievement(
            id="gaming_addict",
            name="Gaming Addict",
            description="Play 100 total games (any type)",
            category="gaming",
            emoji="🎮",
            reward_points=300,
            requirements={"total_games": 100}
        )
        
        self.achievements["lucky_seven"] = Achievement(
            id="lucky_seven",
            name="Lucky Seven",
            description="Win 7 jackpots",
            category="gaming",
            emoji="🍀",
            reward_points=777,
            hidden=True,
            requirements={"jackpot_wins": 7}
        )
        
        # Hangman achievements
        self.achievements["first_hangman"] = Achievement(
            id="first_hangman",
            name="Word Explorer",
            description="Play your first hangman game",
            category="gaming",
            emoji="🎯",
            reward_points=15,
            requirements={"hangman_games": 1}
        )
        
        self.achievements["hangman_winner"] = Achievement(
            id="hangman_winner",
            name="Word Detective",
            description="Win 5 hangman games",
            category="gaming",
            emoji="🔍",
            reward_points=75,
            requirements={"hangman_wins": 5}
        )
        
        self.achievements["hangman_master"] = Achievement(
            id="hangman_master",
            name="Vocabulary Master",
            description="Win 20 hangman games",
            category="gaming",
            emoji="📚",
            reward_points=200,
            requirements={"hangman_wins": 20}
        )
        
        self.achievements["perfect_hangman"] = Achievement(
            id="perfect_hangman",
            name="Flawless Victory",
            description="Win a hangman game without any wrong guesses",
            category="gaming",
            emoji="🌟",
            reward_points=100,
            hidden=True,
            requirements={"perfect_hangman_wins": 1}
        )
        
        self.achievements["hangman_speedster"] = Achievement(
            id="hangman_speedster",
            name="Quick Thinker",
            description="Win 10 hangman games with 4 or fewer wrong guesses",
            category="gaming",
            emoji="⚡",
            reward_points=150,
            requirements={"fast_hangman_wins": 10}
        )
        
        # More social achievements
        self.achievements["super_hugger"] = Achievement(
            id="super_hugger",
            name="Super Hugger",
            description="Give 20 hugs",
            category="social",
            emoji="🫂",
            reward_points=400,
            reward_role="🫂 Super Hugger 🫂",
            requirements={"hugs_given": 20}
        )
        
        self.achievements["pat_master"] = Achievement(
            id="pat_master",
            name="Pat Master",
            description="Give 20 pats",
            category="social",
            emoji="👋",
            reward_points=200,
            requirements={"pats_given": 20}
        )
        
        self.achievements["social_butterfly"] = Achievement(
            id="social_butterfly",
            name="Social Butterfly",
            description="Use social commands 500 times total",
            category="social",
            emoji="🦋",
            reward_points=250,
            requirements={"social_interactions": 500}
        )
        
        # More economy achievements
        self.achievements["shopaholic"] = Achievement(
            id="shopaholic",
            name="Shopaholic",
            description="Buy 5 different roles",
            category="economy",
            emoji="🛍️",
            reward_points=150,
            requirements={"purchases": 5}
        )
        
        self.achievements["whale"] = Achievement(
            id="whale",
            name="High Roller",
            description="Spend 100,000 points in total",
            category="economy",
            emoji="💳",
            reward_points=1000,
            reward_role="💳 High Roller 💳",
            requirements={"total_spent": 100000}
        )
        
        self.achievements["millionaire"] = Achievement(
            id="millionaire",
            name="Millionaire",
            description="Have 1,000,000 contribution points",
            category="economy",
            emoji="💰",
            reward_points=5000,
            reward_role="💰 Millionaire 💰",
            requirements={"total_points": 1000000}
        )
        
        # Time-based achievements
        self.achievements["weekender"] = Achievement(
            id="weekender",
            name="Weekend Warrior",
            description="Send a message on both Saturday and Sunday",
            category="time",
            emoji="📅",
            reward_points=75,
            hidden=True,
            requirements={"weekend_messages": True}
        )
        
        self.achievements["daily_visitor"] = Achievement(
            id="daily_visitor",
            name="Daily Visitor",
            description="Send messages on 7 consecutive days",
            category="time",
            emoji="📆",
            reward_points=100,
            requirements={"consecutive_days": 7}
        )
        
        self.achievements["dedication"] = Achievement(
            id="dedication",
            name="Dedication",
            description="Send messages on 30 consecutive days",
            category="time",
            emoji="🗓️",
            reward_points=500,
            reward_role="🗓️ Dedicated Member 🗓️",
            requirements={"consecutive_days": 30}
        )
        
        self.achievements["annual_member"] = Achievement(
            id="annual_member",
            name="Annual Member",
            description="Be active for 365 days (not consecutive)",
            category="time",
            emoji="🎂",
            reward_points=2000,
            reward_role="🎂 Annual Member 🎂",
            requirements={"total_active_days": 365}
        )
        
        # Command usage achievements
        self.achievements["pun_lover"] = Achievement(
            id="pun_lover",
            name="Pun Lover",
            description="Use the !pun command 50 times",
            category="commands",
            emoji="😄",
            reward_points=100,
            requirements={"pun_uses": 50}
        )
        
        self.achievements["fortune_seeker"] = Achievement(
            id="fortune_seeker",
            name="Fortune Seeker",
            description="Use the !8ball command 100 times",
            category="commands",
            emoji="🔮",
            reward_points=150,
            requirements={"eightball_uses": 100}
        )
        
        self.achievements["animal_lover"] = Achievement(
            id="animal_lover",
            name="Animal Lover",
            description="Use !cat and !doggo commands 10 times each",
            category="commands",
            emoji="🐾",
            reward_points=125,
            requirements={"cat_uses": 10, "dog_uses": 10}
        )
        
        self.achievements["helper"] = Achievement(
            id="helper",
            name="Helper",
            description="Use the !helpstar command 2 times",
            category="commands",
            emoji="❓",
            reward_points=50,
            requirements={"help_uses": 2}
        )
        
        # Special milestone achievements
        self.achievements["first_week"] = Achievement(
            id="first_week",
            name="First Week",
            description="Complete your first week in the server",
            category="milestones",
            emoji="🌟",
            reward_points=100,
            requirements={"days_in_server": 7}
        )
        
        self.achievements["first_month"] = Achievement(
            id="first_month",
            name="Monthly Regular",
            description="Complete your first month in the server",
            category="milestones",
            emoji="🌙",
            reward_points=300,
            requirements={"days_in_server": 30}
        )
        
        self.achievements["server_veteran"] = Achievement(
            id="server_veteran",
            name="Server Veteran",
            description="Be a member for 6 months",
            category="milestones",
            emoji="⚔️",
            reward_points=1000,
            reward_role="⚔️ Server Veteran ⚔️",
            requirements={"days_in_server": 180}
        )
        
        self.achievements["og_member"] = Achievement(
            id="og_member",
            name="OG Member",
            description="Be a member for 1 year",
            category="milestones",
            emoji="👴",
            reward_points=3000,
            reward_role="👴 OG Member 👴",
            requirements={"days_in_server": 365}
        )
        
        # Special behavior achievements
        self.achievements["emoji_enthusiast"] = Achievement(
            id="emoji_enthusiast",
            name="Emoji Enthusiast",
            description="Use 50 different emojis in messages",
            category="special",
            emoji="😀",
            reward_points=150,
            requirements={"unique_emojis": 50}
        )
        
        self.achievements["reaction_collector"] = Achievement(
            id="reaction_collector",
            name="Reaction Collector",
            description="Receive 1000 reactions on your messages",
            category="special",
            emoji="👍",
            reward_points=300,
            requirements={"reactions_received": 1000}
        )
        
        self.achievements["midnight_messenger"] = Achievement(
            id="midnight_messenger",
            name="Midnight Messenger",
            description="Send a message at exactly midnight (00:00)",
            category="special",
            emoji="🕛",
            reward_points=100,
            hidden=True,
            requirements={"midnight_message": True}
        )
        
        self.achievements["question_master"] = Achievement(
            id="question_master",
            name="Question Master",
            description="Send 100 messages with question marks",
            category="special",
            emoji="❓",
            reward_points=150,
            requirements={"question_messages": 100}
        )
        
        # Counting game specific achievements
        self.achievements["counting_hero"] = Achievement(
            id="counting_hero",
            name="Counting Hero",
            description="Contribute 100 numbers to counting",
            category="counting",
            emoji="🔢",
            reward_points=300,
            requirements={"counting_contributions": 100}
        )
        
        # NEW EASY-TO-OBTAIN ACHIEVEMENTS
        self.achievements["first_reaction"] = Achievement(
            id="first_reaction",
            name="First Reaction",
            description="Add your first reaction to any message",
            category="social",
            emoji="👍",
            reward_points=10,
            requirements={"reactions_added": 1}
        )
        
        self.achievements["reaction_enthusiast"] = Achievement(
            id="reaction_enthusiast",
            name="Reaction Enthusiast", 
            description="Add 50 reactions to messages",
            category="social",
            emoji="😊",
            reward_points=75,
            requirements={"reactions_added": 50}
        )
        
        self.achievements["emoji_user"] = Achievement(
            id="emoji_user",
            name="Emoji User",
            description="Use an emoji in a message",
            category="messaging",
            emoji="😀",
            reward_points=5,
            requirements={"emoji_messages": 1}
        )
        
        self.achievements["quick_responder"] = Achievement(
            id="quick_responder",
            name="Quick Responder",
            description="Send a message within 1 minute of someone else's message",
            category="social",
            emoji="⚡",
            reward_points=15,
            requirements={"quick_responses": 1}
        )
        
        self.achievements["morning_person"] = Achievement(
            id="morning_person",
            name="Morning Person",
            description="Send a message between 6-9 AM",
            category="time",
            emoji="🌅",
            reward_points=20,
            requirements={"morning_message": True}
        )
        
        self.achievements["afternoon_chatter"] = Achievement(
            id="afternoon_chatter",
            name="Afternoon Chatter",
            description="Send a message between 12-3 PM",
            category="time", 
            emoji="☀️",
            reward_points=20,
            requirements={"afternoon_message": True}
        )
        
        self.achievements["evening_socializer"] = Achievement(
            id="evening_socializer",
            name="Evening Socializer",
            description="Send a message between 6-9 PM",
            category="time",
            emoji="🌆",
            reward_points=20,
            requirements={"evening_message": True}
        )
        
        self.achievements["weekend_warrior"] = Achievement(
            id="weekend_warrior",
            name="Weekend Warrior",
            description="Send messages on both Saturday and Sunday in the same weekend",
            category="time",
            emoji="🎉",
            reward_points=50,
            requirements={"weekend_messages": True}
        )
        
        self.achievements["monthly_visitor"] = Achievement(
            id="monthly_visitor",
            name="Monthly Visitor",
            description="Send at least one message for 3 consecutive months",
            category="time",
            emoji="📅",
            reward_points=200,
            requirements={"consecutive_months": 3}
        )
        
        self.achievements["holiday_spirit"] = Achievement(
            id="holiday_spirit",
            name="Holiday Spirit",
            description="Send a message on a major holiday (Jan 1, Dec 25, etc.)",
            category="time",
            emoji="🎄",
            reward_points=100,
            hidden=True,
            requirements={"holiday_message": True}
        )
        
        self.achievements["birthday_celebration"] = Achievement(
            id="birthday_celebration",
            name="Birthday Celebration",
            description="Send a message containing 'happy birthday' or birthday emojis",
            category="social",
            emoji="🎂",
            reward_points=25,
            requirements={"birthday_messages": 1}
        )
        
        self.achievements["exclamation_enthusiast"] = Achievement(
            id="exclamation_enthusiast",
            name="Exclamation Enthusiast!",
            description="Send 25 messages with exclamation marks",
            category="messaging",
            emoji="❗",
            reward_points=40,
            requirements={"exclamation_messages": 25}
        )
        
        self.achievements["link_sharer"] = Achievement(
            id="link_sharer",
            name="Link Sharer",
            description="Share your first link or URL in a message",
            category="messaging", 
            emoji="🔗",
            reward_points=15,
            requirements={"links_shared": 1}
        )
        
        self.achievements["mention_master"] = Achievement(
            id="mention_master",
            name="Mention Master",
            description="Mention other users 20 times",
            category="social",
            emoji="@",
            reward_points=60,
            requirements={"mentions_sent": 20}
        )
        
        self.achievements["attachment_sender"] = Achievement(
            id="attachment_sender",
            name="File Sharer",
            description="Send your first message with an attachment or image",
            category="messaging",
            emoji="📎",
            reward_points=20,
            requirements={"attachments_sent": 1}
        )
        
        # MORE TIME-BASED ACHIEVEMENTS
        self.achievements["early_riser"] = Achievement(
            id="early_riser",
            name="Early Riser",
            description="Send messages before 7 AM on 5 different days",
            category="time",
            emoji="🐓",
            reward_points=100,
            requirements={"early_morning_days": 5}
        )
        
        self.achievements["late_night_regular"] = Achievement(
            id="late_night_regular",
            name="Late Night Regular",
            description="Send messages after 11 PM on 10 different days", 
            category="time",
            emoji="🌙",
            reward_points=150,
            requirements={"late_night_days": 10}
        )
        
        self.achievements["weekday_warrior"] = Achievement(
            id="weekday_warrior",
            name="Weekday Warrior",
            description="Send messages on all 5 weekdays in a single week",
            category="time",
            emoji="💼",
            reward_points=75,
            requirements={"weekday_streak": True}
        )
        
        self.achievements["seasonal_visitor"] = Achievement(
            id="seasonal_visitor", 
            name="Seasonal Visitor",
            description="Send messages in all 4 seasons (Spring, Summer, Fall, Winter)",
            category="time",
            emoji="🍂",
            reward_points=300,
            requirements={"seasons_active": 4}
        )
        
        self.achievements["hourly_chatter"] = Achievement(
            id="hourly_chatter",
            name="Around the Clock",
            description="Send messages during 12 different hours of the day",
            category="time", 
            emoji="🕐",
            reward_points=200,
            requirements={"unique_hours": 12}
        )
        
        self.achievements["milestone_hunter"] = Achievement(
            id="milestone_hunter",
            name="Milestone Hunter",
            description="Hit 5 different counting milestones",
            category="counting",
            emoji="🎯",
            reward_points=400,
            requirements={"milestones_hit": 5}
        )
        
        self.achievements["counting_legend"] = Achievement(
            id="counting_legend",
            name="Counting Legend",
            description="Contribute 500 numbers to counting",
            category="counting",
            emoji="🏆",
            reward_points=1000,
            reward_role="🏆 Counting Legend 🏆",
            requirements={"counting_contributions": 500}
        )
        
        # Fun achievements
        self.achievements["caps_lock_warrior"] = Achievement(
            id="caps_lock_warrior",
            name="CAPS LOCK WARRIOR",
            description="SEND 50 MESSAGES IN ALL CAPS",
            category="fun",
            emoji="📢",
            reward_points=100,
            hidden=True,
            requirements={"caps_messages": 50}
        )
        
        self.achievements["short_and_sweet"] = Achievement(
            id="short_and_sweet",
            name="Short and Sweet",
            description="Send 100 messages with 5 or fewer characters",
            category="fun",
            emoji="✂️",
            reward_points=125,
            requirements={"short_messages": 100}
        )
        
        self.achievements["novelist"] = Achievement(
            id="novelist",
            name="Novelist",
            description="Send a message with over 500 characters",
            category="fun",
            emoji="📚",
            reward_points=100,
            requirements={"long_message": True}
        )
    
    def _load_user_data(self):
        """Load user achievement data from file with integrity verification."""
        try:
            with open(self.data_file, 'r') as f:
                data = json.load(f)
                
            # Verify data integrity
            if not isinstance(data, dict):
                raise ValueError("Invalid data format: root is not a dictionary")
                
            loaded_users = 0
            for user_id_str, achievements_data in data.items():
                try:
                    user_id = int(user_id_str)
                    self.user_data[user_id] = {}
                    
                    if not isinstance(achievements_data, dict):
                        logger.warning(f"Invalid achievement data for user {user_id}")
                        continue
                    
                    for achievement_id, achievement_data in achievements_data.items():
                        # Verify achievement exists in system
                        if achievement_id not in self.achievements:
                            logger.warning(f"Unknown achievement {achievement_id} for user {user_id}")
                            continue
                            
                        # Verify required fields
                        required_fields = ["achievement_id", "user_id", "unlocked", "progress"]
                        if not all(field in achievement_data for field in required_fields):
                            logger.warning(f"Missing fields in achievement {achievement_id} for user {user_id}")
                            continue
                            
                        self.user_data[user_id][achievement_id] = UserAchievement(
                            achievement_id=achievement_data["achievement_id"],
                            user_id=achievement_data["user_id"],
                            unlocked=achievement_data["unlocked"],
                            progress=achievement_data["progress"],
                            unlock_date=achievement_data.get("unlock_date")
                        )
                    
                    loaded_users += 1
                    
                except (ValueError, KeyError) as user_error:
                    logger.error(f"Error loading data for user {user_id_str}: {user_error}")
                    continue
                    
            logger.debug(f"Loaded achievement data for {loaded_users} users ({len(data)} total entries)")
            
            # Verification: Check for any corrupted unlock states
            corrupted_count = 0
            for user_id, user_achievements in self.user_data.items():
                for achievement_id, user_achievement in user_achievements.items():
                    if user_achievement.unlocked and not user_achievement.unlock_date:
                        logger.warning(f"Corrupted unlock state detected: {achievement_id} for user {user_id}")
                        corrupted_count += 1
            
            if corrupted_count > 0:
                logger.warning(f"Found {corrupted_count} corrupted achievement entries")
            
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.warning(f"Could not load achievement data: {e}. Starting fresh.")
            self.user_data = {}
            
        except Exception as e:
            logger.error(f"Unexpected error loading achievement data: {e}")
            # Try to load from backup
            try:
                backup_file = f"{self.data_file}.backup"
                if os.path.exists(backup_file):
                    logger.info("Attempting to load from backup file")
                    with open(backup_file, 'r') as f:
                        data = json.load(f)
                    # Recursive call with backup data
                    self.data_file = backup_file
                    self._load_user_data()
                    self.data_file = self.data_file.replace('.backup', '')
                else:
                    logger.error("No backup file available, starting fresh")
                    self.user_data = {}
            except Exception as backup_error:
                logger.error(f"Failed to load from backup: {backup_error}")
                self.user_data = {}
    
    def _save_user_data(self):
        """Save user achievement data to file with backup mechanism."""
        try:
            # Convert to serializable format
            data = {}
            for user_id, achievements in self.user_data.items():
                data[str(user_id)] = {}
                for achievement_id, user_achievement in achievements.items():
                    data[str(user_id)][achievement_id] = asdict(user_achievement)
            
            # Create backup of existing file first
            if os.path.exists(self.data_file):
                backup_file = f"{self.data_file}.backup"
                try:
                    shutil.copy2(self.data_file, backup_file)
                    logger.debug(f"Backup created: {backup_file}")
                except Exception as backup_error:
                    logger.warning(f"Failed to create backup: {backup_error}")
            
            # Write to temporary file first, then rename (atomic operation)
            temp_file = f"{self.data_file}.tmp"
            with open(temp_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            # Atomic rename
            os.replace(temp_file, self.data_file)
                
            logger.debug("Achievement data saved successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error saving achievement data: {e}")
            # Try to restore from backup if main save failed
            try:
                backup_file = f"{self.data_file}.backup"
                if os.path.exists(backup_file):
                    shutil.copy2(backup_file, self.data_file)
                    logger.info("Restored from backup after save failure")
            except Exception as restore_error:
                logger.error(f"Failed to restore from backup: {restore_error}")
            return False
    
    def _save_progress_updates(self):
        """Save progress updates if any have been made."""
        if self._progress_updated:
            if self._save_user_data():
                self._progress_updated = False
                self._last_progress_save = time.time()
                logger.debug("Progress updates saved successfully")
            else:
                logger.warning("Failed to save progress updates")
    
    def force_save_progress(self):
        """Force save any pending progress updates."""
        if self._progress_updated:
            self._save_progress_updates()
            logger.info("Forced save of progress updates completed")
    
    def get_user_achievements(self, user_id: int) -> Dict[str, UserAchievement]:
        """Get all achievements for a user."""
        if user_id not in self.user_data:
            self.user_data[user_id] = {}
        return self.user_data[user_id]
    
    def get_user_achievement(self, user_id: int, achievement_id: str) -> UserAchievement:
        """Get specific achievement for a user."""
        user_achievements = self.get_user_achievements(user_id)
        
        if achievement_id not in user_achievements:
            user_achievements[achievement_id] = UserAchievement(
                achievement_id=achievement_id,
                user_id=user_id
            )
        
        return user_achievements[achievement_id]
    
    def check_achievement(self, user_id: int, achievement_id: str, current_stats: Dict[str, Any]) -> bool:
        """Check if user has unlocked an achievement with fail-safe duplicate prevention."""
        if achievement_id not in self.achievements:
            logger.warning(f"Achievement {achievement_id} not found in system")
            return False
        
        achievement = self.achievements[achievement_id]
        user_achievement = self.get_user_achievement(user_id, achievement_id)
        
        # CRITICAL: Skip if already unlocked (primary duplicate prevention)
        if user_achievement.unlocked:
            logger.debug(f"Achievement {achievement_id} already unlocked for user {user_id}")
            return False
        
        # FAIL-SAFE: Double-check unlock status by re-loading from file
        try:
            self._load_user_data()  # Refresh from file
            user_achievement = self.get_user_achievement(user_id, achievement_id)
            if user_achievement.unlocked:
                logger.warning(f"FAIL-SAFE: Achievement {achievement_id} already unlocked for user {user_id} (detected after reload)")
                return False
        except Exception as e:
            logger.error(f"Error during fail-safe check for achievement {achievement_id}: {e}")
        
        # Check requirements
        requirements_met = True
        for req_key, req_value in achievement.requirements.items():
            if req_key not in current_stats:
                requirements_met = False
                break
            
            if isinstance(req_value, bool):
                if not current_stats[req_key]:
                    requirements_met = False
                    break
            elif isinstance(req_value, (int, float)):
                if current_stats[req_key] < req_value:
                    requirements_met = False
                    break
        
        if requirements_met:
            return self.unlock_achievement(user_id, achievement_id)
        
        # Update progress and mark for saving
        user_achievement.progress.update(current_stats)
        self._progress_updated = True
        
        # Save progress periodically (every 30 seconds) to avoid too frequent I/O
        current_time = time.time()
        if current_time - self._last_progress_save > 30:  # 30 seconds
            self._save_progress_updates()
        
        return False
    
    def unlock_achievement(self, user_id: int, achievement_id: str) -> bool:
        """Unlock an achievement for a user with robust duplicate prevention."""
        if achievement_id not in self.achievements:
            logger.error(f"Achievement {achievement_id} not found")
            return False
        
        # FAIL-SAFE: Reload data before unlock attempt
        try:
            self._load_user_data()
        except Exception as e:
            logger.error(f"Failed to reload data before unlock: {e}")
        
        user_achievement = self.get_user_achievement(user_id, achievement_id)
        
        # CRITICAL: Check if already unlocked (with logging for debugging)
        if user_achievement.unlocked:
            logger.warning(f"DUPLICATE PREVENTION: Achievement {achievement_id} already unlocked for user {user_id}")
            return False
        
        # ATOMIC UNLOCK: Set all unlock properties at once
        unlock_timestamp = datetime.datetime.now().isoformat()
        user_achievement.unlocked = True
        user_achievement.unlock_date = unlock_timestamp
        
        # FAIL-SAFE: Immediate save with retry mechanism
        max_retries = 3
        for attempt in range(max_retries):
            try:
                if self._save_user_data():
                    logger.info(f"Achievement {achievement_id} unlocked for user {user_id} at {unlock_timestamp}")
                    return True
                else:
                    logger.warning(f"Save attempt {attempt + 1} failed for achievement {achievement_id}")
            except Exception as e:
                logger.error(f"Save attempt {attempt + 1} error for achievement {achievement_id}: {e}")
            
            if attempt < max_retries - 1:
                time.sleep(0.1)  # Brief delay before retry
        
        # If all saves failed, revert the unlock to prevent inconsistent state
        user_achievement.unlocked = False
        user_achievement.unlock_date = None
        logger.error(f"CRITICAL: Failed to save achievement {achievement_id} for user {user_id} after {max_retries} attempts")
        return False
    
    def get_unlocked_achievements(self, user_id: int) -> List[Achievement]:
        """Get all unlocked achievements for a user."""
        user_achievements = self.get_user_achievements(user_id)
        unlocked = []
        
        for achievement_id, user_achievement in user_achievements.items():
            if user_achievement.unlocked and achievement_id in self.achievements:
                unlocked.append(self.achievements[achievement_id])
        
        return unlocked
    
    def get_available_achievements(self, user_id: int, include_hidden: bool = False) -> List[Achievement]:
        """Get all available achievements for a user."""
        available = []
        
        for achievement in self.achievements.values():
            if achievement.hidden and not include_hidden:
                continue
            
            user_achievement = self.get_user_achievement(user_id, achievement.id)
            if not user_achievement.unlocked:
                available.append(achievement)
        
        return available
    
    def get_achievement_progress(self, user_id: int, achievement_id: str, current_stats: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get progress for a specific achievement with optional current stats."""
        if achievement_id not in self.achievements:
            return {}
        
        achievement = self.achievements[achievement_id]
        user_achievement = self.get_user_achievement(user_id, achievement_id)
        
        progress_info = {
            "achievement": achievement,
            "unlocked": user_achievement.unlocked,
            "unlock_date": user_achievement.unlock_date,
            "progress": {}
        }
        
        # Calculate progress for each requirement
        for req_key, req_value in achievement.requirements.items():
            # Use current stats if provided, otherwise fall back to stored progress
            if current_stats and req_key in current_stats:
                current = current_stats[req_key]
            else:
                current = user_achievement.progress.get(req_key, 0)
            
            if isinstance(req_value, bool):
                progress_info["progress"][req_key] = {
                    "current": current,
                    "required": req_value,
                    "percentage": 100 if current else 0
                }
            elif isinstance(req_value, (int, float)):
                percentage = min(100, (current / req_value) * 100) if req_value > 0 else 0
                progress_info["progress"][req_key] = {
                    "current": current,
                    "required": req_value,
                    "percentage": percentage
                }
        
        return progress_info
    
    def get_current_user_stats_from_bot(self, user_id: int, bot_instance=None) -> Dict[str, Any]:
        """Get current user stats from bot data for accurate progress tracking."""
        stats = {}
        
        try:
            # This would need to be called with the bot instance to get real data
            # For now, we'll return empty dict and let the calling code populate it
            if bot_instance:
                # Example of how to get stats from bot data
                # stats["messages"] = bot_instance.get_user_message_count(user_id)
                # stats["level"] = bot_instance.get_user_level(user_id)
                # etc.
                pass
            
        except Exception as e:
            logger.error(f"Error getting current user stats: {e}")
        
        return stats
    
    def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """Get achievement statistics for a user."""
        user_achievements = self.get_user_achievements(user_id)
        
        unlocked_count = sum(1 for ua in user_achievements.values() if ua.unlocked)
        total_count = len(self.achievements)
        
        # Calculate points from achievements
        total_points = 0
        for achievement_id, user_achievement in user_achievements.items():
            if user_achievement.unlocked and achievement_id in self.achievements:
                total_points += self.achievements[achievement_id].reward_points
        
        # Get unlocked by category
        categories = {}
        for achievement in self.achievements.values():
            category = achievement.category
            if category not in categories:
                categories[category] = {"total": 0, "unlocked": 0}
            categories[category]["total"] += 1
            
            user_achievement = self.get_user_achievement(user_id, achievement.id)
            if user_achievement.unlocked:
                categories[category]["unlocked"] += 1
        
        return {
            "unlocked_count": unlocked_count,
            "total_count": total_count,
            "completion_percentage": (unlocked_count / total_count) * 100 if total_count > 0 else 0,
            "total_points": total_points,
            "categories": categories
        }
    
    def get_total_contribution_points(self, user_id: int) -> int:
        """Get total contribution points for a user."""
        total_points = 0
        user_achievements = self.user_data.get(user_id, {})
        
        for achievement_id, user_achievement in user_achievements.items():
            if user_achievement.unlocked:
                achievement = self.achievements.get(achievement_id)
                if achievement:
                    total_points += achievement.contribution_points
                    
        return total_points
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status including data integrity checks."""
        status = {
            "total_achievements": len(self.achievements),
            "total_users": len(self.user_data),
            "data_file_exists": os.path.exists(self.data_file),
            "backup_file_exists": os.path.exists(f"{self.data_file}.backup"),
            "data_file_size": 0,
            "total_unlocked": 0,
            "categories": {},
            "integrity_issues": 0,
            "recent_unlocks": 0
        }
        
        try:
            if status["data_file_exists"]:
                status["data_file_size"] = os.path.getsize(self.data_file)
                
            # Count unlocked achievements and check integrity
            now = datetime.datetime.now()
            for user_id, user_achievements in self.user_data.items():
                for achievement_id, user_achievement in user_achievements.items():
                    if user_achievement.unlocked:
                        status["total_unlocked"] += 1
                        
                        # Check if unlocked in last 24 hours
                        if user_achievement.unlock_date:
                            try:
                                unlock_time = datetime.fromisoformat(user_achievement.unlock_date)
                                if (now - unlock_time).days < 1:
                                    status["recent_unlocks"] += 1
                            except ValueError:
                                status["integrity_issues"] += 1
                        else:
                            status["integrity_issues"] += 1
            
            # Count by category
            for achievement_id, achievement in self.achievements.items():
                category = achievement.category
                if category not in status["categories"]:
                    status["categories"][category] = {"total": 0, "unlocked": 0}
                status["categories"][category]["total"] += 1
                
                # Count unlocked in this category
                for user_id, user_achievements in self.user_data.items():
                    if achievement_id in user_achievements and user_achievements[achievement_id].unlocked:
                        status["categories"][category]["unlocked"] += 1
                        
        except Exception as e:
            logger.error(f"Error generating system status: {e}")
            status["error"] = str(e)
            
        return status

    def cleanup_invalid_users(self, guild) -> Dict[str, int]:
        """Remove users from achievement data who have left the server or are bots."""
        if not guild:
            return {"removed": 0, "kept": 0, "error": "No guild provided"}
        
        removed_count = 0
        kept_count = 0
        users_to_remove = []
        
        try:
            for user_id_str in self.user_data.keys():
                try:
                    user_id = int(user_id_str)
                    member = guild.get_member(user_id)
                    
                    # Check if user is no longer in the server or is a bot
                    if not member or member.bot:
                        users_to_remove.append(user_id_str)
                        removed_count += 1
                    else:
                        kept_count += 1
                        
                except ValueError:
                    # Invalid user ID format
                    users_to_remove.append(user_id_str)
                    removed_count += 1
                    
            # Remove the invalid users
            for user_id_str in users_to_remove:
                del self.user_data[user_id_str]
                logger.info(f"Removed achievement data for invalid user: {user_id_str}")
            
            # Save the cleaned data if any users were removed
            if removed_count > 0:
                self._save_user_data()
                logger.info(f"Achievement cleanup: Removed {removed_count} invalid users, kept {kept_count} valid users")
            
            return {
                "removed": removed_count,
                "kept": kept_count,
                "total_processed": removed_count + kept_count
            }
            
        except Exception as e:
            logger.error(f"Error during achievement cleanup: {e}")
            return {"removed": 0, "kept": 0, "error": str(e)}

# Global achievement system instance
achievement_system = AchievementSystem()

def check_message_achievements(user_id: int, message_count: int, level: int, hour: int, 
                              has_emoji: bool = False, has_exclamation: bool = False, 
                              has_question: bool = False, has_link: bool = False, 
                              has_attachment: bool = False, mention_count: int = 0):
    """Check achievements related to messaging."""
    stats = {
        "messages": message_count,
        "level": level,
        "early_message": 5 <= hour <= 7,
        "night_message": hour >= 23 or hour <= 3,
        "midnight_message": hour == 0,
        "morning_message": 6 <= hour <= 9,
        "afternoon_message": 12 <= hour <= 15,
        "evening_message": 18 <= hour <= 21,
        "emoji_messages": 1 if has_emoji else 0,
        "exclamation_messages": 1 if has_exclamation else 0,
        "question_messages": 1 if has_question else 0,
        "links_shared": 1 if has_link else 0,
        "attachments_sent": 1 if has_attachment else 0,
        "mentions_sent": mention_count
    }
    
    achievements_to_check = [
        "first_message", "chatty", "chatterbox", "conversation_master", 
        "mega_chatter", "legendary_speaker",
        "level_up", "level_10", "level_25", "level_50", "level_75", 
        "level_100", "level_150",
        "early_bird", "night_owl", "midnight_messenger",
        "morning_person", "afternoon_chatter", "evening_socializer",
        "emoji_user", "exclamation_enthusiast", "question_master",
        "link_sharer", "attachment_sender", "mention_master"
    ]
    
    newly_unlocked = []
    for achievement_id in achievements_to_check:
        if achievement_system.check_achievement(user_id, achievement_id, stats):
            newly_unlocked.append(achievement_system.achievements[achievement_id])
    
    return newly_unlocked

def check_gaming_achievements(user_id: int, game_stats: Dict[str, Any]):
    """Check achievements related to gaming."""
    achievements_to_check = [
        "first_tictactoe", "tictactoe_winner", "tictactoe_master",
        "blackjack_winner", "blackjack_master", "jackpot_winner", 
        "lucky_seven", "gaming_addict",
        "first_hangman", "hangman_winner", "hangman_master",
        "perfect_hangman", "hangman_speedster"
    ]
    
    newly_unlocked = []
    for achievement_id in achievements_to_check:
        if achievement_system.check_achievement(user_id, achievement_id, game_stats):
            newly_unlocked.append(achievement_system.achievements[achievement_id])
    
    return newly_unlocked

def check_social_achievements(user_id: int, social_stats: Dict[str, Any]):
    """Check achievements related to social interactions."""
    achievements_to_check = [
        "hugger", "super_hugger", "patter", "pat_master", "social_butterfly",
        "first_reaction", "reaction_enthusiast", "quick_responder", 
        "birthday_celebration", "mention_master"
    ]
    
    newly_unlocked = []
    for achievement_id in achievements_to_check:
        if achievement_system.check_achievement(user_id, achievement_id, social_stats):
            newly_unlocked.append(achievement_system.achievements[achievement_id])
    
    return newly_unlocked

def check_economy_achievements(user_id: int, economy_stats: Dict[str, Any]):
    """Check achievements related to economy."""
    achievements_to_check = [
        "first_purchase", "shopaholic", "big_spender", "whale", "millionaire"
    ]
    
    newly_unlocked = []
    for achievement_id in achievements_to_check:
        if achievement_system.check_achievement(user_id, achievement_id, economy_stats):
            newly_unlocked.append(achievement_system.achievements[achievement_id])
    
    return newly_unlocked

def check_counting_achievements(user_id: int, counting_stats: Dict[str, Any]):
    """Check achievements related to counting game."""
    achievements_to_check = [
        "counting_contributor", "counting_hero", "counting_legend",
        "perfectionist", "milestone_hunter"
    ]
    
    newly_unlocked = []
    for achievement_id in achievements_to_check:
        if achievement_system.check_achievement(user_id, achievement_id, counting_stats):
            newly_unlocked.append(achievement_system.achievements[achievement_id])
    
    return newly_unlocked

def check_command_achievements(user_id: int, command_stats: Dict[str, Any]):
    """Check achievements related to command usage."""
    achievements_to_check = [
        "pun_lover", "fortune_seeker", "animal_lover", "helper"
    ]
    
    newly_unlocked = []
    for achievement_id in achievements_to_check:
        if achievement_system.check_achievement(user_id, achievement_id, command_stats):
            newly_unlocked.append(achievement_system.achievements[achievement_id])
    
    return newly_unlocked

def check_time_achievements(user_id: int, time_stats: Dict[str, Any]):
    """Check achievements related to time and activity."""
    achievements_to_check = [
        "weekender", "daily_visitor", "dedication", "annual_member",
        "weekend_warrior", "monthly_visitor", "holiday_spirit",
        "early_riser", "late_night_regular", "weekday_warrior", 
        "seasonal_visitor", "hourly_chatter"
    ]
    
    newly_unlocked = []
    for achievement_id in achievements_to_check:
        if achievement_system.check_achievement(user_id, achievement_id, time_stats):
            newly_unlocked.append(achievement_system.achievements[achievement_id])
    
    return newly_unlocked

def check_milestone_achievements(user_id: int, milestone_stats: Dict[str, Any]):
    """Check achievements related to server milestones."""
    achievements_to_check = [
        "first_week", "first_month", "server_veteran", "og_member"
    ]
    
    newly_unlocked = []
    for achievement_id in achievements_to_check:
        if achievement_system.check_achievement(user_id, achievement_id, milestone_stats):
            newly_unlocked.append(achievement_system.achievements[achievement_id])
    
    return newly_unlocked

def check_special_achievements(user_id: int, special_stats: Dict[str, Any]):
    """Check achievements related to special behaviors."""
    achievements_to_check = [
        "emoji_enthusiast", "reaction_collector",
        "question_master", "caps_lock_warrior",
        "short_and_sweet", "novelist"
    ]
    
    newly_unlocked = []
    for achievement_id in achievements_to_check:
        if achievement_system.check_achievement(user_id, achievement_id, special_stats):
            newly_unlocked.append(achievement_system.achievements[achievement_id])
    
    return newly_unlocked

def check_milestone_achievements(user_id: int, milestone_stats: Dict[str, Any]):
    """Check achievements related to server milestones."""
    achievements_to_check = [
        "first_week", "first_month", "server_veteran", "og_member"
    ]
    
    newly_unlocked = []
    for achievement_id in achievements_to_check:
        if achievement_system.check_achievement(user_id, achievement_id, milestone_stats):
            newly_unlocked.append(achievement_system.achievements[achievement_id])
    
    return newly_unlocked

def save_jackpot_winner_to_file(username: str):
    """Save jackpot winner username to text file without Discord mentions."""
    try:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        winner_entry = f"[{timestamp}] {username}\n"
        
        with open("jackpot_winners.txt", "a", encoding="utf-8") as f:
            f.write(winner_entry)
        
        logger.info(f"Jackpot winner {username} saved to file at {timestamp}")
        
    except Exception as e:
        logger.error(f"Error saving jackpot winner to file: {e}")

def get_recent_jackpot_winners(limit: int = 10) -> List[str]:
    """Get recent jackpot winners from text file."""
    try:
        if not os.path.exists("jackpot_winners.txt"):
            return []
        
        with open("jackpot_winners.txt", "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        # Return the last 'limit' entries (most recent first)
        recent_winners = []
        for line in reversed(lines[-limit:]):
            line = line.strip()
            if line:
                recent_winners.append(line)
        
        return recent_winners
        
    except Exception as e:
        logger.error(f"Error reading jackpot winners from file: {e}")
        return []

def debug_check_time_achievements(user_id: int, guild_member=None):
    """Debug function to manually check and unlock time-based achievements."""
    if not guild_member:
        logger.warning(f"No guild member provided for user {user_id}")
        return []
    
    try:
        # Calculate days in server
        join_date = guild_member.joined_at
        if not join_date:
            logger.warning(f"No join date found for user {user_id}")
            return []
        
        now = datetime.datetime.now(datetime.timezone.utc)
        days_in_server = (now - join_date).days
        
        logger.info(f"Debug: User {user_id} has been in server for {days_in_server} days (joined: {join_date})")
        
        # Build time-based stats
        time_stats = {
            "days_in_server": days_in_server,
            "total_active_days": days_in_server,  # Assuming they were active
            "consecutive_days": min(days_in_server, 30),  # Cap at 30 for safety
            "weekend_messages": True if days_in_server >= 7 else False  # Assume they've sent weekend messages
        }
        
        # Time achievements to check
        time_achievement_ids = [
            "first_week",      # 7 days
            "first_month",     # 30 days  
            "server_veteran",  # 180 days
            "og_member",       # 365 days
            "annual_member",   # 365 days
            "daily_visitor",   # 7 consecutive days
            "dedication",      # 30 consecutive days
            "weekender"        # weekend messages
        ]
        
        newly_unlocked = []
        
        for achievement_id in time_achievement_ids:
            if achievement_id in achievement_system.achievements:
                logger.info(f"Debug: Checking {achievement_id} for user {user_id}")
                
                # Get current achievement status
                user_achievement = achievement_system.get_user_achievement(user_id, achievement_id)
                if user_achievement.unlocked:
                    logger.info(f"Debug: {achievement_id} already unlocked for user {user_id}")
                    continue
                
                # Force check the achievement
                if achievement_system.check_achievement(user_id, achievement_id, time_stats):
                    newly_unlocked.append(achievement_system.achievements[achievement_id])
                    logger.info(f"Debug: Successfully unlocked {achievement_id} for user {user_id}")
                else:
                    # Log why it didn't unlock
                    achievement = achievement_system.achievements[achievement_id]
                    logger.info(f"Debug: {achievement_id} requirements: {achievement.requirements}")
                    logger.info(f"Debug: User stats: {time_stats}")
                    
                    # Check each requirement
                    for req_key, req_value in achievement.requirements.items():
                        if req_key in time_stats:
                            current_value = time_stats[req_key]
                            if isinstance(req_value, bool):
                                meets_req = current_value == req_value
                            else:
                                meets_req = current_value >= req_value
                            logger.info(f"Debug: {req_key}: {current_value} >= {req_value} = {meets_req}")
                        else:
                            logger.info(f"Debug: {req_key} not found in stats")
        
        return newly_unlocked
        
    except Exception as e:
        logger.error(f"Error in debug_check_time_achievements: {e}")
        return []


async def send_achievement_notification(bot, user, achievement):
    """Send achievement notification to user and achievement channel."""
    logger.info(f"Attempting to send achievement notification for {user.display_name} - {achievement.name}")
    try:
        # Create achievement embed
        embed = discord.Embed(
            title="🏆 Achievement Unlocked!",
            description=f"**{achievement.name}**\n{achievement.description}",
            color=discord.Color.gold()
        )
        
        embed.set_author(
            name=f"{user.display_name}",
            icon_url=user.avatar.url if user.avatar else None
        )
        
        embed.add_field(
            name="Category",
            value=achievement.category.title(),
            inline=True
        )
        
        if achievement.reward_points > 0:
            embed.add_field(
                name="Reward",
                value=f"{achievement.reward_points * 10:,} contribution points (10x bonus!)",
                inline=True
            )
        
        if achievement.reward_role:
            embed.add_field(
                name="Role Reward",
                value=achievement.reward_role,
                inline=True
            )
        
        embed.set_footer(text=f"Achievement ID: {achievement.id}")
        
        # Try to send to user via DM
        try:
            await user.send(embed=embed)
            logger.info(f"Achievement notification sent to {user.display_name} via DM")
        except:
            logger.warning(f"Could not send DM to {user.display_name}")
        
        # Try to send to achievement channel
        try:
            # Get achievement channel ID from bot_utils config
            from bot_utils import BOT_CONFIG
            achievement_channel_id = BOT_CONFIG.get("ACHIEVEMENT_CHANNEL_ID", 1386270124029513728)
            logger.info(f"Looking for achievement channel with ID: {achievement_channel_id}")
            
            channel = bot.get_channel(achievement_channel_id)
            if channel:
                await channel.send(f"🎉 {user.mention} unlocked an achievement!", embed=embed)
                logger.info(f"Achievement notification sent to channel {achievement_channel_id} ({channel.name})")
            else:
                logger.error(f"Achievement channel {achievement_channel_id} not found. Bot may not have access to this channel.")
                # Try to find any channel the bot can send to as a fallback
                guild = None
                if hasattr(user, 'guild') and user.guild:
                    guild = user.guild
                elif bot.guilds:
                    guild = bot.guilds[0]  # Use first available guild
                
                if guild:
                    logger.info(f"Searching for alternative channel in guild: {guild.name}")
                    for test_channel in guild.text_channels:
                        if test_channel.permissions_for(guild.me).send_messages:
                            logger.info(f"Found fallback channel: {test_channel.name} ({test_channel.id})")
                            break
        except Exception as e:
            logger.error(f"Could not send to achievement channel: {e}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            
    except Exception as e:
        logger.error(f"Error sending achievement notification: {e}")


def debug_check_message_achievements(user_id: int, guild_member=None):
    """Debug function to check message-based achievements."""
    if not guild_member:
        return []
    
    try:
        # Simulate message stats for easy achievements
        message_stats = {
            "messages": 1,  # Assume they have at least 1 message
            "level": 1,     # Assume basic level
            "emoji_messages": 1,  # Assume they've used emojis
            "exclamation_messages": 1,  # Assume they've used exclamations
            "question_messages": 1,   # Assume they've asked questions
            "links_shared": 1,    # Assume they've shared links
            "attachments_sent": 1, # Assume they've sent attachments
            "mentions_sent": 1    # Assume they've mentioned someone
        }
        
        # Get current time for time-based checks
        hour = datetime.datetime.now().hour
        
        newly_unlocked = check_message_achievements(
            user_id, 
            message_stats["messages"], 
            message_stats["level"], 
            hour,
            has_emoji=True,
            has_exclamation=True, 
            has_question=True,
            has_link=True,
            has_attachment=True,
            mention_count=message_stats["mentions_sent"]
        )
        
        return newly_unlocked
        
    except Exception as e:
        logger.error(f"Error in debug_check_message_achievements: {e}")
        return []


def debug_check_social_achievements(user_id: int, guild_member=None):
    """Debug function to check social achievements."""
    if not guild_member:
        return []
    
    try:
        # Simulate social stats for easy achievements
        social_stats = {
            "reactions_added": 1,      # First reaction
            "quick_responses": 1,      # Quick responder
            "birthday_messages": 1,    # Birthday celebration
            "mentions_sent": 1,        # Mentions
            "hugs_given": 1,          # Basic social interaction
            "pats_given": 1           # Basic social interaction
        }
        
        newly_unlocked = check_social_achievements(user_id, social_stats)
        return newly_unlocked
        
    except Exception as e:
        logger.error(f"Error in debug_check_social_achievements: {e}")
        return []


def debug_check_milestone_achievements(user_id: int, guild_member=None):
    """Debug function to check milestone achievements."""
    if not guild_member:
        return []
    
    try:
        # Calculate actual days in server
        join_date = guild_member.joined_at
        if not join_date:
            return []
        
        now = datetime.datetime.now(datetime.timezone.utc)
        days_in_server = (now - join_date).days
        
        milestone_stats = {
            "days_in_server": days_in_server,
            "total_active_days": days_in_server  # Assume they were active
        }
        
        newly_unlocked = check_milestone_achievements(user_id, milestone_stats)
        return newly_unlocked
        
    except Exception as e:
        logger.error(f"Error in debug_check_milestone_achievements: {e}")
        return []


def debug_check_easy_achievements(user_id: int, guild_member=None):
    """Debug function to check easy-to-obtain achievements."""
    if not guild_member:
        return []
    
    try:
        # Current time info
        now = datetime.datetime.now()
        hour = now.hour
        weekday = now.weekday()  # 0=Monday, 6=Sunday
        month = now.month
        day = now.day
        
        # Easy achievement stats
        easy_stats = {
            # Time-based (current time)
            "morning_message": 6 <= hour <= 9,
            "afternoon_message": 12 <= hour <= 15, 
            "evening_message": 18 <= hour <= 21,
            "weekend_messages": weekday >= 5,  # Saturday or Sunday
            "holiday_message": (month == 1 and day == 1) or (month == 12 and day == 25),  # New Year or Christmas
            
            # Basic interaction stats
            "emoji_messages": 1,
            "reactions_added": 1,
            "quick_responses": 1,
            "links_shared": 1,
            "attachments_sent": 1,
            "mentions_sent": 1,
            "birthday_messages": 1,
            "exclamation_messages": 1
        }
        
        # Check multiple achievement categories for easy ones
        newly_unlocked = []
        
        # Check message achievements with easy stats
        newly_unlocked.extend(check_message_achievements(
            user_id, 1, 1, hour,
            has_emoji=easy_stats["emoji_messages"] > 0,
            has_exclamation=easy_stats["exclamation_messages"] > 0,
            has_link=easy_stats["links_shared"] > 0,
            has_attachment=easy_stats["attachments_sent"] > 0,
            mention_count=easy_stats["mentions_sent"]
        ))
        
        # Check social achievements with easy stats  
        newly_unlocked.extend(check_social_achievements(user_id, easy_stats))
        
        # Check time achievements with current time
        newly_unlocked.extend(check_time_achievements(user_id, easy_stats))
        
        return newly_unlocked
        
    except Exception as e:
        logger.error(f"Error in debug_check_easy_achievements: {e}")
        return []
