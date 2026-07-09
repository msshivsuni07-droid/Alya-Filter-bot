import os
import sys
import logging
import asyncio
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
from telegram import Update
from telegram.constants import ParseMode, ChatPermissions
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    import config
    from database import init_db, filters_col
    from callbacks import master_callback_query_router, check_admin_privileges, get_start_keyboard
    from welcome import welcome_new_members_handler
except ImportError as e:
    logger.critical(f"Failed to import local modules: {e}")
    sys.exit(1)

# Memory storage to track consecutive links per user: {(chat_id, user_id): count}
LINK_SPAM_TRACKER = {}

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"Alya Filter Bot is running perfectly online.")
    def log_message(self, format, *args):
        return

def run_dummy_web_server():
    server_address = ("0.0.0.0", config.PORT)
    httpd = HTTPServer(server_address, HealthCheckHandler)
    logger.info(f"Dummy web server listening on port: {config.PORT}")
    httpd.serve_forever()

# ==========================================
# 🛑 ANTI-LINK FILTER & AUTO-MUTE ENGINE
# ==========================================
async def group_link_guardian_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Scans messages for URLs. Non-admins have links deleted immediately.
    If they send more than 5 links continuously, they are MUTED instantly.
    """
    message = update.effective_message
    if not message or not message.text:
        return
    
    if update.effective_chat.type == "private":
        return

    user = update.effective_user
    chat = update.effective_chat
    incoming_text = message.text.lower()
    
    has_link = "http://" in incoming_text or "https://" in incoming_text or "t.me/" in incoming_text or ".com" in incoming_text or ".net" in incoming_text or ".org" in incoming_text

    tracker_key = (chat.id, user.id)

    if has_link:
        # Check admin credentials
        is_authorized = await check_admin_privileges(update, context)
        if is_authorized:
            return  

        # 1. Delete the link message immediately
        try:
            await message.delete()
        except Exception as e:
            logger.error(f"Failed to delete link: {e}")

        # 2. Update the consecutive link tracking count
        LINK_SPAM_TRACKER[tracker_key] = LINK_SPAM_TRACKER.get(tracker_key, 0) + 1
        current_strikes = LINK_SPAM_TRACKER[tracker_key]

        # 3. Trigger Mute if strikes cross 5
        if current_strikes > 5:
            # Reset tracker for the user
            LINK_SPAM_TRACKER[tracker_key] = 0
            
            # Mute the user in the group (remove message sending rights)
            try:
                mute_permissions = ChatPermissions(can_send_messages=False, can_send_media_messages=False, can_send_other_messages=False)
                await context.bot.restrict_chat_member(chat_id=chat.id, user_id=user.id, permissions=mute_permissions)
                muted_status = "⚠️ <b>USER MUTED FOR SPAM</b>"
            except Exception as mute_err:
                logger.error(f"Failed to mute user: {mute_err}")
                muted_status = "❌ <b>FAILED TO MUTE (Check Bot Permissions)</b>"

            # Send a detailed report to your private owner chat
            report_log = (
                f"🚨 <b><u>LINK SPAM PUNISHMENT CRADLE</u></b>\n\n"
                f"• <b>ᴜsᴇʀ:</b> <a href='tg://user?id={user.id}'>{user.first_name}</a>\n"
                f"• <b>ᴜsᴇʀɴᴀᴍᴇ:</b> @{user.username if user.username else 'None'}\n"
                f"• <b>ᴜsᴇʀ ɪᴅ:</b> <code>{user.id}</code>\n"
                f"• <b>ɢʀ0ᴜᴘ:</b> {chat.title} (<code>{chat.id}</code>)\n"
                f"• <b>sᴛᴀᴛᴜs:</b> {muted_status}\n\n"
                f"💬 <i>This user sent more than 5 links continuously without sending normal text.</i>"
            )
            
            try:
                await context.bot.send_message(chat_id=config.MASTER_OWNER_ID, text=report_log, parse_mode=ParseMode.HTML)
            except Exception as e:
                logger.warning(f"Could not alert Master ID: {e}")
        else:
            # Report a regular single link deletion to the owner
            report_log = (
                f"🚨 <b><u>ᴜɴᴀᴜᴛʜ0ʀɪᴢᴇᴅ ʟɪɴᴋ ᴅᴇᴛᴇᴄᴛᴇᴅ</u></b>\n\n"
                f"• <b>ᴜsᴇʀ:</b> <a href='tg://user?id={user.id}'>{user.first_name}</a>\n"
                f"• <b>ᴜsᴇʀɴᴀᴍᴇ:</b> @{user.username if user.username else 'None'}\n"
                f"• <b>sᴛʀɪᴋᴇs:</b> <code>{current_strikes}/5</code>\n"
                f"• <b>ɢʀ0ᴜᴘ:</b> {chat.title}\n\n"
                f"💬 <b>ʟɪɴᴋ sᴇɴᴛ:</b>\n<code>{message.text}</code>"
            )
            try:
                await context.bot.send_message(chat_id=config.MASTER_OWNER_ID, text=report_log, parse_mode=ParseMode.HTML, disable_web_page_preview=True)
            except Exception:
                pass
    else:
        # If the user sends any normal text message without a link, reset their continuous link strike back to 0
        if tracker_key in LINK_SPAM_TRACKER:
            LINK_SPAM_TRACKER[tracker_key] = 0

# ==========================================
# 👋 CORE SYSTEM MENUS COMMANDS
# ==========================================
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = get_start_keyboard()
    welcome_text = (
        f"✨ <b>ᴡᴇʟᴄ0ᴍᴇ ᴛ0 ᴀʟʏᴀ ғɪʟᴛᴇʀ sᴛᴀᴛɪ0ɴ</b>\n\n"
        f"ᴜsᴇ ᴛʜᴇ ᴅʏɴᴀᴍɪᴄ sᴇʟᴇᴄᴛɪ0ɴ ʙ0ᴀʀᴅ ᴘᴀɴᴇʟ ᴜɴᴅᴇʀɴᴇᴀᴛʜ ᴛ0 ʟ00ᴋ ᴜᴘ sʏsᴛᴇ幕 "
        f"ɪɴғ0ʀᴍᴀᴛ0ɴ ᴍᴇᴛʀɪᴄs 0ʀ ᴄ0ɴғɪɢᴜʀᴀᴛɪ0ɴs."
    )
    try:
        await update.message.reply_photo(photo=config.IMAGE_1, caption=welcome_text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    except Exception:
        await update.message.reply_text(text=welcome_text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "❓ <b>ᴀʟʏᴀ ғɪʟᴛᴇʀ ʙ0ᴛ ʜᴇʟᴘ ᴅ0ᴄᴜᴍᴇɴᴛ</b>\n\n"
        "• /start - Wake up the interactive dashboard\n"
        "• /help - Display this commands list manual\n"
        "• /about - Read system credentials & info metadata\n"
        "• /id - Lookup unique chat, user, or target IDs\n\n"
        "<b>ᴀᴅᴍɪɴɪsᴛʀᴀᴛɪᴠᴇ ᴍ0ᴅᴇʀᴀᴛɪ0ɴ:</b>\n"
        "• `/filter [keyword] [reply text]` - Add auto-reply text\n"
        "• `/filters` - View list of active filters in this chat\n"
        "• `/del [keyword]` - Delete a target custom filter text\n"
        "• `/delall` - Wipe out all local chat filter sets from database"
    )
    await update.message.reply_text(text=help_text, parse_mode=ParseMode.HTML)

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    about_text = (
        "ℹ️ <b>ᴀʙ0ᴜᴛ ᴀʟʏᴀ sʏsᴛᴇᴍ ᴍᴀᴛʀɪx</b>\n\n"
        "• <b>Framework:</b> python-telegram-bot v21.1\n"
        "• <b>Database Storage:</b> MongoDB Atlas Engine\n"
        "• <b>Cloud Host:</b> Render Cloud Production Container\n\n"
        "🤖 <i>🛡️ keeping chats clean with automated pipelines.</i>"
    )
    await update.message.reply_text(text=about_text, parse_mode=ParseMode.HTML)

async def id_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    chat_type = update.effective_chat.type.capitalize()

    id_text = (
        f"🆔 <b><u>ɪᴅ ɪɴғ0ʀᴍᴀᴛɪ0ɴ ᴍᴀᴛʀɪx</u></b>\n\n"
        f"• <b>ʏ0ᴜʀ ɪᴅ:</b> <code>{user_id}</code>\n"
        f"• <b>ᴄʜᴀᴛ ɪᴅ ({chat_type}):</b> <code>{chat_id}</code>"
    )

    if message.reply_to_message:
        target_user = message.reply_to_message.from_user
        id_text += (
            f"\n\n💬 <b><u>ʀᴇᴘʟɪᴇᴅ ᴜsᴇʀ ɪɴғ0:</u></b>\n"
            f"• <b>ᴜsᴇʀ:</b> <a href='tg://user?id={target_user.id}'>{target_user.first_name}</a>\n"
            f"• <b>ᴛᴀʀɢᴇᴛ ɪᴅ:</b> <code>{target_user.id}</code>"
        )
    await message.reply_text(text=id_text, parse_mode=ParseMode.HTML)

# ==========================================
# 💬 FILTER MANAGEMENT FUNCTIONS
# ==========================================
async def global_text_filter_listener(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text or update.message.text.startswith("/"):
        return
    incoming_text = update.message.text.lower().strip()
    chat_id = str(update.effective_chat.id)

    matched_filter = await filters_col.find_one({"chat_id": chat_id, "keyword": incoming_text})
    if matched_filter:
        try:
            await update.message.reply_text(text=matched_filter["reply_message"], reply_to_message_id=update.message.message_id)
        except Exception:
            pass

async def set_filter_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_admin_privileges(update, context):
        await update.message.reply_text("<blockquote><b>...ʏ0ᴜʀ ɴ0ᴛ ᴍʏ sᴇɴᴘᴀɪ...</b></blockquote>", parse_mode=ParseMode.HTML)
        return
    if not context.args or len(context.args) < 2:
        await update.message.reply_text("<blockquote>⚠️ <b>Format Error! Use:</b> <code>/filter [keyword] [reply text]</code></blockquote>", parse_mode=ParseMode.HTML)
        return

    keyword = context.args[0].lower().strip()
    reply_message = " ".join(context.args[1:])
    chat = update.effective_chat

    await filters_col.update_one({"chat_id": str(chat.id), "keyword": keyword}, {"$set": {"reply_message": reply_message}}, upsert=True)
    await update.message.reply_text(f"<blockquote>✅ <b>Filter saved for:</b> <code>{keyword}</code></blockquote>", parse_mode=ParseMode.HTML)

async def view_filters_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    cursor = filters_col.find({"chat_id": chat_id})
    chat_filters = await cursor.to_list(length=100)

    if not chat_filters:
        await update.message.reply_text("<blockquote>📂 <b>No custom text filters saved in this chat yet.</b></blockquote>", parse_mode=ParseMode.HTML)
        return

    filter_list = f"📂 <b>ᴀᴄᴛɪᴠᴇ ғɪʟᴛᴇʀs ɪɴ {update.effective_chat.title or 'this chat'}:</b>\n\n"
    for idx, f in enumerate(chat_filters, 1):
        filter_list += f"{idx}. <code>{f['keyword']}</code>\n"
    await update.message.reply_text(text=filter_list, parse_mode=ParseMode.HTML)

async def delete_filter_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_admin_privileges(update, context):
        return
    if not context.args:
        await update.message.reply_text("<blockquote>⚠️ <b>Format Error! Use:</b> <code>/del [keyword]</code></blockquote>", parse_mode=ParseMode.HTML)
        return

    target_keyword = context.args[0].lower().strip()
    chat_id = str(update.effective_chat.id)

    result = await filters_col.delete_one({"chat_id": chat_id, "keyword": target_keyword})
    if result.deleted_count > 0:
        await update.message.reply_text(f"<blockquote>🗑️ <b>Deleted filter for:</b> <code>{target_keyword}</code></blockquote>", parse_mode=ParseMode.HTML)
    else:
        await update.message.reply_text("<blockquote>❌ <b>Filter keyword not found.</b></blockquote>", parse_mode=ParseMode.HTML)

async def delete_all_filters_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_admin_privileges(update, context):
        return
    chat_id = str(update.effective_chat.id)
    await filters_col.delete_many({"chat_id": chat_id})
    await update.message.reply_text("<blockquote>🚨 <b>All text filters purged from this group.</b></blockquote>", parse_mode=ParseMode.HTML)

# ==========================================
# 🚀 DEPLOYMENT BOOT ENGINE
# ==========================================
def main():
    logger.info("Initializing system bot engine pipeline...")
    web_thread = threading.Thread(target=run_dummy_web_server, daemon=True)
    web_thread.start()

    application = Application.builder().token(config.BOT_TOKEN).build()
    application.job_queue.run_once(lambda ctx: init_db(), when=0)

    # Core System Hooks
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("about", about_command))
    application.add_handler(CommandHandler("id", id_command))

    # Administrative Filters Hooks
    application.add_handler(CommandHandler("filter", set_filter_command))
    application.add_handler(CommandHandler("filters", view_filters_command))
    application.add_handler(CommandHandler("del", delete_filter_command))
    application.add_handler(CommandHandler("delall", delete_all_filters_command))

    # Event Router Listeners
    application.add_handler(CallbackQueryHandler(master_callback_query_router))
    
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS | filters.CHAT, welcome_new_members_handler), group=1)
    
    # Run the Link spam tracker pipeline
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, group_link_guardian_handler), group=2)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, global_text_filter_listener), group=3)

    logger.info("Starting background Long Polling mode...")
    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
