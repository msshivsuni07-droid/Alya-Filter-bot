import logging
import config
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.constants import ParseMode, ChatMemberStatus
from telegram.ext import ContextTypes
from database import filters_col

logger = logging.getLogger(__name__)

def get_start_keyboard(active_button=None):
    """ Returns the primary main layout keyboard panel with highlighted active state """
    lbl_a = "🔹 A 🔹" if active_button == "A" else "A"
    lbl_l = "🔹 L 🔹" if active_button == "L" else "L"
    lbl_y = "🔹 Y 🔹" if active_button == "Y" else "Y"
    lbl_a2 = "🔹 A 🔹" if active_button == "A2" else "A"

    keyboard = [
        [
            InlineKeyboardButton(lbl_a, callback_data="btn_a"),
            InlineKeyboardButton(lbl_l, callback_data="btn_l"),
            InlineKeyboardButton(lbl_y, callback_data="btn_y"),
            InlineKeyboardButton(lbl_a2, callback_data="btn_a2")
        ],
        [
            InlineKeyboardButton("• AB0UT •", callback_data="cb_about"),
            InlineKeyboardButton("• HELP •", callback_data="cb_help")
        ],
        [
            InlineKeyboardButton("• C0MMANDS •", callback_data="cb_commands")
        ],
        [
            InlineKeyboardButton("C", callback_data="close_panel"),
            InlineKeyboardButton("L", callback_data="close_panel"),
            InlineKeyboardButton("0", callback_data="close_panel"),
            InlineKeyboardButton("S", callback_data="close_panel"),
            InlineKeyboardButton("E", callback_data="close_panel")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_commands_keyboard():
    """ Returns the system commands matrix configuration grid """
    keyboard = [
        [
            InlineKeyboardButton("🔨 BAN", callback_data="cmd_ban"),
            InlineKeyboardButton("🔓 UNBAN", callback_data="cmd_unban")
        ],
        [
            InlineKeyboardButton("🤫 MUTE", callback_data="cmd_mute"),
            InlineKeyboardButton("🔊 UNMUTE", callback_data="cmd_unmute")
        ],
        [
            InlineKeyboardButton("🚪 KICK", callback_data="cmd_kick"),
            InlineKeyboardButton("📢 TAGALL", callback_data="cmd_tagall")
        ],
        [
            InlineKeyboardButton("🛡️ PROMOTE", callback_data="cmd_promote"),
            InlineKeyboardButton("📉 DEMOTE", callback_data="cmd_demote")
        ],
        [
            InlineKeyboardButton("🛑 ST0P FILTER", callback_data="cmd_stopfilter"),
            InlineKeyboardButton("🚨 ST0P ALL", callback_data="cmd_stopall")
        ],
        [
            InlineKeyboardButton("🗑️ VIEW FILTERS", callback_data="cmd_viewfilters"),
            InlineKeyboardButton("📊 STATS", callback_data="cmd_stats")
        ],
        [
            InlineKeyboardButton("« BACK T0 MAIN", callback_data="cb_back_main")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

async def check_admin_privileges(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    user_id = update.effective_user.id
    if user_id == config.MASTER_OWNER_ID:
        return True
    if update.effective_chat.type == "private":
        return False
    try:
        member = await context.bot.get_chat_member(update.effective_chat.id, user_id)
        return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except Exception:
        return False

async def master_callback_query_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    try:
        await query.answer()
    except Exception:
        pass

    callback_data = query.data
    if not callback_data:
        return

    # ==========================================
    # 🖼️ IMAGE SWAP & DYNAMIC REFRESH LOGIC
    # ==========================================
    target_photo = None
    button_key = None
    label_tag = ""

    if callback_data == "btn_a": 
        target_photo = config.IMAGE_1
        button_key = "A"
        label_tag = " [ sᴛᴀᴛɪ0ɴ ᴀ ]"
    elif callback_data == "btn_l": 
        target_photo = config.IMAGE_2
        button_key = "L"
        label_tag = " [ sᴛᴀᴛɪ0ɴ ʟ ]"
    elif callback_data == "btn_y": 
        target_photo = config.IMAGE_3
        button_key = "Y"
        label_tag = " [ sᴛᴀᴛɪ0ɴ ʏ ]"
    elif callback_data == "btn_a2": 
        target_photo = config.IMAGE_4
        button_key = "A2"
        label_tag = " [ sᴛᴀᴛɪ0ɴ ᴀ𝟸 ]"

    if target_photo:
        forced_refresh_caption = (
            f"✨ <b>ᴡᴇʟᴄ0ᴍᴇ ᴛ0 ᴀʟʏᴀ ғɪʟᴛᴇʀ sᴛᴀᴛɪ0ɴ</b>{label_tag}\n\n"
            f"ᴜsᴇ ᴛʜᴇ ᴅʏɴᴀᴍɪᴄ sᴇʟᴇᴄᴛɪ0ɴ ʙ0ᴀʀᴅ ᴘᴀɴᴇʟ ᴜɴᴅᴇʀɴᴇᴀᴛʜ ᴛ0 ʟ00ᴋ ᴜᴘ sʏsᴛᴇᴍ "
            f"ɪɴғ0ʀᴍᴀᴛ0ɴ ᴍᴇᴛʀɪᴄs 0ʀ ᴄ0ɴғɪɢᴜʀᴀᴛɪ0ɴs."
        )
        try:
            await query.edit_message_media(
                media=InputMediaPhoto(media=target_photo, caption=forced_refresh_caption, parse_mode=ParseMode.HTML),
                reply_markup=get_start_keyboard(active_button=button_key)
            )
            return
        except Exception as e:
            logger.error(f"Image swap failure: {e}")
            return

    # ==========================================
    # 📑 NAVIGATION PAGE ROUTING CHANNELS
    # ==========================================
    if callback_data == "cb_commands":
        commands_text = (
            "🛠️ <b>SYSTEM c0MMANDS MATRIX</b>\n\n"
            "SELECT ANY MANAGEMENT 0R INDEXING t00L AB0VE t0 MANAGE THIS CHAT ENVIR0NMENT."
        )
        await query.edit_message_caption(caption=commands_text, reply_markup=get_commands_keyboard(), parse_mode=ParseMode.HTML)
        return

    elif callback_data == "cb_back_main":
        welcome_text = (
            "✨ <b>ᴡᴇʟᴄ0ᴍᴇ ᴛ0 ᴀʟʏᴀ ғɪʟᴛᴇʀ sᴛᴀᴛɪ0ɴ</b>\n\n"
            "ᴜsᴇ ᴛʜᴇ ᴅʏɴᴀᴍɪᴄ sᴇʟᴇᴄᴛɪ0ɴ ʙ0ᴀʀ裝 ᴘᴀɴᴇʟ ᴜɴᴅᴇʀɴᴇᴀᴛʜ ᴛ0 ʟ00ᴋ ᴜᴘ sʏsᴛᴇᴍ "
            "ɪɴғ0ʀᴍᴀᴛ0ɴ ᴍᴇᴛʀɪᴄs 0ʀ ᴄ0ɴғɪɢᴜʀᴀᴛɪ0ɴs."
        )
        await query.edit_message_caption(caption=welcome_text, reply_markup=get_start_keyboard(), parse_mode=ParseMode.HTML)
        return

    elif callback_data == "cb_help":
        help_text = "❓ <b>sʏsᴛᴇᴍ ᴍᴀɴᴜᴀʟ:</b> Use <code>/filter [keyword] [reply text]</code> to add keywords. Look up listings using <code>/filters</code>."
        await query.edit_message_caption(caption=help_text, reply_markup=get_start_keyboard(), parse_mode=ParseMode.HTML)
        return

    elif callback_data == "cb_about":
        about_text = "ℹ️ <b>ᴀʟʏᴀ ᴍᴀᴛʀɪx:</b> Python-Telegram-Bot powered cloud filter engine linked with secure Mongo infrastructure streams."
        await query.edit_message_caption(caption=about_text, reply_markup=get_start_keyboard(), parse_mode=ParseMode.HTML)
        return

    elif callback_data == "close_panel":
        try:
            await query.message.delete()
        except Exception:
            pass
        return

    if callback_data.startswith("cmd_"):
        if not await check_admin_privileges(update, context):
            await query.message.reply_text("<blockquote><b>...ʏ0ᴜʀ ɴ0ᴛ ᴍʏ sᴇɴᴘᴀɪ...</b></blockquote>", parse_mode=ParseMode.HTML)
            return

        chat_id = update.effective_chat.id
        action = callback_data.replace("cmd_", "")

        if action == "viewfilters":
            cursor = filters_col.find({"chat_id": str(chat_id)})
            chat_filters = await cursor.to_list(length=100)
            if not chat_filters:
                await query.message.reply_text("<blockquote>📂 <b>No active filters found.</b></blockquote>", parse_mode=ParseMode.HTML)
            else:
                f_list = "📂 <b>ᴀᴄᴛɪᴠᴇ ғɪʟᴛᴇʀs:</b>\n\n" + "\n".join([f"• <code>{f['keyword']}</code>" for f in chat_filters])
                await query.message.reply_text(f_list, parse_mode=ParseMode.HTML)
        elif action == "stopall":
            await filters_col.delete_many({"chat_id": str(chat_id)})
            await query.message.reply_text("<blockquote>🚨 <b>All chat word filters have been purged.</b></blockquote>", parse_mode=ParseMode.HTML)
        else:
            await query.message.reply_text(f"<blockquote>🛠️ <b>{action.upper()} action panel invoked.</b> Reply to a target user message to run.</blockquote>", parse_mode=ParseMode.HTML)
