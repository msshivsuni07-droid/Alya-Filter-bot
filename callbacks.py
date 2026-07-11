from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode

def get_start_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✨ A", callback_data="brand"), InlineKeyboardButton("✨ L", callback_data="brand"), 
         InlineKeyboardButton("✨ Y", callback_data="brand"), InlineKeyboardButton("✨ A", callback_data="brand")],
        [InlineKeyboardButton("• ABOUT •", callback_data="about"), InlineKeyboardButton("• HELP •", callback_data="help")],
        [InlineKeyboardButton("• COMMANDS •", callback_data="commands")],
        [InlineKeyboardButton("C", callback_data="close"), InlineKeyboardButton("L", callback_data="close"), 
         InlineKeyboardButton("0", callback_data="close"), InlineKeyboardButton("S", callback_data="close"), 
         InlineKeyboardButton("E", callback_data="close")]
    ])

async def master_callback_query_router(update, context):
    query = update.callback_query
    data = query.data
    
    # We use a silent answer to stop the loading icon without triggering an alert
    await query.answer()

    if data == "about":
        await query.edit_message_caption(caption="ℹ️ <b>ᴀʟʏᴀ sʏsᴛᴇᴍ sᴛᴀᴛɪ0ɴ</b>", 
                                         reply_markup=get_start_keyboard(), parse_mode=ParseMode.HTML)
    elif data == "help":
        await query.edit_message_caption(caption="❓ <b>ʜᴇʟᴘ ᴍᴀɴᴜᴀʟ</b>", 
                                         reply_markup=get_start_keyboard(), parse_mode=ParseMode.HTML)
    elif data == "commands":
        # No alert parameter is used here
        await query.edit_message_caption(caption="📂 <b>ᴄ0ᴍᴍᴀɴᴅs:</b>\n\n/filter, /filters, /del, /id", 
                                         reply_markup=get_start_keyboard(), parse_mode=ParseMode.HTML)
    elif data == "close":
        await query.message.delete()
