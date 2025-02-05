import os
import logging
import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

# --- Global Configuration ---
API_LOGIN_URL = os.getenv("API_LOGIN_URL", "http://web:8000/auth/login")
API_CHECK_EMAIL_URL = os.getenv("API_CHECK_EMAIL_URL", "http://web:8000/auth/check_email")
BOT_TOKEN = os.getenv("BOT_TOKEN", "8103489251:AAEw30I0rifou8Ehx_Du2R_TCLEzA6w_Sbk")

# Conversation states for the login process
STATE_EMAIL, STATE_PASSWORD = range(2) 

# --- Logging ---
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Helper Function ---
def escape_markdown_v2(text: str) -> str:
    reserved_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in reserved_chars:
        text = text.replace(char, f"\\{char}")
    return text

# --- Translations Dictionary ---
translations = {
    "en": {
        "welcome": "🌐 *Welcome!* Please choose your language:",
        "login": "🔐 Login",
        "return": "↩️ Return",
        "email_prompt": "Please enter your email:",
        "email_not_found": "This email doesn't exist. Please enter a valid email:",
        "password_prompt": "Now, please enter your password:",
        "login_success": "Login successful! Welcome {email}. Your role is: {role}",
        "login_failed": "Login failed. Please try again.",
    },
    "ru": {
        "welcome": "🌐 *Добро пожаловать!* Пожалуйста, выберите язык:",
        "login": "🔐 Войти",
        "return": "↩️ Назад",
        "email_prompt": "Пожалуйста, введите вашу электронную почту:",
        "email_not_found": "Такой email не существует. Пожалуйста, введите действующий email:",
        "password_prompt": "Теперь введите ваш пароль:",
        "login_success": "Успешный вход! Добро пожаловать {email}. Ваша роль: {role}",
        "login_failed": "Ошибка входа. Пожалуйста, попробуйте снова.",
    },
    "ky": {
        "welcome": "🌐 *Кош келиңиз!* Сураныч, тилиңизди тандаңыз:",
        "login": "🔐 Кирүү",
        "return": "↩️ Артка",
        "email_prompt": "Сураныч, электрондук почтаңызды жазыңыз:",
        "email_not_found": "Мындай email жок. Сураныч, туура электрондук почтаңызды жазыңыз:",
        "password_prompt": "Эми сырсөзүңүздү жазыңыз:",
        "login_success": "Кирүү ийгиликтүү болду! {email} кош келиңиз. Сиздин ролуңуз: {role}",
        "login_failed": "Кирүү учурунда ката. Кайра аракет кылыңыз.",
    },
    "kk": {
        "welcome": "🌐 *Қош келдіңіз!* Тілді таңдаңыз:",
        "login": "🔐 Кіру",
        "return": "↩️ Артқа",
        "email_prompt": "Өтінеміз, электрондық поштаңызды енгізіңіз:",
        "email_not_found": "Мұндай email жоқ. Өтінеміз, дұрыс email енгізіңіз:",
        "password_prompt": "Енді, құпия сөзіңізді енгізіңіз:",
        "login_success": "Кіру сәтті болды! {email} қош келдіңіз. Сіздің рөліңіз: {role}",
        "login_failed": "Кіру кезінде қате кетті. Қайта көріңіз.",
    },
}

LANG_CODES = ["en", "ru", "ky", "kk"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("English", callback_data="en"),
         InlineKeyboardButton("Русский", callback_data="ru")],
        [InlineKeyboardButton("Kyrgyz", callback_data="ky"),
         InlineKeyboardButton("Қазақша", callback_data="kk")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    welcome_text = escape_markdown_v2(translations["en"]["welcome"])
    await update.message.reply_text(
        welcome_text,
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN_V2,
    )

async def main_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    data = query.data

    if data in LANG_CODES:
        context.user_data["language"] = data
        lang = data
        keyboard = [
            [
                InlineKeyboardButton(translations[lang]["login"], callback_data="login"),
                InlineKeyboardButton(translations[lang]["return"], callback_data="return"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        text = f"*{lang.upper()} Selected*\\\n\\\nChoose an option:"
        text = escape_markdown_v2(text)
        await query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN_V2,
        )
    elif data == "return":
        context.user_data.pop("language", None)
        keyboard = [
            [InlineKeyboardButton("English", callback_data="en"),
             InlineKeyboardButton("Русский", callback_data="ru")],
            [InlineKeyboardButton("Kyrgyz", callback_data="ky"),
             InlineKeyboardButton("Қазақша", callback_data="kk")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        welcome_text = escape_markdown_v2(translations["en"]["welcome"])
        await query.edit_message_text(
            text=welcome_text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN_V2,
        )

async def login_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("language", "en")
    keyboard = [[InlineKeyboardButton(translations[lang]["return"], callback_data="cancel_login")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    prompt = escape_markdown_v2(translations[lang]["email_prompt"])
    await query.edit_message_text(
        text=prompt,
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN_V2,
    )
    return STATE_EMAIL

async def email_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    email = update.message.text.strip()
    lang = context.user_data.get("language", "en")
    
    try:
        response = requests.post(API_CHECK_EMAIL_URL, json={"email": email})
        # If a 422 occurs (e.g. invalid email format), treat it as "email not found"
        if response.status_code == 422:
            result = {"exists": False}
        else:
            response.raise_for_status()
            result = response.json()
            
        if not result.get("exists", False):
            not_found_text = escape_markdown_v2(translations[lang]["email_not_found"])
            await update.message.reply_text(
                text=not_found_text,
                parse_mode=ParseMode.MARKDOWN_V2,
            )
            keyboard = [[InlineKeyboardButton(translations[lang]["return"], callback_data="cancel_login")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            prompt = escape_markdown_v2(translations[lang]["email_prompt"])
            await update.message.reply_text(
                text=prompt,
                reply_markup=reply_markup,
                parse_mode=ParseMode.MARKDOWN_V2,
            )
            return STATE_EMAIL
    except Exception as e:
        logger.error("Error checking email existence: %s", e)
        await update.message.reply_text(
            text="An error occurred while checking the email. Please try again.",
        )
        return STATE_EMAIL

    context.user_data["email"] = email
    keyboard = [[InlineKeyboardButton(translations[lang]["return"], callback_data="cancel_login")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    prompt = escape_markdown_v2(translations[lang]["password_prompt"])
    await update.message.reply_text(
        text=prompt,
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN_V2,
    )
    return STATE_PASSWORD

async def password_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    password = update.message.text.strip()
    email = context.user_data.get("email", "")
    lang = context.user_data.get("language", "en")
    data = {"email": email, "password": password}
    try:
        response = requests.post(API_LOGIN_URL, json=data)
        response.raise_for_status()
        user_info = response.json()
        success_text = translations[lang]["login_success"].format(
            email=user_info.get("email", email),
            role=user_info.get("role", "unknown")
        )
        success_text = escape_markdown_v2(success_text)
        await update.message.reply_text(
            text=success_text,
            parse_mode=ParseMode.MARKDOWN_V2,
        )
        return ConversationHandler.END
    except Exception as e:
        logger.error("Login error: %s", e)
        # Inform the user that the login failed and re-prompt for the password.
        failure_text = escape_markdown_v2(translations[lang]["login_failed"])
        await update.message.reply_text(
            text=failure_text,
            parse_mode=ParseMode.MARKDOWN_V2,
        )
        keyboard = [[InlineKeyboardButton(translations[lang]["return"], callback_data="cancel_login")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        prompt = escape_markdown_v2(translations[lang]["password_prompt"])
        await update.message.reply_text(
            text=prompt,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN_V2,
        )
        return STATE_PASSWORD

async def login_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("English", callback_data="en"),
         InlineKeyboardButton("Русский", callback_data="ru")],
        [InlineKeyboardButton("Kyrgyz", callback_data="ky"),
         InlineKeyboardButton("Қазақша", callback_data="kk")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    welcome_text = escape_markdown_v2(translations["en"]["welcome"])
    await query.edit_message_text(
        text=welcome_text,
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN_V2,
    )
    return ConversationHandler.END

def main() -> None:
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(main_menu_handler, pattern="^(en|ru|ky|kk|return)$"))

    login_conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(login_start, pattern="^login$")],
        states={
            STATE_EMAIL: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, email_received),
                CallbackQueryHandler(login_cancel, pattern="^cancel_login$")
            ],
            STATE_PASSWORD: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, password_received),
                CallbackQueryHandler(login_cancel, pattern="^cancel_login$")
            ],
        },
        fallbacks=[CallbackQueryHandler(login_cancel, pattern="^cancel_login$")],
    )
    application.add_handler(login_conv_handler)

    application.run_polling()

if __name__ == "__main__":
    main()
