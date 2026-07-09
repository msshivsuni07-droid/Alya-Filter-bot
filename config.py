import os

# Telegram API & Bot Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN", "8842243659:AAG1hXBDwSrjSZ18qQWtMuFc4238r-mbZy4")
API_ID = int(os.getenv("API_ID", "28596954"))
API_HASH = os.getenv("API_HASH", "")  

# Administrative Rules & Logs
MASTER_OWNER_ID = 7195555305
LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID", "-1004413159220")) 
FILTER_STORAGE_CHANNEL_ID = int(os.getenv("FILTER_STORAGE_CHANNEL_ID", "-1004380631752"))

# Infrastructure Database Parameters
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://praveenshiv2008_db_user:u1k6AuTaGD1bN7K7@alyafilterbot.iv7zs5r.mongodb.net/?appName=AlyaFilterbot")

# Deployment Server Mapping Settings
RENDER_URL = os.getenv("RENDER_EXTERNAL_URL")
PORT = int(os.getenv("PORT", 3000))

# 🖼️ Image Link Asset Matrix with Catbox Hosting
IMAGE_1 = "https://files.catbox.moe/xh6fdc.jpg"
IMAGE_2 = "https://files.catbox.moe/t3c8bc.jpg"
IMAGE_3 = "https://files.catbox.moe/9tqcsy.jpg"
IMAGE_4 = "https://files.catbox.moe/sla8rd.jpg"
