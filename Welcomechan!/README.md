# Welcomechan! Project


👋 Invite me here: https://discord.com/oauth2/authorize?client_id=1365308829440671935

### **🌟 WelcomeChan! — The Digital Spirit of Hospitality**  

<img src="https://github.com/AlexandrosPanag/My_Discord_Projects/blob/main/Welcomechan!/Welcomechan!.png?raw=true" alt="drawing" width="120"/>
<img src="github.com/AlexandrosPanag/My_Discord_Projects/blob/main/Welcomechan!/welcomechan2.png?raw=true" alt="drawing" width="120"/>

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


### DOCUMENTATION

# WelcomeChan Discord Bot Documentation

WelcomeChan is a feature-rich, easy-to-use Discord bot for community fun, moderation, and D&D-style party management. Below you'll find a summary of all commands, features, and usage examples.

---

## 📝 **General Commands**

| Command                | Description                                               | Example Usage                |
|------------------------|----------------------------------------------------------|------------------------------|
| `!hi`                  | Greet the bot and get a friendly reply                   | `!hi`                        |
| `!cat`                 | Sends a random cat gif                                   | `!cat`                       |
| `!pun`                 | Get a random pun                                         | `!pun`                       |
| `!bonk [@user]`        | Bonk a user with a funny gif                             | `!bonk @alex`                |
| `!pat @user`           | Pat a user with a wholesome gif                          | `!pat @alex`                 |
| `!easteregg`           | Sends a fun computer history easter egg                  | `!easteregg`                 |
| `!credits`             | Show bot credits                                         | `!credits`                   |

---

## 🧹 **Moderation Commands**

| Command                                 | Description                                  | Example Usage                |
|------------------------------------------|----------------------------------------------|------------------------------|
| `!purge <n>`                            | Delete up to 999 messages                    | `!purge 10`                  |
| `!kick @user [reason]`                  | Kick a user from the server                  | `!kick @alex spam`           |
| `!modpost <channel_id> <message>`       | Post a message as the bot in any channel     | `!modpost 1234567890 Hello!` |
| `!sethibye`                             | Set current channel for join/leave messages  | `!sethibye`                  |

---

## 🔢 **Counting Game**

| Command                | Description                                               | Example Usage                |
|------------------------|----------------------------------------------------------|------------------------------|
| `!counting`            | Start the counting game in the current channel           | `!counting`                  |
| `!skipcount <n>`       | Skip the counting to a specific number                   | `!skipcount 20`              |

---

## 🧮 **Calculator**

| Command                | Description                                               | Example Usage                |
|------------------------|----------------------------------------------------------|------------------------------|
| `!calcadd a b`         | Add two numbers                                          | `!calcadd 2 3`               |
| `!calcsub a b`         | Subtract two numbers                                     | `!calcsub 5 2`               |
| `!calcmul a b`         | Multiply two numbers                                     | `!calcmul 4 3`               |
| `!calcdiv a b`         | Divide two numbers                                       | `!calcdiv 10 2`              |

---

## 🎲 **Dice Rolling**

| Command                | Description                                               | Example Usage                |
|------------------------|----------------------------------------------------------|------------------------------|
| `!d4`                  | Roll a 4-sided dice                                      | `!d4`                        |
| `!d6`                  | Roll a 6-sided dice                                      | `!d6`                        |
| `!d8`                  | Roll an 8-sided dice                                     | `!d8`                        |
| `!d10`                 | Roll a 10-sided dice                                     | `!d10`                       |
| `!d20`                 | Roll a 20-sided dice                                     | `!d20`                       |
| `!doubledice`          | Roll two 6-sided dice                                    | `!doubledice`                |

---

## 🛡️ **D&D Party Management**

| Command                                 | Description                                  | Example Usage                |
|------------------------------------------|----------------------------------------------|------------------------------|
| `!partycreate @user STR DEX CON INT WIS CHA HP AC INIT` | Add a party member with stats | `!partycreate @alex 8 12 14 20 14 16 140 2 1` |
| `!partyshow`                            | Show all party members and stats             | `!partyshow`                 |
| `!partyremove @user`                    | Remove a party member                        | `!partyremove @alex`         |
| `!partystats @user`                     | Show stats for a party member                | `!partystats @alex`          |
| `!partyheal @user <amt>`                | Heal a party member                          | `!partyheal @alex 10`        |
| `!healall`                              | Fully heal all party members                 | `!healall`                   |
| `!partylevelup @user`                   | Level up a party member                      | `!partylevelup @alex`        |
| `!flee @user1 @user2 ...`               | Attempt to flee the encounter                | `!flee @alex @bob`           |

---

## 👾 **Monsters**

| Command                                 | Description                                  | Example Usage                |
|------------------------------------------|----------------------------------------------|------------------------------|
| `!dndmonster <type> <amt>`              | Create monsters                              | `!dndmonster goblin 3`       |
| `!monstershow`                          | Show all active monsters                     | `!monstershow`               |
| `!monstersattack <type> <amt> @users`   | Monsters attack party members                | `!monstersattack goblin 2 @alex @bob` |
| `!dndmdefeated <type> <num>`            | Mark monsters as defeated                    | `!dndmdefeated goblin 1`     |
| `!helpmonsters`                         | Show all available monsters and stats        | `!helpmonsters`              |

---

## 🐉 **Bosses**

| Command                                 | Description                                  | Example Usage                |
|------------------------------------------|----------------------------------------------|------------------------------|
| `!bosses`                               | Show all available bosses and stats          | `!bosses`                    |
| `!bosscreate <boss> <amt>`              | Create bosses                                | `!bosscreate kraken 1`       |
| `!bossshow`                             | Show all active bosses                       | `!bossshow`                  |
| `!bossesattack <boss> <amt> @users`     | Bosses attack party members                  | `!bossesattack kraken 1 @alex @bob` |
| `!helpbosses`                           | Show all available bosses and stats          | `!helpbosses`                |

---

## ℹ️ **Other**

- Use `!helpwc`, `!helpwelcomechan`, `!helpchan`, or `!welpwchan` to see this help message in Discord.
- For D&D initiative, use: `!dndbegin @user1 roll1 ...`
- For monster and boss stats, use: `!helpmonsters` or `!helpbosses`.

---

## 🛠️ **Setup & Persistence**

- **Join/Leave Channel:** Use `!sethibye` in your desired channel. The bot will remember this channel even after restarts.
- **Counting Game:** Use `!counting` to start the counting game in a channel. Progress is saved automatically.
- **Party, Monsters, Bosses:** All stats and creations are saved to disk and persist through bot restarts.

---

## 👤 **Credits**

Bot made by [@alexandrospanag](https://github.com/alexandrospanag)

---

Enjoy using WelcomeChan! 🎉

For help, use `!helpwelcomechan` in your server!

