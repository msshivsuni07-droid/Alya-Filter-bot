import logging
import config
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

async def welcome_new_members_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ Handles member arrivals and clears automated system join or approval badges """
    message = update.message
    if not message:
        return

    is_new_member = bool(message.new_chat_members)
    is_accepted_tag = bool(message.chat_shared or hasattr(message, 'successful_payment') or (message.text and "accepted into the group" in message.text.lower()))
    
    if is_new_member or is_accepted_tag:
        try:
            await context.bot.delete_message(chat_id=message.chat_id, message_id=message.message_id)
            logger.info(f"Erased system join/approval badge in chat {message.chat_id}")
        except Exception as e:
            logger.warning(f"Could not erase system tag: {e}. Bot needs delete permissions.")

    if message.new_chat_members:
        for member in message.new_chat_members:
            if member.id == context.bot.id:
                continue

            welcome_text = (
                f"👋 <b>ʜᴇʏ <a href='tg://user?id={member.id}'>{member.first_name}</a>!</b>\n\n"
                f"ᴡᴇʟᴄ0ᴍᴇ ᴛ0 <b>{message.chat.title}</b>! ✨\n"
                f"s0 ɢʟᴀᴅ ʏ0ᴜ ᴊ0ɪɴᴇᴅ ᴜs. ᴘʟᴇᴀsᴇ sᴛᴀʏ ᴀᴄᴛɪᴠᴇ ᴀɴᴅ ʀᴇsᴘᴇᴄᴛ ᴛʜᴇ ɢʀ0ᴜᴘ ʀᴜʟᴇs!"
            )

            keyboard = [[InlineKeyboardButton("🤖 Open Main Panel", url=f"https://t.me/{(await context.bot.get_me()).username}?start=help")]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            try:
                await message.chat.reply_photo(photo=config.IMAGE_1, caption=welcome_text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
            except Exception:
                await message.chat.reply_text(text=welcome_text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
