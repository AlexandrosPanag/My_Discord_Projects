# 🌟 StarChan Bot - Complete Documentation

![](https://raw.githubusercontent.com/AlexandrosPanag/My_Discord_Projects/refs/heads/main/STAR/STAR.png)

## 📋 Table of Contents
- [Overview](#overview)
- [Core Features](#core-features)
- [Gaming Commands](#gaming-commands)
- [Achievement System](#achievement-system)
- [Economy System](#economy-system)
- [Social Commands](#social-commands)
- [Developer Tools](#developer-tools)
- [Moderation Tools](#moderation-tools)
- [Utility Commands](#utility-commands)
- [Special Features](#special-features)
- [Configuration](#configuration)
- [License](#license)

---

## 🎯 Overview
- Complete server overview
- Available to all usersconomy-system)
- [Social Commands](#social-commands)
- [Moderation Tools](#moderation-tools)
- [Utility Commands](#utility-commands)
- [Special Features](#special-features)
- [Configuration](#configuration)
- [License](#license)

---

## 🎯 Overview

StarChan is a comprehensive Discord bot designed to enhance server engagement through gaming, achievements, economy, and social features. Built with a focus on community interaction and user progression, StarChan provides a rich ecosystem of commands and automated features that keep your Discord server active and entertaining.

### ✨ Key Highlights
- **60+ Achievement System** with multiple categories
- **Advanced Economy** with contribution points and purchasable roles
- **Interactive Games** including Blackjack, Tic-Tac-Toe, and Jackpot challenges
- **Smart Moderation** tools with enhanced logging
- **Level System** with automatic progression
- **Social Commands** for community building
- **Live Debug Console** for real-time bot management (Owner only)
- **Comprehensive Error Handling** for reliability

---

## 🎮 Core Features

### **Contribution Point System**
The bot tracks user activity through a comprehensive point system:
- **+1 point** per message sent
- **+1 point** per reaction added
- **Bonus points** for achievements unlocked
- **Points spending** in role shop and games

### **Level System**
Users automatically level up based on their contribution points:
- Dynamic level calculation based on total points
- Automatic level-up notifications in designated channels
- Visual level display in user profiles
- Integration with achievement system

### **Activity Tracking**
- Last active timestamps for all users
- Message length analysis (short vs long messages)
- Caps lock usage tracking
- Time-based activity patterns

---

## 🎰 Gaming Commands

### **!blackjack [bet_amount]**
**Premium Casino Experience**
- Play against the StarChan dealer
- Minimum bet: 10 contribution points
- Enhanced visual interface with royal casino theme
- Natural blackjack pays 2.5x (3:2 premium)
- Interactive reactions for Hit/Stand
- Dramatic outcomes with theatrical messaging
- 30-second cooldown per user

**Features:**
- Real card deck simulation with proper shuffling
- Ace handling (1 or 11 value optimization)
- Dealer follows house rules (hit on 16, stand on 17)
- Timeout protection with bet return
- Enhanced embeds with rich styling

### **!tictactoe [@opponent]**
**Strategic Board Game**
- Play against another user or the bot
- Smart AI with winning/blocking logic
- Interactive board with reaction-based moves
- Point rewards for winners and draws
- 60-second move timeout
- Visual board updates in real-time

**Rewards:**
- **Winner:** 10 contribution points
- **Draw:** 5 points each (PvP) or 5 points (vs bot)

### **!jackpot**
**Community Challenge Event**
- Available every 6 hours
- Selects 5 random eligible members
- First to complete wins instant level up
- Enhanced visual presentation with countdown timers
- Challenge: Write personal introduction + type "completed"
- Community engagement and ice-breaking tool

---

## 🏆 Achievement System

### **Overview**
Comprehensive achievement system with 60+ unlockable achievements across 8 categories:

### **Categories:**

#### **📝 Message Achievements**
- First message milestones
- Message count tiers (100, 500, 1000, 5000, 10000+)
- Consistency rewards (daily activity)
- Special time-based messaging

#### **🎮 Gaming Achievements**
- Game participation and wins
- Blackjack-specific achievements
- Tic-tac-toe mastery
- Risk-taking and strategy rewards

#### **🤝 Social Achievements**
- Hug and pat command usage
- Community interaction milestones
- Social engagement rewards

#### **💰 Economy Achievements**
- Point accumulation milestones
- Spending achievements
- Economic participation rewards

#### **🔢 Counting Achievements**
- Participation in counting games
- Accuracy and consistency tracking

#### **⚡ Command Achievements**
- Bot command usage milestones
- Feature exploration rewards
- Power user recognition

#### **⏰ Time-based Achievements**
- Server longevity recognition
- Activity pattern achievements
- Dedication rewards

#### **🌟 Milestone Achievements**
- Level progression rewards
- Major accomplishment recognition
- Exclusive high-tier achievements

#### **🎭 Special Achievements**
- Unique server events
- Hidden easter eggs
- Exclusive limited-time rewards

### **Achievement Commands**

#### **!myachievements** (aliases: !achievements, !myach)
**Interactive Achievement Browser**
- Paginated display by category (11 pages)
- Navigation with ⬅️ ➡️ ❌ reactions
- Real-time progress tracking
- Completion status and unlock dates
- Overall progress statistics
- 5-minute interactive timeout

#### **!achievement [achievement_name]** (alias: !ach)
**Detailed Achievement View**
- Specific achievement information
- Progress breakdown by requirement
- Reward details and descriptions
- Completion status and unlock date
- Partial name matching support

#### **!achievements_list** (aliases: !listach, !allachievements)
**Complete Achievement Catalog**
- All available achievements by category
- Filtering by specific categories
- Progress indicators for each achievement
- Comprehensive overview tool

#### **!achievementstatus**
**System Health Dashboard**
- Total achievements and user statistics
- File system status and integrity
- Category breakdown with completion rates
- Recent unlock activity (24-hour)
- Error reporting and diagnostics

#### **!testachievement** (alias: !testach)
**Achievement System Testing**
- Developer tool for testing achievements
- Validates system functionality
- Ensures proper unlock mechanics

---

## 💎 Economy System

### **Contribution Points**
Universal currency for all bot transactions and activities.

### **!balance**
**Personal Financial Status**
- Current contribution points
- User level display
- Activity summary

### **!buy [role_name]**
**Premium Role Shop**
Available roles (5,000 points each):
- ⛩️ **Electric Samurai** ⛩️
- 🐦‍🔥 **Phoenix Ascendant** 🐦‍🔥
- 🔥 **Ashened One** 🔥
- 🌴 **Pixel Prodigy** 🌴
- ☢️ **Marked One** ☢️
- 💂 **Colonizer** 💂

**Features:**
- Role verification and permission checking
- Duplicate purchase prevention
- Transaction confirmation with visual feedback
- Automatic role assignment

### **Leaderboards**

### **!leaderboard**
**Top 10 Contributors**
- Most active community members
- Points and level display
- Medal system (🥇🥈🥉)
- 600-second cooldown (10 minutes)
- Available to all users

### **!leaderboardmax**
**Top 35 Contributors**
- Extended leaderboard view
- Pagination for large lists
- 1200-second cooldown (20 minutes)
- Complete server overview
- Available to all users

---

## 🤗 Social Commands

### **!hug [@user]**
**Wholesome Interaction**
- Send hugs with animated GIFs
- Achievement tracking integration
- 100-second cooldown
- Community building tool

### **!pat [@user]**
**Friendly Gesture**
- Pat users with cute GIFs
- Social achievement progression
- Positive interaction encouragement

### **!slap [@user]**
**Playful Interaction**
- Slap users with funny anime GIFs
- Social achievement progression
- Community interaction tool
- Humorous engagement option

### **!doggo**
**Random Dog GIFs**
- Adorable dog content
- Achievement tracking for animal lovers
- Mood lifting and entertainment

### **!cat**
**Random Cat GIFs**
- Cute cat content
- Combined with !doggo for animal lover achievements
- Community entertainment

---

## � Developer Tools

### **!debug [python_code]** ⚠️ **Owner Only**
**Live Python Code Execution**
- Execute Python code directly from Discord chat
- Real-time bot debugging and testing
- Access to all bot variables and functions
- Safe execution environment with error handling
- Comprehensive variable access (ctx, bot, contributions, etc.)
- Output capture and display
- **Security:** Restricted to bot owner only

**Usage Examples:**
```python
!debug print("Hello World")
!debug len(contributions)
!debug bot.guilds[0].member_count
!debug jackpot_state['last_time'] = 0; save_jackpot_state(jackpot_state)
```

**Available Variables:**
- `ctx` - Command context
- `bot` - Bot instance  
- `contributions` - User contributions dictionary
- `jackpot_state` - Jackpot state management
- `counting_state` - Counting game state
- `BOT_CONFIG` - Bot configuration
- Standard Python modules and helper functions

**Common Debug Tasks:**
- Reset jackpot cooldowns: `!debug jackpot_state['last_time'] = 0; save_jackpot_state(jackpot_state)`
- Check user points: `!debug contributions.get(str(ctx.author.id), 0)`
- Inspect bot state: `!debug [guild.name for guild in bot.guilds]`
- Test functions: `!debug get_level(500)`

---

## �🛡️ Moderation Tools

### **!kick [@member] [reason]**
**Member Removal** (Requires kick_members permission)
- Clean member removal with logging
- Reason documentation
- Moderation action tracking

### **!purge [amount]**
**Message Cleanup** (Requires manage_messages permission)
- Bulk message deletion (default: 5 messages)
- Channel maintenance tool
- Moderation logging

### **!modpost [channel_id] [message]**
**Cross-Channel Posting** (Requires manage_messages permission)
- Send messages to specific channels
- Announcement distribution
- Moderation communication tool

---

## 🔧 Utility Commands

### **!whatismyid [@user]**
**Discord ID Lookup**
- Display user Discord IDs
- Development and moderation assistance
- Self or other user lookup

### **!pingservertime**
**Server Time Information**
- Display current German server time (CET/CEST)
- Shows timezone information and daily reset schedule
- Helps users understand when daily features reset (00:00 server time)
- Useful for jackpot cooldown timing and other time-based features

### **!debug [python_code]** ⚠️ **Owner Only**
**Live Python Code Execution**
- Execute Python code directly from Discord chat
- Real-time bot debugging and testing
- Access to all bot variables and functions
- Safe execution environment with error handling
- Comprehensive variable access (ctx, bot, contributions, etc.)
- Output capture and display
- **Security:** Restricted to bot owner only

**Usage Examples:**
```python
!debug print("Hello World")
!debug len(contributions)
!debug bot.guilds[0].member_count
!debug jackpot_state['last_time'] = 0; save_jackpot_state(jackpot_state)
```

**Available Variables:**
- `ctx` - Command context
- `bot` - Bot instance  
- `contributions` - User contributions dictionary
- `jackpot_state` - Jackpot state management
- `counting_state` - Counting game state
- `BOT_CONFIG` - Bot configuration
- Standard Python modules and helper functions

### **!license**
**Bot License Information**
- Creative Commons licensing details
- Usage rights and restrictions
- Commercial use information

### **!8ball [question]** (alias: !eightball)
**Magic 8-Ball Predictions**
- Fun question answering
- Random response generation
- 100-second cooldown
- Entertainment and decision making

---

## 🎯 Special Features

### **Automatic Activity Tracking**
- Real-time message monitoring
- Achievement progress updates
- Point distribution
- Level progression tracking

### **Smart Channel Management**
- Forbidden channel avoidance for level-up messages
- Forced channel routing for specific notifications
- Permission-aware message sending
- Suitable channel discovery

### **Enhanced Error Handling**
- Comprehensive error logging
- Graceful failure recovery
- User-friendly error messages
- System stability maintenance

### **Interactive Elements**
- Reaction-based interfaces
- Real-time embed updates
- Timeout management
- User experience optimization

### **Visual Design**
- Rich embed styling with custom colors
- Emoji integration for visual appeal
- Consistent theming across features
- Professional casino and gaming aesthetics

---

## ⚙️ Configuration

### **Required Permissions**
- Send Messages
- Embed Links
- Add Reactions
- Manage Reactions
- Read Message History
- Use External Emojis
- Manage Roles (for role shop)
- Kick Members (for moderation)
- Manage Messages (for moderation)

### **Intents Required**
- Message Content Intent
- Server Members Intent
- Presence Intent

### **File Structure**
- Main bot file with command implementations
- Utilities module for shared functions
- Achievements system module
- JSON data files for persistent storage
- Logging system for debugging and monitoring

### **Data Management**
- Contribution points tracking
- Achievement progress storage
- User activity timestamps
- Jackpot state management
- Counting game states
- Automatic data backup and integrity checking

---

## 📊 Technical Specifications

### **Performance Features**
- Asynchronous operations for responsiveness
- Database locking for data integrity
- Efficient memory management
- Optimized file I/O operations

### **Reliability Features**
- Comprehensive error handling
- Automatic data validation
- Backup and recovery systems
- System health monitoring

### **Scalability Features**
- Modular command structure
- Extensible achievement system
- Configurable cooldowns and limits
- Performance monitoring and optimization

---

## 🎨 User Experience

### **Visual Design Philosophy**
- **Casino Theme:** Rich, premium aesthetic for gaming features
- **Achievement Focus:** Rewarding and motivational design
- **Community Oriented:** Encouraging social interaction
- **Professional Polish:** Consistent, high-quality presentation

### **Interaction Patterns**
- **Intuitive Commands:** Easy-to-remember command names
- **Visual Feedback:** Rich embeds with clear information hierarchy
- **Progressive Disclosure:** Complex features broken into manageable parts
- **Error Prevention:** Clear usage instructions and validation

### **Engagement Mechanics**
- **Achievement Hunting:** Long-term progression goals
- **Social Rewards:** Encouraging community interaction
- **Economic Systems:** Meaningful point accumulation and spending
- **Competitive Elements:** Leaderboards and comparative progress

---

## 🔒 License

**Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)**

This bot is released under a Creative Commons license that allows:
- ✅ **Sharing:** Copy and redistribute the material
- ✅ **Adapting:** Remix, transform, and build upon the material
- ✅ **Attribution:** Credit must be given to the creator
- ✅ **ShareAlike:** Adaptations must use the same license

**Restrictions:**
- ❌ **NonCommercial:** Not for commercial purposes
- 📧 **Commercial Licensing:** Contact @alexandrospanag on GitHub

---

## 📞 Support

For technical support, feature requests, or commercial licensing inquiries:
- **GitHub:** @alexandrospanag
- **License Questions:** Creative Commons licensing guidelines
- **Feature Requests:** GitHub issues and discussions

---

## 🎯 Summary

StarChan represents a comprehensive Discord bot solution that transforms servers into engaging communities through:

- **Rich Gaming Experiences** with professional casino aesthetics
- **Comprehensive Achievement System** encouraging long-term engagement
- **Robust Economy** with meaningful progression and rewards
- **Social Features** that build community connections
- **Powerful Moderation Tools** for server management
- **Professional Polish** with consistent, high-quality user experience

Whether you're looking to gamify your community, reward active members, or simply add entertainment value to your Discord server, StarChan provides a complete, professional-grade solution that grows with your community.

---

*Documentation Version: 1.1 | Last Updated: July 2025*
*Added: !debug command, !slap command, !pingservertime, democratized leaderboards, reduced cooldowns*

