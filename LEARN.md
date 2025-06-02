# Learn.md – Learning with My Discord Bot Projects

Welcome to the **Learn.md** guide for this repository!  
Here you’ll find explanations, tips, and learning resources to help you understand, use, and extend the Discord bot code examples provided.

---

## 📚 What You’ll Learn

- **How Discord bots work:**  
  Understand the basics of Discord bots using [discord.py](https://discordpy.readthedocs.io/).

- **How to add commands:**  
  See how to create commands like `!8ball`, `!cat`, `!userinfo`, and more.

- **How to handle events:**  
  Learn about event handlers such as `on_message` and `on_reaction_add`.

- **How to use cooldowns and permissions:**  
  Prevent spam and restrict commands to certain users or roles.

- **How to store and load data:**  
  Use JSON files to save scores, contributions, and game states.

---

## 🛠️ Getting Started

1. **Install Python 3.8+**  
   Download from [python.org](https://www.python.org/).

2. **Install discord.py**  
   ```
   pip install discord.py
   ```

3. **Set up your bot:**  
   - Create a bot on the [Discord Developer Portal](https://discord.com/developers/applications).
   - Copy your bot token and add it to your script.

4. **Run your bot:**  
   ```
   python welcomechan.py
   ```

---

## 📝 Example: Adding a Command

```python
@bot.command()
async def hello(ctx):
    await ctx.send("Hello, world!")
```

---

## 💡 Tips

- **Never share your bot token publicly!**
- Use cooldowns to prevent spam.
- Use permissions to protect admin commands.
- Read the [discord.py documentation](https://discordpy.readthedocs.io/) for more advanced features.

---

## 📖 More Resources

- [discord.py Guide](https://discordpy.readthedocs.io/)
- [Official Discord API Docs](https://discord.com/developers/docs/intro)
- [Python.org Tutorials](https://docs.python.org/3/tutorial/)

---

Happy learning and coding!  
**— alexandrospanag**
