async def master_callback_query_router(update, context):
    query = update.callback_query
    data = query.data
    
    # Force a silent answer
    await query.answer()

    if data == "cmd_about":
        await query.edit_message_caption(caption="ℹ️ <b>ᴀʟʏᴀ sʏsᴛᴇᴍ sᴛᴀᴛɪ0ɴ</b>", 
                                         reply_markup=get_start_keyboard(), parse_mode=ParseMode.HTML)
    elif data == "cmd_help":
        await query.edit_message_caption(caption="❓ <b>ʜᴇʟᴘ ᴍᴀɴᴜᴀʟ</b>", 
                                         reply_markup=get_start_keyboard(), parse_mode=ParseMode.HTML)
    elif data == "cmd_commands":
        # New name ensures no old cache interference
        await query.edit_message_caption(caption="📂 <b>ᴄ0ᴍᴍᴀɴᴅs:</b>\n\n/filter, /filters, /del, /id", 
                                         reply_markup=get_start_keyboard(), parse_mode=ParseMode.HTML)
    elif data == "cmd_close":
        await query.message.delete()
