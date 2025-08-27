# 🌟 StarChan Bot - Complete Documentation

![](https://raw.githubusercontent.com/AlexandrosPanag/My_Discord_Projects/refs/heads/main/STAR/STAR.png)

# StarChan Discord Bot 

A feature-rich Discord bot with contribution system, achievements, games, and intelligent chatterbot functionality.

##  Features

### Core Systems
- **Contribution System** - Earn points through messages, reactions, and activities
- **Achievement System** - Unlock achievements with rewards and progress tracking
- **Level System** - Level up and unlock new roles and privileges
- **Interactive Shop** - Spend contribution points on roles and perks

### Games & Activities
- **Counting Game** - Collaborative counting with milestone rewards
- **Weekly Riddle Challenge** - Solve riddles for 3,000 contribution points
- **Rock Paper Scissors** - Play against the bot with contribution rewards
- **Coin Flip** - Simple gambling game with point wagering

### Advanced Features
- **Intelligent Chatterbot** - AI-powered conversations with gaming knowledge
- **Leaderboard System** - Track top contributors and achievers
- **Admin Tools** - Comprehensive moderation and management commands
- **Achievement Notifications** - Dedicated channel for achievement announcements

### Special Systems
- **Star Contributor Boost** - 2x contribution points for special role holders (weekly reset)
- **Memory System** - Bot remembers user preferences and conversation history
- **Content Filtering** - Safe, non-political conversations
- **Owner-Only Features** - Exclusive chatterbot access for bot owner

##  Prerequisites

- Python 3.8 or higher
- Discord.py library
- A Discord Bot Token
- Discord Server with proper permissions

##  Installation & Setup

### 1. Clone/Download the Repository
`ash
git clone [your-repo-url]
cd StarChan
`

### 2. Install Required Dependencies
`ash
pip install discord.py
pip install aiofiles
`

### 3. Get Your Discord IDs

Enable Developer Mode in Discord:
1. Go to Discord Settings  Advanced  Enable "Developer Mode"
2. Right-click on servers, channels, or users to copy their IDs

### 4. Configure the Bot

**Important:** Before running the bot, you must replace all placeholder IDs with your actual Discord IDs.

#### Required Configuration in ot_utils.py:
`python
BOT_CONFIG = {
    "MAIN_SERVER_IDS": {YOUR_SERVER_ID, ANOTHER_SERVER_ID},
    "main_server_id": YOUR_PRIMARY_SERVER_ID,
    "FORBIDDEN_CHANNEL_IDS": [
        YOUR_RULES_CHANNEL_ID,  # Channels where bot shouldn't post
        ANOTHER_FORBIDDEN_CHANNEL_ID
    ],
    "FORCED_LEVELUP_CHANNEL_ID": YOUR_LEVELUP_CHANNEL_ID,
    "ACHIEVEMENT_CHANNEL_ID": YOUR_ACHIEVEMENT_CHANNEL_ID,
    "BOT_OWNER_ID": YOUR_DISCORD_USER_ID,
    "owner_id": YOUR_DISCORD_USER_ID,
}
`

#### Required Configuration in pp.py:
`python
MAIN_SERVER_IDS = [YOUR_SERVER_ID]
BOT_CONFIG = {
    "main_server_id": YOUR_PRIMARY_SERVER_ID,
    "owner_id": YOUR_DISCORD_USER_ID,
}
`

#### Update Hardcoded Channel IDs:
Search for 
