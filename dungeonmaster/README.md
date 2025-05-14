# DungeonMaster Discord Bot Documentation

DungeonMaster is a Discord bot designed to help you run tabletop RPG sessions, manage parties, roll dice, and create monsters—all from your server!

---

## 🎲 Dice Roll Commands

| Command      | Description                |
|--------------|---------------------------|
| `!d4`        | Roll a 4-sided die        |
| `!d6`        | Roll a 6-sided die        |
| `!d8`        | Roll an 8-sided die       |
| `!d10`       | Roll a 10-sided die       |
| `!d12`       | Roll a 12-sided die       |
| `!d20`       | Roll a 20-sided die       |
| `!d100`      | Roll a 100-sided die      |

---

## 🧑‍🤝‍🧑 Party Management

| Command                                              | Description                                               |
|------------------------------------------------------|-----------------------------------------------------------|
| `!createparty @user1 @user2 ...`                     | Import party from character `.txt` files                  |
| `!removeparty @user`                                 | Remove a member from the party                            |
| `!modifyparty @user <new character info>`            | Modify a member's character in the party                  |
| `!activeparty`                                       | Show all current party members and their stats (with emojis) |

**Character files:**  
Each party member should have a file named `<user_id>.txt` with lines like:  
```
Strength: 15
Dexterity: 12
Constitution: 14
Intelligence: 10
Wisdom: 13
Charisma: 8
```

---

## 👹 Monster Database

| Command                                              | Description                                               |
|------------------------------------------------------|-----------------------------------------------------------|
| `!createmonster <name> <stats>`                      | Add a monster (e.g. `!createmonster Goblin HP:7 ATK:2 DEF:1`) |
| `!showmonsters`                                      | Display all monsters in the database                      |
| `!monsterattack <name>`                              | Simulate a monster attack (with miss/crit chance)         |

---

## 📜 Other Commands

| Command                | Description                                  |
|------------------------|----------------------------------------------|
| `!license`             | Show bot license info                        |
| `!helpdungeonmaster`   | Show this help message                       |

---

## 📝 License

This bot is licensed under the [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) license.  
You are free to share and adapt the bot for non-commercial purposes, as long as you give appropriate credit and share alike.  
For commercial use or to purchase rights, contact the author via GitHub: **@alexandrospanag**

---

## 🛠️ Getting Started

1. Invite the bot to your Discord server.
2. Use `!helpdungeonmaster` to see all commands.
3. Prepare character `.txt` files for your party members.
4. Create monsters and manage your party with simple commands!

---

Enjoy your adventures!
