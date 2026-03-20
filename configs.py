from os import getenv

class Config:
    API_ID      = int(getenv("API_ID", "0"))
    API_HASH    = getenv("API_HASH", "")
    BOT_TOKEN   = getenv("BOT_TOKEN", "")
    # Force-subscribe channel ID (make bot admin here)
    CHID        = int(getenv("CHID", "0"))
    # Space-separated owner/admin user IDs
    SUDO        = list(map(int, getenv("SUDO", "0").split()))
    MONGO_URI   = getenv("MONGO_URI", "")

cfg = Config()
