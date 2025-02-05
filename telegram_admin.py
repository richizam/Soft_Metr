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
translations = {
"en": {
"view_workers": "View Workers",
"analytics": "Analytics",
"back": "Back",
"worker_list": "Worker List:",
"no_workers": "No workers found.",
"worker_details": "Worker Details:",
"daily_entries": "Daily Entries:",
"no_data": "No data available.",
"error_fetching": "Error fetching data.",
"top_workers": "Top Workers:"
}
}
def get_lang(context: ContextTypes.DEFAULT_TYPE) -> str:
    return context.user_data.get("language", "en")
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
        await query.edit_message_text(text="Returning to Admin Menu.")
        return ConversationHandler.END
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
        keyboard = [[InlineKeyboardButton(translations[lang]["back"], callback_data="admin_view_workers")]]
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
    text = translations[lang]["analytics"] + "\n"
    text += f"Average Hours: {analytics.get('average_hours', 0):.2f}\n"
    text += f"Max Hours: {analytics.get('max_hours', 0):.2f}\n"
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
            CallbackQueryHandler(admin_worker_details, pattern="^(worker_.*|admin_back)$")
        ],
        ADMIN_WORKER_DETAILS: [
            CallbackQueryHandler(admin_view_workers, pattern="^admin_view_workers$")
        ],
        ADMIN_ANALYTICS: [
            CallbackQueryHandler(admin_cancel, pattern="^admin_back$")
        ],
    },
    fallbacks=[CallbackQueryHandler(admin_cancel, pattern="^admin_cancel$")],
    allow_reentry=True
)
