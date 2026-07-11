import asyncio, logging, config
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from callbacks import master_callback_query_router, get_start_keyboard

logging.basicConfig(level=logging.INFO)

async def start_command(update, context):
    await update.message.reply_photo(photo=config.IMAGE_1, caption="ℹ️ <b>ᴀʟʏᴀ ᴍᴀᴛʀɪx:</b> Engine Online.", 
                                     reply_markup=get_start_keyboard(), parse_mode="HTML")

async def main():
    # drop_pending_updates=True prevents the bot from processing old alerts
    app = Application.builder().token(config.BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CallbackQueryHandler(master_callback_query_router))
    
    await app.initialize()
    await app.start()
    await app.updater.start_polling(drop_pending_updates=True) 
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
