# telegram_bot.py
import logging
import requests
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Define conversation states
EMAIL, PASSWORD = range(2)

# Set the API login URL
# Replace <YOUR_PUBLIC_URL_OR_DOMAIN> with your domain or use localhost if testing locally
API_LOGIN_URL = "http://localhost/auth/login"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Welcome! Please enter your email to log in:")
    return EMAIL

async def get_email(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["email"] = update.message.text
    await update.message.reply_text("Now, please enter your password:")
    return PASSWORD

async def get_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    email = context.user_data.get("email")
    password = update.message.text

    # Prepare data for login
    data = {"email": email, "password": password}

    try:
        response = requests.post(API_LOGIN_URL, json=data)
        response.raise_for_status()  # Raise error for bad status codes
        user_info = response.json()
        await update.message.reply_text(
            f"Login successful! Welcome {user_info.get('email')}.\nYour role is: {user_info.get('role')}"
        )
    except Exception as e:
        await update.message.reply_text("Login failed. Please try again.")
        logger.error("Login failed: %s", e)
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Operation canceled.")
    return ConversationHandler.END

def main():
    # Replace with your Telegram Bot token from BotFather
    application = Application.builder().token("8103489251:AAEw30I0rifou8Ehx_Du2R_TCLEzA6w_Sbk").build()

    # Define the conversation handler for login
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_email)],
            PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_password)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == "__main__":
    main()
