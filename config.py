import os

# --- Core Bot Token (Verify this matches exactly one string from @BotFather) ---
BOT_TOKEN = os.getenv("BOT_TOKEN", "8842243659:AAG1hXBDwSrjSZ18qQWtMuFc4238r-mbZy4").strip()

# --- Access Rights Credentials ---
MASTER_OWNER_ID = int(os.getenv("MASTER_OWNER_ID", "7195555305"))

# --- Hosting Port Settings ---
PORT = int(os.getenv("PORT", "10000"))

# --- Media Visual Assets ---
IMAGE_1 = os.getenv("IMAGE_1", "https://files.catbox.moe/sla8rd.jpg")

# --- Database Storage Settings ---
PART_1 = "mongodb+srv://praveenshiv2008_db_user:u1k6AuTaGD1bN7K7"
PART_2 = "@alyafilterbot.iv7zs5r.mongodb.net/?appName=AlyaFilterbot"
MONGO_URI = os.getenv("MONGO_URI", PART_1 + PART_2)
