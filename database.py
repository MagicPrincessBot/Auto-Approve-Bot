from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from configs import cfg
import sys

try:
    client = MongoClient(cfg.MONGO_URI, serverSelectionTimeoutMS=5000)
    # Verify the connection is alive
    client.admin.command("ping")
    print("✅ MongoDB connected successfully.")
except (ConnectionFailure, ServerSelectionTimeoutError) as e:
    print(f"❌ MongoDB connection failed: {e}")
    sys.exit(1)

users  = client["main"]["users"]
groups = client["main"]["groups"]


def already_db(user_id: int) -> bool:
    return bool(users.find_one({"user_id": str(user_id)}))


def already_dbg(chat_id: int) -> bool:
    return bool(groups.find_one({"chat_id": str(chat_id)}))


def add_user(user_id: int):
    if not already_db(user_id):
        users.insert_one({"user_id": str(user_id)})


def remove_user(user_id: int):
    if already_db(user_id):
        users.delete_one({"user_id": str(user_id)})


def add_group(chat_id: int):
    if not already_dbg(chat_id):
        groups.insert_one({"chat_id": str(chat_id)})


def all_users() -> int:
    return users.count_documents({})


def all_groups() -> int:
    return groups.count_documents({})
