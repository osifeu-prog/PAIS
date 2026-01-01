import asyncio
import logging
from datetime import datetime
from decimal import Decimal
from typing import Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, 
    CallbackQueryHandler, ContextTypes, filters
)
import aiohttp
import json

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot configuration
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
API_URL = "http://localhost:8000"  # Change to your API URL

class PredictionBot:
    def __init__(self, token: str):
        self.token = token
        self.application = Application.builder().token(token).build()
        self.setup_handlers()
    
    def setup_handlers(self):
        """Setup command handlers"""
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("help", self.help))
        self.application.add_handler(CommandHandler("balance", self.balance))
        self.application.add_handler(CommandHandler("predict", self.predict))
        self.application.add_handler(CommandHandler("market", self.market))
        self.application.add_handler(CommandHandler("leaderboard", self.leaderboard))
        
        # Callback query handler for inline buttons
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
        
        # Message handler for predictions
        self.application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND, self.handle_message
        ))
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send welcome message and register user"""
        user = update.effective_user
        
        # Register user via API
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{API_URL}/api/v1/users/register-telegram", 
                                  json={
                                      "telegram_id": user.id,
                                      "username": user.username or user.first_name,
                                      "main_system_id": f"telegram_{user.id}"
                                  }) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    welcome_text = f"""
🎯 *Welcome to Prediction Point System*, {user.first_name}!

You've been awarded *{data.get('initial_points', 1000)} starting points*!

*Available Commands:*
/predict - Generate lottery predictions
/balance - Check your points balance
/market - Browse marketplace
/leaderboard - View top players
/help - Show all commands

*How it works:*
1. Use /predict to get lucky numbers
2. Earn points for accurate predictions
3. Points earn daily interest (0.1%)
4. Trade points in the marketplace
5. Climb the leaderboard!

Start by typing /predict to get your first prediction!
                    """
                else:
                    welcome_text = f"""
🎯 *Welcome to Prediction Point System*, {user.first_name}!

*Available Commands:*
/predict - Generate lottery predictions
/balance - Check your points balance
/market - Browse marketplace
/leaderboard - View top players
/help - Show all commands

*Note:* There was an issue with registration. Please try again.
                    """
        
        await update.message.reply_text(welcome_text, parse_mode='Markdown')
    
    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show help message"""
        help_text = """
*🤖 Prediction Point System Bot Help*

*📊 Account Commands:*
/start - Start the bot and register
/balance - Check your points balance and interest
/leaderboard - View top players

*🎯 Prediction Commands:*
/predict - Generate lottery predictions
/predict stats - View your prediction statistics

*🛒 Marketplace Commands:*
/market - Browse active listings
/market sell <price> <description> - Create a listing
/market my - View your listings

*💰 Points Economy:*
- Start with 1000 points
- Earn points for predictions
- Points earn 0.1% daily interest
- Trade points in marketplace
- Transfer points to friends

*Need more help?*
Contact support or visit our website.
        """
        
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def balance(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show user's balance"""
        user = update.effective_user
        
        async with aiohttp.ClientSession() as session:
            # Get user's API token (simplified - in production, use proper auth)
            # For now, we'll use a simplified approach
            async with session.get(
                f"{API_URL}/api/v1/ledger/balance",
                headers={"Authorization": f"Bearer telegram_{user.id}"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    balance_text = f"""
*💰 Your Points Balance*

*Current Balance:* {data['balance']:,.2f} points
*Total Earned:* {data['total_earned']:,.2f} points
*Total Spent:* {data['total_spent']:,.2f} points

*📈 Interest Information*
Daily Rate: {data['interest_rate']['daily']*100}%
APY: {data['interest_rate']['apy']:.2f}%
Projected Today: +{data['projected_interest_today']:.2f} points

*💡 Tips:*
- Keep points in your wallet to earn interest
- Make predictions daily to earn more
- Check /market for trading opportunities
                    """
                else:
                    balance_text = "❌ Could not fetch balance. Please try again."
        
        await update.message.reply_text(balance_text, parse_mode='Markdown')
    
    async def predict(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Generate predictions"""
        user = update.effective_user
        
        # Check for stats subcommand
        if context.args and context.args[0] == 'stats':
            await self.prediction_stats(update, context)
            return
        
        keyboard = [
            [
                InlineKeyboardButton("Lotto (6 numbers)", callback_data="predict_lotto"),
                InlineKeyboardButton("777 (3 numbers)", callback_data="predict_777")
            ],
            [
                InlineKeyboardButton("Chance (4 numbers)", callback_data="predict_chance"),
                InlineKeyboardButton("My Stats", callback_data="prediction_stats")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🎲 *Choose Lottery Type:*\n\n"
            "• Lotto: 6 numbers from 1-49\n"
            "• 777: 3 numbers from 0-9\n"
            "• Chance: 4 numbers from 0-9\n\n"
            "Click a button below to generate predictions:",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def prediction_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show prediction statistics"""
        user = update.effective_user
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{API_URL}/api/v1/predictions/stats",
                headers={"Authorization": f"Bearer telegram_{user.id}"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get('total_predictions', 0) == 0:
                        stats_text = "📊 You haven't made any predictions yet.\nUse /predict to get started!"
                    else:
                        stats_text = f"""
*📊 Your Prediction Statistics*

*Total Predictions:* {data['total_predictions']}
*Correct Predictions:* {data['correct_predictions']}
*Success Rate:* {data['success_rate']}%

*Accuracy:*
Average: {data['average_accuracy']}%
Best: {data['best_accuracy']}%
Worst: {data['worst_accuracy']}%

*Points Earned:* {data['total_points_earned']:,.2f}

*🎯 Tips:*
- Make predictions daily
- Analyze hot/cold numbers
- Check your stats regularly
                        """
                else:
                    stats_text = "❌ Could not fetch statistics. Please try again."
        
        # If called from callback, use different reply method
        if update.callback_query:
            await update.callback_query.edit_message_text(
                stats_text, 
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(stats_text, parse_mode='Markdown')
    
    async def market(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle marketplace commands"""
        if not context.args:
            # Show marketplace main menu
            keyboard = [
                [
                    InlineKeyboardButton("Browse Listings", callback_data="market_browse"),
                    InlineKeyboardButton("My Listings", callback_data="market_my")
                ],
                [
                    InlineKeyboardButton("Create Listing", callback_data="market_create"),
                    InlineKeyboardButton("My Transactions", callback_data="market_transactions")
                ]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                "🛒 *Marketplace*\n\n"
                "Trade points for services, digital products, or prediction packages!\n\n"
                "*Categories:*\n"
                "• Digital Products\n"
                "• Services\n"
                "• Prediction Packages\n"
                "• Consultations\n\n"
                "Select an option below:",
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
        
        elif context.args[0] == 'sell' and len(context.args) >= 3:
            # Handle create listing
            try:
                price = float(context.args[1])
                description = ' '.join(context.args[2:])
                
                # Simplified - in production, use proper API call
                await update.message.reply_text(
                    f"📝 Listing created!\n\n"
                    f"*Price:* {price} points\n"
                    f"*Description:* {description}\n\n"
                    f"Your listing will be reviewed and activated soon.",
                    parse_mode='Markdown'
                )
            except ValueError:
                await update.message.reply_text(
                    "❌ Invalid price. Usage: /market sell <price> <description>"
                )
        
        elif context.args[0] == 'my':
            # Show user's listings
            await update.message.reply_text(
                "📋 *Your Listings*\n\n"
                "Feature coming soon! Use the buttons above for now.",
                parse_mode='Markdown'
            )
    
    async def leaderboard(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show leaderboard"""
        timeframe = context.args[0] if context.args else "weekly"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{API_URL}/api/v1/users/leaderboard",
                params={"timeframe": timeframe, "limit": 10}
            ) as response:
                if response.status == 200:
                    leaderboard = await response.json()
                    
                    leaderboard_text = f"🏆 *{timeframe.title()} Leaderboard*\n\n"
                    
                    for i, player in enumerate(leaderboard[:10]):
                        medal = ""
                        if i == 0:
                            medal = "🥇 "
                        elif i == 1:
                            medal = "🥈 "
                        elif i == 2:
                            medal = "🥉 "
                        
                        leaderboard_text += (
                            f"{medal}*{player['username']}* - "
                            f"{player['points_balance']:,.0f} points\n"
                            f"  Level: {player['level']} • "
                            f"Predictions: {player['prediction_count']}\n\n"
                        )
                    
                    # Add timeframe selector
                    keyboard = [
                        [
                            InlineKeyboardButton("Daily", callback_data="leaderboard_daily"),
                            InlineKeyboardButton("Weekly", callback_data="leaderboard_weekly"),
                            InlineKeyboardButton("Monthly", callback_data="leaderboard_monthly")
                        ]
                    ]
                    
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    
                else:
                    leaderboard_text = "❌ Could not fetch leaderboard. Please try again."
                    reply_markup = None
        
        await update.message.reply_text(
            leaderboard_text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular text messages"""
        text = update.message.text
        
        # Check if it's lottery numbers
        if all(c.isdigit() or c.isspace() or c == ',' for c in text):
            numbers = [int(n.strip()) for n in text.replace(',', ' ').split() if n.strip().isdigit()]
            
            if 3 <= len(numbers) <= 10:
                # Analyze numbers
                await update.message.reply_text(
                    f"🔢 Analyzing your numbers: {', '.join(map(str, numbers))}\n\n"
                    f"This feature is coming soon! Use /predict to generate predictions.",
                    parse_mode='Markdown'
                )
                return
        
        # Default response
        await update.message.reply_text(
            "🤖 I didn't understand that command.\n"
            "Try /help to see available commands.",
            parse_mode='Markdown'
        )
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle inline button callbacks"""
        query = update.callback_query
        await query.answer()
        
        callback_data = query.data
        
        if callback_data.startswith("predict_"):
            lottery_type = callback_data.replace("predict_", "")
            
            # Generate prediction
            user = query.from_user
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{API_URL}/api/v1/predictions/generate",
                    params={"lottery_type": lottery_type},
                    headers={"Authorization": f"Bearer telegram_{user.id}"}
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        numbers = data.get("numbers", [])
                        probability = data.get("probability", 0)
                        
                        # Format based on lottery type
                        if lottery_type == "lotto":
                            type_name = "Lotto"
                            range_text = "1-49"
                        elif lottery_type == "777":
                            type_name = "777"
                            range_text = "0-9"
                        else:
                            type_name = "Chance"
                            range_text = "0-9"
                        
                        prediction_text = f"""
*🎰 {type_name} Prediction*

*Your Numbers:* {', '.join(map(str, numbers))}
*Range:* {range_text}
*Probability:* {probability:.6f}%

*📊 Analysis:*
These numbers were generated using:
• Historical frequency analysis
• Hot/Cold number patterns
• Statistical optimization

*💡 Tips:*
- Save these numbers for the next draw
- Make predictions daily to improve accuracy
- Check /balance to see points earned
                        """
                        
                        # Add keyboard for more actions
                        keyboard = [
                            [
                                InlineKeyboardButton("🔢 Analyze My Numbers", callback_data="analyze_numbers"),
                                InlineKeyboardButton("📊 My Stats", callback_data="prediction_stats")
                            ],
                            [
                                InlineKeyboardButton("🔄 New Prediction", callback_data=f"predict_{lottery_type}")
                            ]
                        ]
                        
                        reply_markup = InlineKeyboardMarkup(keyboard)
                        
                    else:
                        prediction_text = "❌ Could not generate prediction. Please try again."
                        reply_markup = None
            
            await query.edit_message_text(
                prediction_text,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
        
        elif callback_data == "prediction_stats":
            await self.prediction_stats(update, context)
        
        elif callback_data.startswith("leaderboard_"):
            timeframe = callback_data.replace("leaderboard_", "")
            context.args = [timeframe]
            await self.leaderboard(update, context)
        
        elif callback_data.startswith("market_"):
            action = callback_data.replace("market_", "")
            
            if action == "browse":
                await query.edit_message_text(
                    "🛒 *Browse Marketplace*\n\n"
                    "Feature coming soon! Check back later.",
                    parse_mode='Markdown'
                )
            elif action == "my":
                await query.edit_message_text(
                    "📋 *My Listings*\n\n"
                    "Feature coming soon! Check back later.",
                    parse_mode='Markdown'
                )
            elif action == "create":
                await query.edit_message_text(
                    "📝 *Create Listing*\n\n"
                    "To create a listing, use:\n"
                    "`/market sell <price> <description>`\n\n"
                    "*Example:*\n"
                    "`/market sell 500 Weekly predictions package`",
                    parse_mode='Markdown'
                )
    
    async def run(self):
        """Run the bot"""
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()
        
        logger.info("Bot started and polling...")
        
        # Keep running
        await asyncio.Event().wait()

def main():
    """Main function to run the bot"""
    bot = PredictionBot(BOT_TOKEN)
    
    try:
        asyncio.run(bot.run())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot error: {e}")

if __name__ == "__main__":
    main()
