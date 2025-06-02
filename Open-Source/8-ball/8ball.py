# 8BALL COMMAND -----------------------------------------------------------------------------------------------------------------------------------
@bot.command(name="8ball", aliases=["eightball"])
@cooldown(1, 300, BucketType.user)  # 1 use per 5 minutes per user
async def eight_ball(ctx, *, question: str = None):
    """
    Ask the magic 8-ball a question.
    Usage: !8ball Will I win the lottery?
    """
    responses = [
        "It is certain.", "It is decidedly so.", "Without a doubt.",
        "Yes – definitely.", "You may rely on it.", "As I see it, yes.",
        "Most likely.", "Outlook good.", "Yes.", "Signs point to yes.",
        "Reply hazy, try again.", "Ask again later.", "Better not tell you now.",
        "Cannot predict now.", "Concentrate and ask again.",
        "Don't count on it.", "My reply is no.", "My sources say no.",
        "Outlook not so good.", "Very doubtful."
    ]
    if not question:
        await ctx.send("🎱 Please ask a question, e.g. `!8ball Will I win the lottery?`")
        return
    answer = random.choice(responses)
    await ctx.send(f"🎱 Question: {question}\nAnswer: {answer}")
