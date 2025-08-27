# 🌟 StarChan Bot – Complete Documentation

![StarChan Logo](https://raw.githubusercontent.com/AlexandrosPanag/My_Discord_Projects/refs/heads/main/STAR/STAR.png)

A feature-rich Discord bot with contribution system, achievements, games, and intelligent chatterbot functionality.

---
# StarChan Discord Bot

StarChan is a **feature-packed, experimental AI-powered Discord bot** designed for **community engagement, interactive games, and gamified contribution systems** — all with an integrated shop, achievements, and a text-based Discord terminal.

## 🚀 Features

### 🤖 AI & Experimental Systems
- **ChatterBot Integration**: AI conversational module for dynamic and context-aware responses.
- **Smart Achievement Tracking**: Automatic detection of user actions to unlock rewards.
- **Leveling System**: XP-based progression using an advanced formula for smooth scaling.
- **Economy Achievements**: Detects spending, earning milestones, and awards bonuses.

### 🎮 Games & Fun Commands
- **Blackjack Royale** – High-stakes card game with:
  - Custom casino-style embeds
  - Variable payouts (including Blackjack 3:2)
  - Special role awards for extreme wins (e.g., 🎲 *Gambler* role)
- **8-Ball, Puns, Roasts, Praises, Dad Jokes** – Community-driven fun.
- **Weekly Riddles** – Solve brain teasers for rewards.
- **Reaction-based Mini-Games** – Interactive play through Discord emoji reactions.

### 🏆 Achievements & Rewards
- **Role Shop** – Buy cosmetic roles with earned points.
- **Special Titles** – Legendary, Epic, Rare, Common, and Starter tier roles.
- **Milestone Bonuses** – Contribution and counting streak achievements.
- **Exclusive Roles** – e.g., 🎲 *Gambler* for high-stakes blackjack winners.

### 💬 Discord Terminal
- Command prefix: `!`
- Fully text-driven interactive experience.
- In-terminal economy management, role purchases, and mini-games.
- Rich embed styling for immersive command responses.

### 🛠️ Moderation & Permissions
- **VIP System** – Special perks for premium supporters.
- **Developer Commands** – Locked to bot owner or specific roles.
- **Channel Restrictions** – Prevent bot activity in forbidden channels.

---

## 📦 Installation

**Requirements:**
- Python 3.9+
- [discord.py](https://github.com/Rapptz/discord.py) (with Intents enabled)
- `requests`, `asyncio`, and standard library dependencies.

**Setup:**
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/starchan-bot.git
   cd starchan-bot

2. Install dependencies:

pip install -r requirements.txt

---
### Configure your bot:

Update BOT_CONFIG values in app.py and bot_utils.py with your Discord bot token, server IDs, and channel IDs.

---
###
Run the bot:

python app.py

---
# ⚙️ Configuration

The bot uses a central BOT_CONFIG dictionary for IDs, role prices, and feature toggles.

Main Configurable Files:

app.py – Core bot logic, games, achievements, AI chat.

bot_utils.py – Utility functions, role/shop definitions, riddles, and game content.

---
## 🧠 AI Experimental Notes

ChatterBot: The AI chat backend is modular, meaning you can replace or extend it with GPT-based APIs.

Command Cooldowns: Implemented to prevent spam and encourage fair play.

Achievement Logic: Real-time checks for gaming, economy, and social milestones.

---
## 📜 License

This project is licensed under the Attribution-NonCommercial-ShareAlike 4.0 International License – see the LICENSE.md
 file for details: https://github.com/AlexandrosPanag/My_Discord_Projects/blob/main/LEARN.md


---
## 🤖 New AI features

## 🤖Additional Discord terminal commands

More achievements or games
Feel free to open an issue or PR.
