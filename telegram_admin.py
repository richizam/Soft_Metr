# telegram_admin.py
import os
import logging
import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.error import BadRequest
from telegram.constants import ParseMode
from telegram.ext import CallbackQueryHandler, ConversationHandler, ContextTypes

logger = logging.getLogger(__name__)

ADMIN_VIEW_WORKERS = 20
ADMIN_WORKER_DETAILS = 21
ADMIN_ANALYTICS = 22

def escape_markdown_v2(text: str) -> str:
    reserved_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in reserved_chars:
        text = text.replace(char, f"\\{char}")
    return text

# Admin translations – all languages now have complete texts.
translations = {
    "en": {
        "view_workers": "👥 View Workers",
        "analytics": "📊 Analytics",
        "back": "🔙 Back",
        "worker_list": "Worker List:",
        "no_workers": "No workers found.",
        "worker_details": "Worker Details:",
        "daily_entries": "Daily Entries:",
        "no_data": "No data available.",
        "error_fetching": "Error fetching data.",
        "top_workers": "🏆 Top 10 Workers:",
        "average_hours": "Average Hours:",
        "max_hours": "Max Hours:",
        "admin_menu": "🛠 Admin Menu:",
        "logout": "Log Out"
    },
    "ru": {
        "view_workers": "👥 Рабочие",
        "analytics": "📊 Аналитика",
        "back": "🔙 Назад",
        "worker_list": "Список рабочих:",
        "no_workers": "Рабочих не найдено.",
        "worker_details": "Детали рабочего:",
        "daily_entries": "Отчёты:",
        "no_data": "Нет данных.",
        "error_fetching": "Ошибка получения данных.",
        "top_workers": "🏆 Лучшие рабочие (топ-10):",
        "average_hours": "Среднее время:",
        "max_hours": "Максимальное время:",
        "admin_menu": "🛠 Админ меню:",
        "logout": "Выйти"
    },
    "ky": {
        "view_workers": "👥 Ишчилер",
        "analytics": "📊 Аналитика",
        "back": "🔙 Артка",
        "worker_list": "Ишчилер тизмеси:",
        "no_workers": "Ишчилер табылган жок.",
        "worker_details": "Ишчинин маалыматтары:",
        "daily_entries": "Күнүмдүк эсептер:",
        "no_data": "Даналар жок.",
        "error_fetching": "Маалыматтарды алууда ката.",
        "top_workers": "Эң мыкты ишчилер 10:",
        "average_hours": "Орточо убакыт:",
        "max_hours": "Эң көп убакыт:",
        "admin_menu": "🛠 Админ меню:",
        "logout": "Чыгуу"
    },
    "kk": {
        "view_workers": "👥 Қызметкерлер",
        "analytics": "📊 Аналитика",
        "back": "🔙 Артқа",
        "worker_list": "Қызметкерлер тізімі:",
        "no_workers": "Қызметкерлер табылмады.",
        "worker_details": "Қызметкердің деректері:",
        "daily_entries": "Күнделікті есептер:",
        "no_data": "Деректер жоқ.",
        "error_fetching": "Деректерді алуда қате.",
        "top_workers": "Ең үздік қызметкерлер: 10 ",
        "average_hours": "Орташа уақыт:",
        "max_hours": "Ең көп уақыт:",
        "admin_menu": "🛠 Админ меню:",
        "logout": "Шығу"
    }
}

def get_lang(context: ContextTypes.DEFAULT_TYPE) -> str:
    return context.user_data.get("language", "ru")

async def admin_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # This function returns to the admin main menu.
    query = update.callback_query
    lang = get_lang(context)
    try:
        await query.answer()
    except BadRequest as e:
        logger.warning("Callback query answer failed in admin_main_menu: %s", e)
    keyboard = [
        [InlineKeyboardButton(translations[lang]["view_workers"], callback_data="admin_view_workers")],
        [InlineKeyboardButton(translations[lang]["analytics"], callback_data="admin_analytics")],
        [InlineKeyboardButton(translations[lang]["logout"], callback_data="logout")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = translations[lang]["admin_menu"]
    try:
        await query.edit_message_text(text=escape_markdown_v2(text), reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN_V2)
    except BadRequest as e:
        logger.warning("Editing message in admin_main_menu failed: %s", e)
        await query.message.reply_text(text=escape_markdown_v2(text), reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN_V2)
    return ADMIN_VIEW_WORKERS

async def admin_view_workers(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    lang = get_lang(context)
    try:
        await query.answer()
    except BadRequest as e:
        logger.warning("Callback query answer failed in admin_view_workers: %s", e)
    project_id = context.user_data.get("project_id")
    api_url = os.getenv("API_ADMIN_WORKERS_URL", "http://web:8000/admin/workers")
    try:
        response = requests.get(api_url, params={"project_id": project_id})
        response.raise_for_status()
        workers = response.json()
    except Exception as e:
        logger.error("Error fetching workers: %s", e)
        await query.edit_message_text(text=escape_markdown_v2(translations[lang]["error_fetching"]), parse_mode=ParseMode.MARKDOWN_V2)
        return ConversationHandler.END
    if not workers:
        await query.edit_message_text(text=escape_markdown_v2(translations[lang]["no_workers"]), parse_mode=ParseMode.MARKDOWN_V2)
        return ConversationHandler.END
    keyboard = []
    for worker in workers:
        keyboard.append([InlineKeyboardButton(worker["email"], callback_data=f"worker_{worker['id']}")])
    keyboard.append([InlineKeyboardButton(translations[lang]["back"], callback_data="admin_back")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = translations[lang]["worker_list"]
    await query.edit_message_text(text=escape_markdown_v2(text), reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN_V2)
    return ADMIN_VIEW_WORKERS

async def admin_worker_details(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    lang = get_lang(context)
    try:
        await query.answer()
    except BadRequest as e:
        logger.warning("Callback query answer failed in admin_worker_details: %s", e)
    data = query.data
    if data == "admin_back":
        return await admin_main_menu(update, context)
    if data.startswith("worker_"):
        worker_id = int(data.split("_")[1])
        api_url = os.getenv("API_ADMIN_WORKER_DETAILS_URL", f"http://web:8000/admin/worker/{worker_id}")
        try:
            response = requests.get(api_url)
            response.raise_for_status()
            details = response.json()
        except Exception as e:
            logger.error("Error fetching worker details: %s", e)
            await query.edit_message_text(text=escape_markdown_v2(translations[lang]["error_fetching"]), parse_mode=ParseMode.MARKDOWN_V2)
            return ADMIN_VIEW_WORKERS
        worker = details.get("worker", {})
        entries = details.get("entries", [])
        text = translations[lang]["worker_details"] + "\n"
        text += f"Email: {worker.get('email', 'N/A')}\n"
        text += f"Total Entries: {len(entries)}\n"
        if entries:
            text += translations[lang]["daily_entries"] + "\n"
            for entry in entries:
                text += f"- Date: {entry.get('date', '')}, Hours: {entry.get('hours_worked', 0)}\n"
        else:
            text += translations[lang]["no_data"]
        keyboard = [[InlineKeyboardButton(translations[lang]["back"], callback_data="admin_back")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=escape_markdown_v2(text), reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN_V2)
        return ADMIN_WORKER_DETAILS
    return ADMIN_VIEW_WORKERS

async def admin_analytics(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    lang = get_lang(context)
    try:
        await query.answer()
    except BadRequest as e:
        logger.warning("Callback query answer failed in admin_analytics: %s", e)
    project_id = context.user_data.get("project_id")
    api_url = os.getenv("API_ADMIN_ANALYTICS_URL", "http://web:8000/admin/analytics")
    try:
        response = requests.get(api_url, params={"project_id": project_id})
        response.raise_for_status()
        analytics = response.json()
    except Exception as e:
        logger.error("Error fetching analytics: %s", e)
        await query.edit_message_text(text=escape_markdown_v2(translations[lang]["error_fetching"]), parse_mode=ParseMode.MARKDOWN_V2)
        return ConversationHandler.END
    text = f"{translations[lang]['analytics']} 📊\n"
    text += f"{translations[lang]['average_hours']} 📈 {analytics.get('average_hours', 0):.2f}\n"
    text += f"{translations[lang]['max_hours']} 📉 {analytics.get('max_hours', 0):.2f}\n"
    top_workers = analytics.get("top_workers", [])
    if top_workers:
        text += translations[lang]["top_workers"] + "\n"
        for worker in top_workers:
            text += f"{worker.get('email', 'N/A')}: {worker.get('total_hours', 0):.2f}\n"
    else:
        text += translations[lang]["no_data"]
    keyboard = [[InlineKeyboardButton(translations[lang]["back"], callback_data="admin_back")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=escape_markdown_v2(text), reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN_V2)
    return ADMIN_ANALYTICS

async def admin_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    try:
        await query.answer()
    except BadRequest:
        pass
    await query.edit_message_text(text="Admin action cancelled.")
    return ConversationHandler.END

admin_conv_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(admin_view_workers, pattern="^admin_view_workers$"),
        CallbackQueryHandler(admin_analytics, pattern="^admin_analytics$")
    ],
    states={
        ADMIN_VIEW_WORKERS: [
            CallbackQueryHandler(admin_worker_details, pattern="^worker_.*$"),
            CallbackQueryHandler(admin_main_menu, pattern="^admin_back$")
        ],
        ADMIN_WORKER_DETAILS: [
            CallbackQueryHandler(admin_main_menu, pattern="^admin_back$")
        ],
        ADMIN_ANALYTICS: [
            CallbackQueryHandler(admin_main_menu, pattern="^admin_back$")
        ],
    },
    fallbacks=[CallbackQueryHandler(admin_cancel, pattern="^admin_cancel$")],
    allow_reentry=True
)
