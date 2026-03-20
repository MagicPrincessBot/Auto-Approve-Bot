# Auto Approve Bot

**Automatically approves Telegram Group/Channel join requests.**

---

## 🐛 Bugs Fixed
| File | Bug |
|------|-----|
| `bot.py` | `chk` callback used `m.from_user.id` (undefined) → fixed to `cb.from_user.id` |
| `bot.py` | Broadcast logic duplicated → refactored into shared `_broadcast()` helper |
| `configs.py` | Hardcoded API keys/tokens/MongoDB URI → all moved to env vars |
| `database.py` | No connection error handling → added ping check + graceful exit |
| `database.py` | Used slow `len(list(find({})))` → replaced with `count_documents({})` |
| `app.py` | Flask hardcoded port → now reads `PORT` env var (required by Render) |
| `requirements.txt` | Outdated/incompatible package versions → updated for Python 3.10 |
| `Dockerfile` | `python:3.10.8` tag doesn't exist → changed to `python:3.10-slim` |

---

## 🏷 Environment Variables

Set these in Render → Environment:

| Variable | Description |
|----------|-------------|
| `API_ID` | Telegram API ID from [my.telegram.org](https://my.telegram.org) |
| `API_HASH` | Telegram API Hash from [my.telegram.org](https://my.telegram.org) |
| `BOT_TOKEN` | Bot token from [@BotFather](https://t.me/BotFather) |
| `CHID` | Force-subscribe channel ID (make bot admin here) |
| `SUDO` | Owner user ID(s), space-separated for multiple |
| `MONGO_URI` | MongoDB connection string |

---

## 🚀 Deploy on Render

1. Push all files to a GitHub repo.
2. Go to [render.com](https://render.com) → **New** → **Blueprint** → connect your repo.
3. Render will detect `render.yaml` automatically.
4. Set all environment variables listed above under **Environment**.
5. Click **Deploy**.

> The service type is **Worker** (not Web Service) since it's a long-running bot process.

---

## 🤖 Bot Commands

| Command | Access | Description |
|---------|--------|-------------|
| `/start` | All users | Start the bot |
| `/users` | SUDO only | Show user/group stats |
| `/bcast` | SUDO only | Broadcast (copy) a message to all users |
| `/fcast` | SUDO only | Forward a message to all users |
