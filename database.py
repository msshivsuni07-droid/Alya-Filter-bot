import logging
import sys
from motor.motor_asyncio import AsyncIOMotorClient
import config

logger = logging.getLogger(__name__)

db = None
filters_col = None

def init_db():
    global db, filters_col
    try:
        logger.info("Connecting to MongoDB Atlas...")
        client = AsyncIOMotorClient(config.MONGO_URI)
        db = client["alya_filter_database"]
        filters_col = db["chat_filters"]
        logger.info("Successfully established connection to MongoDB collection infrastructure.")
    except Exception as e:
        logger.critical(f"MongoDB connection failed: {e}")
        sys.exit(1)
