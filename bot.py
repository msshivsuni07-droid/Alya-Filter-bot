import asyncio
import logging
import threading
import config
import database
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)
# Importing the router and keyboard from your callbacks.py
from callbacks import master_callback_query_router, get_start_keyboard
from welcome import welcome_new_members_handler

# Setup logging to monitor for the 404/401 errors seen previously
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Health Check Server (Required for Render) ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is active")
    def log_message(self, format, *args):
        return

def run_web_server():
    server = HTTPServer(("0.0.0.0", config.PORT), HealthCheckHandler)
    server.serve_forever()

# --- Main Bot Logic ---
async def start_command(update, context):
    """Sends the welcome image and the button keyboard."""
    await update.message.reply_photo(
        photo=config.IMAGE_1, 
        caption="ℹ️ <b>ᴀʟʏᴀ ᴍᴀᴛʀɪx:</b> Engine Online.", 
        reply_markup=get_start_keyboard(), 
        parse_mode="HTML"
    )

async def run_bot_async():
    # Building the application with your token from config.py
    app = Application.builder().token(config.BOT_TOKEN).build()
    
    # Handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CallbackQueryHandler(master_callback_query_router))
    
    # Initializing and starting
    await app.initialize()
    await app.start()
    
    # drop_pending_updates=True is critical to stop old pop-ups from firing
    await app.updater.start_polling(drop_pending_updates=True) 
    
    logger.info("Bot is running...")
    await asyncio.Event().wait()

if __name__ == "__main__":
    # Start the web server in a background thread
    threading.Thread(target=run_web_server, daemon=True).start()
    # Run the bot
    asyncio.run(run_bot_async())
