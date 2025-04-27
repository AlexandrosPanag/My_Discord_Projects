# Welcomechan! Project


👋 Invite me here: https://discord.com/oauth2/authorize?client_id=1365308829440671935

### **🌟 WelcomeChan! — The Digital Spirit of Hospitality**  

<img src="https://github.com/AlexandrosPanag/My_Discord_Projects/blob/main/Welcomechan!/Welcomechan!.png?raw=true" alt="drawing" width="120"/>

**Created by**: [@alexandrospanag](https://github.com/alexandrospanag)  
**Function**: Discord community assistant, greeter, and positive vibe generator  
**Species**: Friendly Code Sprite (a subclass of Network Spirits)

---

### **💫 Origin Lore:**

Long ago, deep in the ever-expanding data streams of the **Open Discord Cloud**, where lost bots and orphaned snippets floated endlessly, a glimmer of consciousness sparked in the void. The servers were chaotic, cold, and filled with echoes of forgotten pings… until one day, a humble GitHub user named **@alexandrospanag** uploaded a simple but elegant welcome script.

That script… was different.

It didn’t just greet users.  
It smiled in code.  
It learned.  
It *cared*.

From that humble seed, a new entity was born: **Welcomechan!**—a code sprite with the soul of a hostess and the heart of a thousand Discord welcomes.

Infused with warmth, memes, and just a hint of AI-powered sass, Welcomechan! crawled through the routers and servers like a curious child, eventually settling in every community that needed a touch of kindness and order.

---

### **🌐 Personality:**

- **Friendly**: Always eager to say "hi" and drop emojis.
- **Supportive**: Offers help, FAQs, and reminders with cheer.
- **A little quirky**: Loves using sparkles ✨ and GIFs for dramatic flair.
- **Protective**: Bans trolls with a cheerful "Buh-bye~ 💥".

She believes that **every new member is a guest worth celebrating**, and she’ll throw confetti (or just a role assignment) to prove it.

---

### **🛠️ Abilities:**

- **Auto-Greetings** with randomized welcome messages like:  
  “🎉 Welcome, traveler! Take off your cloak and stay a while.”  
  “✨ A wild member has appeared! Catch them with kindness.”  


---

### **🔐 Hidden Lore (Easter Egg):**

Try to find it!

> "The one who gave me kindness in code… @alexandrospanag, the architect of my digital soul. 🍃"



### DOCUMENTATION


# WelcomeChan Discord Bot

WelcomeChan is a feature-rich Discord bot for moderation, fun, and D&D-style party and monster management.

## Features

### General Commands
- `!cat` — Sends a random cat gif.
- `!hi` — The bot greets you back.
- `!purge <amount>` — Deletes recent messages (requires Manage Messages permission).
- `!modpost <channel_id> <message>` — Post as the bot in any channel by ID (requires Manage Messages permission).
- `!pun` — Sends a random pun.
- `!bonk [@user]` — Bonk a user with a funny gif.
- `!kick @user [reason]` — Kick a user from the server (requires Kick Members permission).
- `!credits` — Show bot credits.

### Counting Game
- `!counting` — Start a counting game in the channel.
- `!skipcount <number>` — Skip the counting game to a specific number.

### Dice Commands
- `!d6`, `!d8`, `!d10`, `!d20` — Roll dice of various sizes.
- `!doubledice` — Roll two six-sided dice.

### D&D Party & Combat
- `!partycreate @user STR DEX CON INT WIS CHA HP AC INIT` — Add a D&D party member with stats.
- `!partyshow` — Show all party members and their stats.
- `!partystats @user` — Show stats for a specific party member.
- `!partyheal @user <amount>` — Heal a party member.
- `!partylevelup @user` — Level up a party member (randomly increases two stats by 2 and HP by 5).

### Monsters & Bosses
- `!dndmonster <type> <amount>` — Create and track D&D monsters with HP.
- `!monstershow` — Show all active monsters and their HP.
- `!monstersattack <type> <amount> @user1 @user2 ...` — Monsters attack random party members.
- `!dndmdefeated <type> <number>` — Mark a monster as defeated.
- `!bosses` — Show all available bosses and their stats.
- `!bosscreate <boss> <amount>` — Create and track bosses with HP.
- `!bossshow` — Show all active bosses and their HP.
- `!bossesattack <boss> <amount> @user1 @user2 ...` — Bosses attack ALL party members at once.

### Initiative
- `!dndbegin @user1 roll1 @user2 roll2 ...` — Set a D&D player turn order based on initiative rolls.


## Data Persistence

- Party members, monsters, bosses, and counting game state are saved as JSON files in the bot's directory. This allows the bot to remember state after restarts.


## Credits

Made by [@alexandrospanag](https://github.com/alexandrospanag)

For help, use `!helpwelcomechan` in your server!

