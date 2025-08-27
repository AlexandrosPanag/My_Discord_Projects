"""
Weekly Riddle Command Implementation
Handles the !riddlemethis command and VIP role management.
"""

import logging
from discord.ext import commands
import discord
from bot_utils import (
    DataManager, RiddleManager, EmbedHelper, PermissionHelper, 
    BOT_CONFIG, send_achievement_notification
)

# Import from main app file
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app import add_contribution

# Set up module logger
logger = logging.getLogger('StarChan.RiddleCommand')

class RiddleCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='riddlemethis', aliases=['riddle', 'weeklyriddle'])
    async def riddle_me_this(self, ctx, *, answer: str = None):
        """
        Weekly riddle challenge! Solve the riddle to earn 3,000 contribution points.
        Only one person can win per week!
        Usage: !riddlemethis [answer]
        """
        try:
            # Load riddle state
            riddle_state = DataManager.load_riddle_state()
            current_riddle = RiddleManager.get_current_riddle(riddle_state)
            
            # Check if riddle is already solved
            if riddle_state.get("solved", False):
                winner_id = riddle_state.get("winner_id")
                if winner_id:
                    try:
                        winner = await self.bot.fetch_user(winner_id)
                        embed = EmbedHelper.create_info_embed(
                            "🏆 Riddle Already Solved!",
                            f"This week's riddle has already been solved by **{winner.display_name}**!\n\n"
                            f"🎁 They earned **3,000 contribution points**!\n"
                            f"⏰ Next riddle: {RiddleManager.get_time_until_next_riddle()}"
                        )
                    except:
                        embed = EmbedHelper.create_info_embed(
                            "🏆 Riddle Already Solved!",
                            f"This week's riddle has already been solved!\n\n"
                            f"⏰ Next riddle: {RiddleManager.get_time_until_next_riddle()}"
                        )
                else:
                    embed = EmbedHelper.create_info_embed(
                        "🏆 Riddle Already Solved!",
                        f"This week's riddle has already been solved!\n\n"
                        f"⏰ Next riddle: {RiddleManager.get_time_until_next_riddle()}"
                    )
                await ctx.send(embed=embed)
                return
            
            # If no answer provided, show the riddle
            if not answer:
                await self._show_riddle(ctx, riddle_state, current_riddle)
                return
            
            # Check the answer
            if RiddleManager.check_answer(answer, current_riddle["answer"]):
                await self._handle_correct_answer(ctx, riddle_state, current_riddle)
            else:
                await self._handle_incorrect_answer(ctx, riddle_state)
                
        except Exception as e:
            logger.error(f"Error in riddle command: {e}")
            embed = EmbedHelper.create_error_embed(
                "❌ Error",
                "Something went wrong with the riddle command. Please try again later."
            )
            await ctx.send(embed=embed)

    async def _show_riddle(self, ctx, riddle_state, current_riddle):
        """Display the current riddle."""
        embed = EmbedHelper.create_info_embed(
            "🧩 Weekly Riddle Challenge",
            f"**{current_riddle['riddle']}**\n\n"
            f"🎯 **How to answer:** `!riddlemethis your answer here`\n"
            f"🎁 **Prize:** 3,000 contribution points!\n"
            f"⚠️ **Note:** Only ONE person can win per week!\n\n"
            f"Good luck solving it!"
        )
        
        # Always show hint
        embed.add_field(
            name="💡 Hint",
            value=current_riddle["hint"],
            inline=False
        )
        
        embed.set_footer(text="Weekly riddle challenge • First to solve wins!")
        await ctx.send(embed=embed)

    async def _handle_correct_answer(self, ctx, riddle_state, current_riddle):
        """Handle when user gives correct answer."""
        try:
            # Double-check that riddle hasn't been solved while processing
            fresh_riddle_state = DataManager.load_riddle_state()
            if fresh_riddle_state.get("solved", False):
                embed = EmbedHelper.create_warning_embed(
                    "⚠️ Too Late!",
                    f"Sorry {ctx.author.mention}, someone else just solved the riddle!\n\n"
                    f"Better luck next week!"
                )
                await ctx.send(embed=embed)
                return
            
            # Mark riddle as solved and record winner
            riddle_state["solved"] = True
            riddle_state["winner_id"] = ctx.author.id
            riddle_state["winner_name"] = ctx.author.display_name
            DataManager.save_json_file("riddle_state.txt", riddle_state)
            
            # Award 3,000 contribution points
            await self._award_points(ctx, 3000)
            
            # Create success embed
            embed = EmbedHelper.create_success_embed(
                "🎉 CORRECT! Riddle Solved!",
                f"**Congratulations {ctx.author.mention}!**\n\n"
                f"🧩 **The answer was:** {current_riddle['answer'][0].title()}\n"
                f"💰 **You've earned 3,000 contribution points!**\n"
                f"🏆 **You are this week's riddle champion!**\n\n"
                f"⏰ Next riddle: {RiddleManager.get_time_until_next_riddle()}"
            )
            embed.set_thumbnail(url=ctx.author.display_avatar.url if ctx.author.display_avatar else None)
            embed.set_footer(text="Congratulations on solving the weekly riddle!")
            
            await ctx.send(embed=embed)
            
            # Log the achievement
            logger.info(f"User {ctx.author.id} ({ctx.author.name}) solved weekly riddle and earned 3,000 points")
            
        except Exception as e:
            logger.error(f"Error handling correct answer: {e}")
            embed = EmbedHelper.create_error_embed(
                "❌ Error",
                "You got the right answer, but there was an error processing it. Please contact an admin."
            )
            await ctx.send(embed=embed)

    async def _handle_incorrect_answer(self, ctx, riddle_state):
        """Handle when user gives incorrect answer."""
        embed = EmbedHelper.create_warning_embed(
            "❌ Incorrect Answer",
            f"Sorry {ctx.author.mention}, that's not correct.\n\n"
            f"� **Tip:** Look at the hint and think carefully!\n"
            f"🔄 **Try again:** Use `!riddlemethis your new answer`\n\n"
            f"Don't give up - you can keep trying!"
        )
        
        await ctx.send(embed=embed)

    async def _award_points(self, ctx, points):
        """Award contribution points to the user."""
        try:
            # Award points using the main bot's contribution system
            await add_contribution(ctx.author.id, points, ctx.channel, ctx.author)
            
            logger.info(f"Awarded {points} points to {ctx.author.id} ({ctx.author.name}) for solving weekly riddle")
            
        except Exception as e:
            logger.error(f"Error awarding points: {e}")
            raise

    # Hint command removed - hints are now shown automatically in riddlemethis command

    @commands.command(name='riddlestatus', aliases=['riddleinfo'])
    async def riddle_status(self, ctx):
        """Show current riddle status."""
        try:
            riddle_state = DataManager.load_riddle_state()
            current_riddle = RiddleManager.get_current_riddle(riddle_state)
            
            embed = EmbedHelper.create_info_embed(
                "🧩 Weekly Riddle Status",
                f"**Current Week:**\n"
                f"🏆 Riddle solved: {'✅ Yes' if riddle_state.get('solved', False) else '❌ No'}\n"
                f"🎯 Reward: 3,000 contribution points\n"
                f"👥 Open to: **Everyone** (first to solve wins!)\n\n"
                f"⏰ Next riddle: {RiddleManager.get_time_until_next_riddle()}"
            )
            
            if riddle_state.get('solved', False):
                winner_id = riddle_state.get('winner_id')
                if winner_id:
                    try:
                        winner = await self.bot.fetch_user(winner_id)
                        embed.add_field(
                            name="🎉 This Week's Winner",
                            value=f"**{winner.display_name}** earned 3,000 points!",
                            inline=False
                        )
                    except:
                        embed.add_field(
                            name="🎉 This Week's Winner",
                            value="Someone already solved this week's riddle and earned 3,000 points!",
                            inline=False
                        )
            else:
                embed.add_field(
                    name="🎯 How to Participate",
                    value="Use `!riddlemethis your answer` to solve the riddle!\nFirst person to get it right wins 3,000 points!",
                    inline=False
                )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in riddle status command: {e}")
            embed = EmbedHelper.create_error_embed(
                "❌ Error",
                "Something went wrong. Please try again later."
            )
            await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(RiddleCommand(bot))
