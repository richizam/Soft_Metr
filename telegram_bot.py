# telegram_bot.py

import os, logging, shutil, requests
from datetime import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.error import BadRequest
from telegram.constants import ParseMode
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ConversationHandler, MessageHandler, ContextTypes, filters

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Conversation states
LOGIN_EMAIL = 0
LOGIN_PASSWORD = 1
TASK_SELECTION = 2
WAIT_START = 3
WAIT_CHECKIN_PHOTO = 4
WAIT_CONFIRM_CHECKIN = 5
WAIT_FINISH = 6
WAIT_CHECKOUT_PHOTO = 7
WAIT_CONFIRM_CHECKOUT = 8
MAIN_MENU = 100

API_LOGIN_URL = os.getenv("API_LOGIN_URL", "http://web:8000/auth/login")
API_CHECK_EMAIL_URL = os.getenv("API_CHECK_EMAIL_URL", "http://web:8000/auth/check_email")
API_GET_TASKS_URL = os.getenv("API_GET_TASKS_URL", "http://web:8000")
API_DAILY_ENTRY_URL = os.getenv("API_DAILY_ENTRY_URL", "http://web:8000/data/daily-entry")
API_DAILY_ENTRY_TODAY_URL = os.getenv("API_DAILY_ENTRY_TODAY_URL", "http://web:8000/data/daily-entry/today")
BOT_TOKEN = os.getenv("BOT_TOKEN", "8103489251:AAEw30I0rifou8Ehx_Du2R_TCLEzA6w_Sbk")

# Translations dictionary
translations = {
    "en": {
        "welcome": "🌐 *Welcome!* Please choose your language:",
        "login": "🔐 Login",
        "logout": "Log Out",
        "enter_daily": "📝 Enter Daily Entry",
        "email_prompt": "Please enter your email:",
        "email_not_found": "This email doesn't exist. Please enter a valid email:",
        "password_prompt": "Now, please enter your password:",
        "login_success": "Login successful! Welcome {email}! Your role is: {role}",
        "login_failed": "Login failed. Please try again.",
        "daily_already": "You have already submitted your daily entry for today.",
        "task_prompt": "Please select the task you will perform today:",
        "start_button": "Start 🚀",
        "finish_button": "Finish ✅",
        "checkin_prompt": "Please send your check‑in photo:",
        "checkout_prompt": "Please send your check‑out photo:",
        "confirm_photo": "Is this the photo you want to send? 🤔",
        "yes": "Yes 👍",
        "no": "No 👎",
        "cancel": "Cancel ❌",
        "please_send_photo": "Please send a photo.",
        "please_send_new_checkin": "Please send a new check‑in photo.",
        "please_send_new_checkout": "Please send a new check‑out photo.",
        "submission_success": "Thank you! Your daily entry has been submitted successfully.",
        "submission_error": "Error submitting daily entry. Please try again.",
        "photo_sent": "Photo sent",
        "login_prompt": "Please log in to continue:"
    },
    "ru": {
        "welcome": "Привет! 👋🏻 Пожалуйста, выбери язык 🌍💬:",
        "login": "🔐 Войти",
        "logout": "Выйти",
        "enter_daily": "📝 Отправить ежедневный отчет",
        "email_prompt": "Пожалуйста, введи свою почту:",
        "email_not_found": "Такого email нет. Введи, пожалуйста, корректный email:",
        "password_prompt": "Теперь введи свой пароль:",
        "login_success": "Успешный вход! Привет, {email}! Твоя роль: {role}",
        "login_failed": "Ошибка входа. Попробуй ещё раз.",
        "daily_already": "Ты уже отправил ежедневный отчет сегодня.",
        "task_prompt": "Выбери задачу, которую будешь выполнять сегодня:",
        "start_button": "Начать 🚀",
        "finish_button": "Закончить ✅",
        "checkin_prompt": "Пришли фото для входа:",
        "checkout_prompt": "Пришли фото для выхода:",
        "confirm_photo": "Это фото, которое хочешь отправить? 🤔",
        "yes": "Да 👍",
        "no": "Нет 👎",
        "cancel": "Отмена ❌",
        "please_send_photo": "Пожалуйста, пришли фото.",
        "please_send_new_checkin": "Пришли новое фото для входа.",
        "please_send_new_checkout": "Пришли новое фото для выхода.",
        "submission_success": "Спасибо! Ежедневный отчет успешно отправлен.",
        "submission_error": "Ошибка отправки отчета. Попробуй ещё раз.",
        "photo_sent": "Фото отправлено.",
        "login_prompt": "Пожалуйста, войди, чтобы продолжить:"
    },
    "ky": {
        "welcome": "🌐 *Кош келиңиз!* Сураныч, тилиңизди тандаңыз:",
        "login": "🔐 Кирүү",
        "logout": "Чыгуу",
        "enter_daily": "Күнүмдүк отчетту жөнөтүү",
        "email_prompt": "Сураныч, электрондук почтаңызды жазыңыз:",
        "email_not_found": "Мындай email жок. Сураныч, туура электрондук почтаңызды жазыңыз:",
        "password_prompt": "Эми сырсөзүңүздү жазыңыз:",
        "login_success": "Кирүү ийгиликтүү болду! {email} кош келиңиз. Сиздин ролуңуз: {role}",
        "login_failed": "Кирүү учурунда ката. Кайра аракет кылыңыз.",
        "daily_already": "Сиз бүгүн күнүмдүк отчетту жөнөтүп алдыңыз.",
        "task_prompt": "Сураныч, бүгүн аткармакчы болгон тапшырманы тандаңыз:",
        "start_button": "Баштоо",
        "finish_button": "Аяктоо",
        "checkin_prompt": "Сураныч, кирүү үчүн фото жибериниз:",
        "checkout_prompt": "Сураныч, чыгуу үчүн фото жибериниз:",
        "confirm_photo": "Бул сиз жөнөтүүчү фото экенине ишенесизби?",
        "yes": "Ооба",
        "no": "Жок",
        "cancel": "Баш тартуу",
        "please_send_photo": "Сураныч, фото жибериңиз.",
        "please_send_new_checkin": "Сураныч, кирүү үчүн жаңы фото жибериниз.",
        "please_send_new_checkout": "Сураныч, чыгуу үчүн жаңы фото жибериниз.",
        "submission_success": "Рахмат! Сиздин күнүмдүк отчет ийгиликтүү жөнөтүлдү.",
        "submission_error": "Ката, күнүмдүк отчет жөнөтүлгөн жок. Кайра аракет кылыңыз.",
        "photo_sent": "Фото жөнөтүлдү.",
        "login_prompt": "Сураныч, кирип улант:"
    },
    "kk": {
        "welcome": "🌐 *Қош келдіңіз!* Тілді таңдаңыз:",
        "login": "🔐 Кіру",
        "logout": "Шығу",
        "enter_daily": "Күнделікті есепті енгізу",
        "email_prompt": "Өтінеміз, электрондық поштаңызды енгізіңіз:",
        "email_not_found": "Мұндай email жоқ. Өтінеміз, дұрыс email енгізіңіз:",
        "password_prompt": "Енді, құпия сөзіңізді енгізіңіз:",
        "login_success": "Кіру сәтті болды! {email} қош келдіңіз. Сіздің рөліңіз: {role}",
        "login_failed": "Кіру кезінде қате кетті. Қайта көріңіз.",
        "daily_already": "Сіз бүгін күнделікті есепті енгізіп қойдыңыз.",
        "task_prompt": "Бүгін орындауыңыз қажет тапсырманы таңдаңыз:",
        "start_button": "Бастау",
        "finish_button": "Аяқтау",
        "checkin_prompt": "Өтінеміз, кірген кездегі фотоны жіберіңіз:",
        "checkout_prompt": "Өтінеміз, шыққан кездегі фотоны жіберіңіз:",
        "confirm_photo": "Бұл сіз жібергіңіз келетін фото екеніне сенесіз бе?",
        "yes": "Иә",
        "no": "Жоқ",
        "cancel": "Бас тарту",
        "please_send_photo": "Өтінеміз, фото жіберіңіз.",
        "please_send_new_checkin": "Өтінеміз, кірген кездегі жаңа фото жіберіңіз.",
        "please_send_new_checkout": "Өтінеміз, шыққан кездегі жаңа фото жіберіңіз.",
        "submission_success": "Рақмет! Күнделікті есеп сәтті жіберілді.",
        "submission_error": "Күнделікті есеп жіберілген жоқ. Өтінеміз, қайта көріңіз.",
        "photo_sent": "Фото жіберілді.",
        "login_prompt": "Кіріп, жалғастыр:"
    }
}

def escape_markdown(text: str) -> str:
    reserved_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in reserved_chars:
        text = text.replace(char, f"\\{char}")
    return text

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("English", callback_data="en"), InlineKeyboardButton("Русский", callback_data="ru")],
        [InlineKeyboardButton("Kyrgyz", callback_data="ky"), InlineKeyboardButton("Қазақша", callback_data="kk")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    # Start with Russian welcome message by default
    welcome_text = escape_markdown(translations["ru"]["welcome"])
    await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN_V2)

async def main_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    try:
        await query.answer()
    except BadRequest as e:
        logger.warning("Callback query answer failed: %s", e)
    data = query.data
    if data in ["en", "ru", "ky", "kk"]:
        context.user_data["language"] = data
        lang = data
        keyboard = [[InlineKeyboardButton(translations[lang]["login"], callback_data="login")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        text = translations[lang]["login_prompt"]
        try:
            await query.edit_message_text(text=escape_markdown(text), reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN_V2)
        except BadRequest:
            await query.message.reply_text(text=escape_markdown(text), reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN_V2)
    elif data == "logout":
        context.user_data.clear()
        keyboard = [
            [InlineKeyboardButton("English", callback_data="en"), InlineKeyboardButton("Русский", callback_data="ru")],
            [InlineKeyboardButton("Kyrgyz", callback_data="ky"), InlineKeyboardButton("Қазақша", callback_data="kk")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        try:
            await query.edit_message_text(text=escape_markdown(translations["ru"]["welcome"]), reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN_V2)
        except BadRequest:
            await query.message.reply_text(text=escape_markdown(translations["ru"]["welcome"]), reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN_V2)

async def conversation_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = context.user_data.get("language", "ru")
    if "user_id" not in context.user_data:
        context.user_data.clear()
        keyboard = [
            [InlineKeyboardButton("English", callback_data="en"), InlineKeyboardButton("Русский", callback_data="ru")],
            [InlineKeyboardButton("Kyrgyz", callback_data="ky"), InlineKeyboardButton("Қазақша", callback_data="kk")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        if update.callback_query:
            try:
                await update.callback_query.message.edit_text(
                    text=escape_markdown(translations["ru"]["welcome"]),
                    reply_markup=reply_markup,
                    parse_mode=ParseMode.MARKDOWN_V2,
                )
            except BadRequest as e:
                logger.warning("Editing message failed in conversation_cancel: %s", e)
        else:
            await update.message.reply_text(
                text=escape_markdown(translations["ru"]["welcome"]),
                reply_markup=reply_markup,
                parse_mode=ParseMode.MARKDOWN_V2,
            )
    else:
        await main_menu_handler(update, context)
    return ConversationHandler.END

async def login_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    try:
        await query.answer()
    except BadRequest as e:
        logger.warning("Callback query answer failed in login_start: %s", e)
    lang = context.user_data.get("language", "ru")
    keyboard = [[InlineKeyboardButton(translations[lang]["cancel"], callback_data="cancel_conversation")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text=escape_markdown(translations[lang]["email_prompt"]),
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN_V2,
    )
    return LOGIN_EMAIL

async def email_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = context.user_data.get("language", "ru")
    email = update.message.text.strip()
    if email.lower() == "cancel":
        return await conversation_cancel(update, context)
    try:
        response = requests.post(API_CHECK_EMAIL_URL, json={"email": email})
        if response.status_code == 422:
            result = {"exists": False}
        else:
            response.raise_for_status()
            result = response.json()
        if not result.get("exists", False):
            await update.message.reply_text(
                text=escape_markdown(translations[lang]["email_not_found"]),
                parse_mode=ParseMode.MARKDOWN_V2,
            )
            keyboard = [[InlineKeyboardButton(translations[lang]["cancel"], callback_data="cancel_conversation")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                text=escape_markdown(translations[lang]["email_prompt"]),
                reply_markup=reply_markup,
                parse_mode=ParseMode.MARKDOWN_V2,
            )
            return LOGIN_EMAIL
    except Exception as e:
        logger.error("Error checking email existence: %s", e)
        await update.message.reply_text("An error occurred while checking the email. Please try again.")
        return LOGIN_EMAIL
    context.user_data["email"] = email
    keyboard = [[InlineKeyboardButton(translations[lang]["cancel"], callback_data="cancel_conversation")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        text=escape_markdown(translations[lang]["password_prompt"]),
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN_V2,
    )
    return LOGIN_PASSWORD

async def password_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = context.user_data.get("language", "ru")
    password = update.message.text.strip()
    if password.lower() == "cancel":
        return await conversation_cancel(update, context)
    try:
        await update.message.delete()
    except Exception as e:
        logger.error("Error deleting password message: %s", e)
    email = context.user_data.get("email", "")
    data = {"email": email, "password": password}
    try:
        response = requests.post(API_LOGIN_URL, json=data)
        response.raise_for_status()
        user_info = response.json()
        context.user_data["role"] = user_info.get("role", "unknown")
        context.user_data["user_id"] = user_info.get("user_id")
        context.user_data["project_id"] = user_info.get("project_id")
        success_text = translations[lang]["login_success"].format(
            email=user_info.get("email", email), role=user_info.get("role", "unknown")
        )
        await update.message.reply_text(text=escape_markdown(success_text), parse_mode=ParseMode.MARKDOWN_V2)
    except Exception as e:
        logger.error("Login error: %s", e)
        await update.message.reply_text(text=escape_markdown(translations[lang]["login_failed"]), parse_mode=ParseMode.MARKDOWN_V2)
        return LOGIN_PASSWORD
    return await show_logged_in_menu(update, context)

async def show_logged_in_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = context.user_data.get("language", "ru")
    user_id = context.user_data.get("user_id")
    email = context.user_data.get("email", "User")
    role = context.user_data.get("role", "unknown")
    try:
        response = requests.get(API_DAILY_ENTRY_TODAY_URL, params={"user_id": user_id})
        response.raise_for_status()
        result = response.json()
    except Exception as e:
        logger.error("Error checking daily entry for today: %s", e)
        result = {"exists": False}
    if role == "admin":
        text = translations[lang]["login_success"].format(email=email, role=role) + "\n\nAdmin Menu:"
        keyboard = [
            [InlineKeyboardButton("View Workers", callback_data="admin_view_workers")],
            [InlineKeyboardButton("Analytics", callback_data="admin_analytics")],
            [InlineKeyboardButton(translations[lang]["logout"], callback_data="logout")],
        ]
    else:
        if result.get("exists", False):
            text = translations[lang]["login_success"].format(email=email, role=role) + "\n\n" + translations[lang]["daily_already"]
            keyboard = [[InlineKeyboardButton(translations[lang]["logout"], callback_data="logout")]]
        else:
            text = translations[lang]["login_success"].format(email=email, role=role)
            keyboard = [
                [InlineKeyboardButton(translations[lang]["enter_daily"], callback_data="enter_daily_entry")],
                [InlineKeyboardButton(translations[lang]["logout"], callback_data="logout")],
            ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.callback_query:
        try:
            await update.callback_query.message.edit_text(
                text=escape_markdown(text), reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN_V2
            )
        except BadRequest as e:
            logger.warning("Editing message in show_logged_in_menu failed: %s", e)
            await update.callback_query.message.reply_text(
                text=escape_markdown(text), reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN_V2
            )
    else:
        await update.message.reply_text(
            text=escape_markdown(text), reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN_V2
        )
    return MAIN_MENU

async def enter_daily_entry_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    from_ = await show_task_selection(update, context)
    return from_

async def logout_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    keyboard = [
        [InlineKeyboardButton("English", callback_data="en"), InlineKeyboardButton("Русский", callback_data="ru")],
        [InlineKeyboardButton("Kyrgyz", callback_data="ky"), InlineKeyboardButton("Қазақша", callback_data="kk")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    try:
        await update.callback_query.message.edit_text(
            text=escape_markdown(translations["ru"]["welcome"]),
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN_V2,
        )
    except BadRequest as e:
        logger.warning("Editing message in logout_handler failed: %s", e)
        await update.callback_query.message.reply_text(
            text=escape_markdown(translations["ru"]["welcome"]),
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN_V2,
        )
    return ConversationHandler.END

async def show_task_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = context.user_data.get("language", "ru")
    project_id = context.user_data.get("project_id")
    if not project_id:
        await update.message.reply_text("No project assigned. Contact admin.")
        return ConversationHandler.END
    try:
        url = f"{API_GET_TASKS_URL}/projects/{project_id}/tasks"
        response = requests.get(url)
        response.raise_for_status()
        tasks = response.json()
    except Exception as e:
        logger.error("Error fetching tasks: %s", e)
        await update.message.reply_text("Error fetching tasks. Please try again later.")
        return ConversationHandler.END
    if not tasks:
        await update.message.reply_text("No tasks found for your project.")
        return ConversationHandler.END
    keyboard = []
    for task in tasks:
        keyboard.append([InlineKeyboardButton(task["name"], callback_data=f"task_{task['id']}")])
    keyboard.append([InlineKeyboardButton(translations[lang]["cancel"], callback_data="cancel_conversation")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    prompt = translations[lang]["task_prompt"]
    if update.message:
        await update.message.reply_text(text=escape_markdown(prompt), reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN_V2)
    else:
        await update.callback_query.message.reply_text(text=escape_markdown(prompt), reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN_V2)
    return TASK_SELECTION

async def task_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    try:
        await query.answer()
    except BadRequest as e:
        logger.warning("Callback query answer failed in task_selected: %s", e)
    data = query.data
    lang = context.user_data.get("language", "ru")
    if data.startswith("task_"):
        task_id = int(data.split("_")[1])
        context.user_data["task_id"] = task_id
        keyboard = [
            [InlineKeyboardButton(translations[lang]["start_button"], callback_data="start_task")],
            [InlineKeyboardButton(translations[lang]["cancel"], callback_data="cancel_conversation")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text=escape_markdown(translations[lang]["start_button"]),
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN_V2,
        )
        return WAIT_START
    elif data == "cancel_conversation":
        return await conversation_cancel(update, context)
    return TASK_SELECTION

async def start_task_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    try:
        await query.answer()
    except BadRequest as e:
        logger.warning("Callback query answer failed in start_task_handler: %s", e)
    context.user_data["start_time"] = datetime.utcnow().isoformat()
    lang = context.user_data.get("language", "ru")
    keyboard = [[InlineKeyboardButton(translations[lang]["cancel"], callback_data="cancel_conversation")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text=escape_markdown(translations[lang]["checkin_prompt"]),
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN_V2,
    )
    return WAIT_CHECKIN_PHOTO

async def checkin_photo_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = context.user_data.get("language", "ru")
    if not update.message.photo:
        await update.message.reply_text(translations[lang]["please_send_photo"])
        return WAIT_CHECKIN_PHOTO
    photo = update.message.photo[-1]
    file = await photo.get_file()
    os.makedirs("photos", exist_ok=True)
    file_path = f"photos/temp_checkin_{file.file_id}.jpg"
    await file.download_to_drive(file_path)
    context.user_data["temp_check_in_photo"] = file_path
    keyboard = [
        [InlineKeyboardButton(translations[lang]["yes"], callback_data="confirm_checkin_yes"),
         InlineKeyboardButton(translations[lang]["no"], callback_data="confirm_checkin_no")],
        [InlineKeyboardButton(translations[lang]["cancel"], callback_data="cancel_conversation")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_photo(
        photo=open(file_path, "rb"),
        caption=escape_markdown(translations[lang]["confirm_photo"]),
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=reply_markup,
    )
    return WAIT_CONFIRM_CHECKIN

async def confirm_checkin_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    try:
        await query.answer()
    except BadRequest as e:
        logger.warning("Callback query answer failed in confirm_checkin_handler: %s", e)
    data = query.data
    lang = context.user_data.get("language", "ru")
    if data == "confirm_checkin_yes":
        temp_path = context.user_data.get("temp_check_in_photo")
        if temp_path:
            permanent_path = temp_path.replace("temp_", "")
            shutil.move(temp_path, permanent_path)
            context.user_data["check_in_photo"] = permanent_path
        context.user_data.pop("temp_check_in_photo", None)
        keyboard = [
            [InlineKeyboardButton(translations[lang]["finish_button"], callback_data="finish_task")],
            [InlineKeyboardButton(translations[lang]["cancel"], callback_data="cancel_conversation")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_caption(
            caption=escape_markdown(translations[lang]["photo_sent"]),
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN_V2,
        )
        return WAIT_FINISH
    elif data == "confirm_checkin_no":
        temp_path = context.user_data.get("temp_check_in_photo")
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
        context.user_data.pop("temp_check_in_photo", None)
        await query.edit_message_caption(
            caption=escape_markdown(translations[lang]["please_send_new_checkin"]),
            parse_mode=ParseMode.MARKDOWN_V2,
        )
        return WAIT_CHECKIN_PHOTO

async def finish_task_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    try:
        await query.answer()
    except BadRequest as e:
        logger.warning("Callback query answer failed in finish_task_handler: %s", e)
    context.user_data["finish_time"] = datetime.utcnow().isoformat()
    lang = context.user_data.get("language", "ru")
    keyboard = [[InlineKeyboardButton(translations[lang]["cancel"], callback_data="cancel_conversation")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if query.message.photo:
        try:
            await query.edit_message_caption(
                caption=escape_markdown(translations[lang]["checkout_prompt"]),
                reply_markup=reply_markup,
                parse_mode=ParseMode.MARKDOWN_V2,
            )
        except BadRequest as e:
            logger.warning("Editing message caption failed in finish_task_handler: %s", e)
            await query.message.reply_text(
                text=escape_markdown(translations[lang]["checkout_prompt"]),
                reply_markup=reply_markup,
                parse_mode=ParseMode.MARKDOWN_V2,
            )
    else:
        try:
            await query.edit_message_text(
                text=escape_markdown(translations[lang]["checkout_prompt"]),
                reply_markup=reply_markup,
                parse_mode=ParseMode.MARKDOWN_V2,
            )
        except BadRequest as e:
            logger.warning("Editing message text failed in finish_task_handler: %s", e)
            await query.message.reply_text(
                text=escape_markdown(translations[lang]["checkout_prompt"]),
                reply_markup=reply_markup,
                parse_mode=ParseMode.MARKDOWN_V2,
            )
    return WAIT_CHECKOUT_PHOTO

async def checkout_photo_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = context.user_data.get("language", "ru")
    if not update.message.photo:
        await update.message.reply_text(translations[lang]["please_send_photo"])
        return WAIT_CHECKOUT_PHOTO
    photo = update.message.photo[-1]
    file = await photo.get_file()
    os.makedirs("photos", exist_ok=True)
    file_path = f"photos/temp_checkout_{file.file_id}.jpg"
    await file.download_to_drive(file_path)
    context.user_data["temp_check_out_photo"] = file_path
    keyboard = [
        [InlineKeyboardButton(translations[lang]["yes"], callback_data="confirm_checkout_yes"),
         InlineKeyboardButton(translations[lang]["no"], callback_data="confirm_checkout_no")],
        [InlineKeyboardButton(translations[lang]["cancel"], callback_data="cancel_conversation")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_photo(
        photo=open(file_path, "rb"),
        caption=escape_markdown(translations[lang]["confirm_photo"]),
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=reply_markup,
    )
    return WAIT_CONFIRM_CHECKOUT

async def confirm_checkout_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    try:
        await query.answer()
    except BadRequest as e:
        logger.warning("Callback query answer failed in confirm_checkout_handler: %s", e)
    data = query.data
    lang = context.user_data.get("language", "ru")
    if data == "confirm_checkout_yes":
        temp_path = context.user_data.get("temp_check_out_photo")
        if temp_path:
            permanent_path = temp_path.replace("temp_", "")
            shutil.move(temp_path, permanent_path)
            context.user_data["check_out_photo"] = permanent_path
        context.user_data.pop("temp_check_out_photo", None)
        try:
            start_time = datetime.fromisoformat(context.user_data.get("start_time"))
            finish_time = datetime.fromisoformat(context.user_data.get("finish_time"))
            diff = finish_time - start_time
            hours_worked = diff.total_seconds() / 3600.0
        except Exception as e:
            logger.error("Error computing hours worked: %s", e)
            hours_worked = 0.0
        context.user_data["hours_worked"] = hours_worked
        payload = {
            "user_id": context.user_data.get("user_id"),
            "task_id": context.user_data.get("task_id"),
            "hours_worked": hours_worked,
            "start_time": context.user_data.get("start_time"),
            "finish_time": context.user_data.get("finish_time"),
        }
        files = {}
        if "check_in_photo" in context.user_data:
            files["check_in_photo"] = open(context.user_data["check_in_photo"], "rb")
        if "check_out_photo" in context.user_data:
            files["check_out_photo"] = open(context.user_data["check_out_photo"], "rb")
        try:
            response = requests.post(API_DAILY_ENTRY_URL, data=payload, files=files)
            response.raise_for_status()
            await query.message.reply_text(
                text=escape_markdown(translations[lang]["submission_success"]),
                parse_mode=ParseMode.MARKDOWN_V2,
            )
        except Exception as e:
            logger.error("Error submitting daily entry: %s", e)
            await query.message.reply_text(translations[lang]["submission_error"])
        return await show_logged_in_menu(update, context)
    elif data == "confirm_checkout_no":
        temp_path = context.user_data.get("temp_check_out_photo")
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
        context.user_data.pop("temp_check_out_photo", None)
        await query.edit_message_caption(
            caption=escape_markdown(translations[lang]["please_send_new_checkout"]),
            parse_mode=ParseMode.MARKDOWN_V2,
        )
        return WAIT_CHECKOUT_PHOTO

def main() -> None:
    from telegram_admin import admin_conv_handler
    application = Application.builder().token(BOT_TOKEN).build()
    conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(login_start, pattern="^login$"),
            CallbackQueryHandler(enter_daily_entry_handler, pattern="^enter_daily_entry$")
        ],
        states={
            LOGIN_EMAIL: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, email_received),
                CallbackQueryHandler(conversation_cancel, pattern="^cancel_conversation$")
            ],
            LOGIN_PASSWORD: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, password_received),
                CallbackQueryHandler(conversation_cancel, pattern="^cancel_conversation$")
            ],
            TASK_SELECTION: [
                CallbackQueryHandler(task_selected, pattern="^task_"),
                CallbackQueryHandler(conversation_cancel, pattern="^cancel_conversation$")
            ],
            WAIT_START: [
                CallbackQueryHandler(start_task_handler, pattern="^start_task$"),
                CallbackQueryHandler(conversation_cancel, pattern="^cancel_conversation$")
            ],
            WAIT_CHECKIN_PHOTO: [
                MessageHandler(filters.PHOTO, checkin_photo_received),
                CallbackQueryHandler(conversation_cancel, pattern="^cancel_conversation$")
            ],
            WAIT_CONFIRM_CHECKIN: [
                CallbackQueryHandler(confirm_checkin_handler, pattern="^confirm_checkin_")
            ],
            WAIT_FINISH: [
                CallbackQueryHandler(finish_task_handler, pattern="^finish_task$"),
                CallbackQueryHandler(conversation_cancel, pattern="^cancel_conversation$")
            ],
            WAIT_CHECKOUT_PHOTO: [
                MessageHandler(filters.PHOTO, checkout_photo_received),
                CallbackQueryHandler(conversation_cancel, pattern="^cancel_conversation$")
            ],
            WAIT_CONFIRM_CHECKOUT: [
                CallbackQueryHandler(confirm_checkout_handler, pattern="^confirm_checkout_")
            ],
            MAIN_MENU: [
                CallbackQueryHandler(enter_daily_entry_handler, pattern="^enter_daily_entry$"),
                CallbackQueryHandler(logout_handler, pattern="^logout$")
            ]
        },
        fallbacks=[CallbackQueryHandler(conversation_cancel, pattern="^cancel_conversation$")],
        allow_reentry=True,
    )
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(main_menu_handler, pattern="^(en|ru|ky|kk|logout)$"))
    application.add_handler(conv_handler)
    application.add_handler(admin_conv_handler)
    application.run_polling()

if __name__ == "__main__":
    main()
