  
@bot.command()
@cooldown(1, 60, BucketType.user)
async def retrogamequiz(ctx):
    """
    Play a Retro Quiz! Usage: !retrogamequiz
    """
    questions = [
        {
            "question": "Which company created the original Game Boy?",
            "choices": ["A) Sega", "B) Nintendo", "C) Sony", "D) Atari"],
            "answer": "b"
        },
        {
            "question": "What was the first home video game console?",
            "choices": ["A) Atari 2600", "B) NES", "C) Magnavox Odyssey", "D) ColecoVision"],
            "answer": "c"
        },
        {
            "question": "Which console is famous for its 'Ring of Death' error?",
            "choices": ["A) PlayStation 2", "B) Xbox 360", "C) Dreamcast", "D) SNES"],
            "answer": "b"
        },
        {
            "question": "Which handheld console used interchangeable 'Game Paks'?",
            "choices": ["A) Game Gear", "B) Game Boy", "C) PSP", "D) Neo Geo Pocket"],
            "answer": "b"
        },
        {
            "question": "Which company made the Dreamcast?",
            "choices": ["A) Sony", "B) Sega", "C) Nintendo", "D) Atari"],
            "answer": "b"
        },
        {
            "question": "What was the name of the first PlayStation mascot?",
            "choices": ["A) Mario", "B) Crash Bandicoot", "C) Sonic", "D) Donkey Kong"],
            "answer": "b"
        },
        {
            "question": "Which console introduced the first analog stick on a controller?",
            "choices": ["A) PlayStation", "B) Nintendo 64", "C) Atari 2600", "D) Sega Genesis"],
            "answer": "b"
        },
        {
            "question": "Which console was known for its 'Mode 7' graphics?",
            "choices": ["A) SNES", "B) NES", "C) Sega Saturn", "D) PlayStation"],
            "answer": "a"
        },
        {
            "question": "Which company created the Atari 2600?",
            "choices": ["A) Atari", "B) Nintendo", "C) Sega", "D) Sony"],
            "answer": "a"
        },
        {
            "question": "What color was the original Game Boy?",
            "choices": ["A) Red", "B) Green", "C) Gray", "D) Blue"],
            "answer": "c"
        },
        {
            "question": "Which console was the first to use CDs as its primary media?",
            "choices": ["A) PlayStation", "B) Sega Saturn", "C) 3DO", "D) SNES"],
            "answer": "c"
        },
        {
            "question": "Which company developed the Neo Geo console?",
            "choices": ["A) SNK", "B) Sega", "C) Nintendo", "D) Sony"],
            "answer": "a"
        },
        {
            "question": "Which console had the game 'Sonic the Hedgehog' as its mascot?",
            "choices": ["A) SNES", "B) Sega Genesis", "C) NES", "D) PlayStation"],
            "answer": "b"
        },
        {
            "question": "What was the first Nintendo console to support online play?",
            "choices": ["A) GameCube", "B) Wii", "C) NES", "D) SNES"],
            "answer": "a"
        },
        {
            "question": "Which console featured the game 'GoldenEye 007'?",
            "choices": ["A) PlayStation", "B) Nintendo 64", "C) Sega Saturn", "D) Dreamcast"],
            "answer": "b"
        },
        {
            "question": "Which company created the TurboGrafx-16?",
            "choices": ["A) NEC", "B) Sega", "C) Nintendo", "D) Sony"],
            "answer": "a"
        },
        {
            "question": "Which console was known for its VMU (Visual Memory Unit)?",
            "choices": ["A) Dreamcast", "B) PlayStation", "C) GameCube", "D) Xbox"],
            "answer": "a"
        },
        {
            "question": "Which console had the 'Power Glove' accessory?",
            "choices": ["A) NES", "B) SNES", "C) Sega Genesis", "D) Atari 2600"],
            "answer": "a"
        },
        {
            "question": "Which company made the handheld 'Lynx' console?",
            "choices": ["A) Atari", "B) Sega", "C) Nintendo", "D) SNK"],
            "answer": "a"
        },
        {
            "question": "Which console was bundled with 'Super Mario World'?",
            "choices": ["A) NES", "B) SNES", "C) N64", "D) GameCube"],
            "answer": "b"
        },
           {
            "question": "Which rare NES game is considered the 'Holy Grail' for collectors, sometimes selling for over $100,000?",
            "choices": ["A) Stadium Events", "B) DuckTales 2", "C) Little Samson", "D) Bubble Bobble Part 2"],
            "answer": "a"
        },
        {
            "question": "What was the codename for the Nintendo 64 during its development?",
            "choices": ["A) Project Reality", "B) Ultra 64", "C) Dolphin", "D) Revolution"],
            "answer": "a"
        },
        {
            "question": "Which Sega console featured a built-in TV tuner as an official accessory (in Japan)?",
            "choices": ["A) Game Gear", "B) Master System", "C) Saturn", "D) Dreamcast"],
            "answer": "a"
        },
        {
            "question": "Which arcade game was the first to feature a 'continue' option after losing all lives?",
            "choices": ["A) Double Dragon", "B) Gauntlet", "C) Pac-Man", "D) Donkey Kong"],
            "answer": "b"
        },
        {
            "question": "What was the name of the failed add-on for the SNES that was later reworked into the original PlayStation?",
            "choices": ["A) Satellaview", "B) Super FX", "C) Play Station", "D) 32X"],
            "answer": "c"
        },
        
    ]
    score = 0
    for q in questions:
        await ctx.send(f"🕹️ **Retro Quiz!**\n{q['question']}\n" + "\n".join(q["choices"]) + "\nType A, B, C, or D.")
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel and not m.author.bot
        try:
            msg = await bot.wait_for('message', timeout=20.0, check=check)
            if msg.content.lower().strip() == q["answer"]:
                await ctx.send("✅ Correct!")
                score += 1
            else:
                await ctx.send(f"❌ Wrong! The correct answer was {q['answer'].upper()}.")
        except asyncio.TimeoutError:
            await ctx.send("⏰ Time's up for this question!")

    # Purge up to 999 messages before printing the high score
    try:
        await ctx.channel.purge(limit=999)
    except Exception as e:
        await ctx.send(f"Could not purge messages: {e}")

    # Now print only the score and high score messages
    await ctx.send(f"🏁 Quiz finished! Your score: {score}/{len(questions)}")

    # Save high score if it's higher than previous
    user_id = str(ctx.author.id)
    prev = retrogame_scores.get(user_id, 0)
    if score > prev:
        retrogame_scores[user_id] = score
        save_retrogame_scores(retrogame_scores)
        await ctx.send(f"🌟 New personal high score! ({score})")
    elif score == len(questions) and prev < len(questions):
        retrogame_scores[user_id] = score
        save_retrogame_scores(retrogame_scores)
        await ctx.send(f"🏆 Perfect score! Well done!")

