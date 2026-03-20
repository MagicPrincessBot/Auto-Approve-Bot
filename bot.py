from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from pyrogram import filters, Client, errors
from pyrogram.errors.exceptions.flood_420 import FloodWait
from database import add_user, add_group, all_users, all_groups, users, remove_user
from configs import cfg
import asyncio

app = Client(
    "approver",
    api_id=cfg.API_ID,
    api_hash=cfg.API_HASH,
    bot_token=cfg.BOT_TOKEN,
)

CHANNEL_BUTTONS = InlineKeyboardMarkup(
    [[
        InlineKeyboardButton("🗯 Channel", url="https://t.me/bot_test_channel"),
        InlineKeyboardButton("💬 Support", url="https://t.me/vj_bot_disscussion"),
    ]]
)

START_CAPTION = (
    "**🦊 Hello {}!\n"
    "I'm an auto approve [Admin Join Requests]({}) Bot.\n"
    "I can approve users in Groups/Channels. "
    "Add me to your chat and promote me to admin with **add members** permission.\n\n"
    "__Powered By : @Gentleman_09__**"
)

# ─────────────────────────────── Auto-approve ────────────────────────────────

@app.on_chat_join_request(filters.group | filters.channel)
async def approve(_, m: Message):
    try:
        add_group(m.chat.id)
        await app.approve_chat_join_request(m.chat.id, m.from_user.id)
        add_user(m.from_user.id)
        await app.send_message(
            m.from_user.id,
            "✅ Your join request has been approved! Welcome."
        )
    except errors.PeerIdInvalid:
        # User hasn't started the bot yet — silently skip DM
        pass
    except Exception as err:
        print(f"[approve] {err}")

# ─────────────────────────────── /start ──────────────────────────────────────

@app.on_message(filters.private & filters.command("start"))
async def start(_, m: Message):
    # Force-subscribe check
    try:
        await app.get_chat_member(cfg.CHID, m.from_user.id)
    except errors.UserNotParticipant:
        try:
            invite_link = await app.create_chat_invite_link(int(cfg.CHID))
        except Exception:
            await m.reply("**Make sure I am an admin in your channel.**")
            return
        key = InlineKeyboardMarkup([[
            InlineKeyboardButton("🍿 Join Update Channel 🍿", url=invite_link.invite_link),
            InlineKeyboardButton("🍀 Check Again 🍀", callback_data="chk"),
        ]])
        await m.reply_text(
            "**⚠️ Access Denied!\n\n"
            "Please join my update channel to use me. "
            "After joining, tap **Check Again** to confirm.**",
            reply_markup=key,
        )
        return
    except Exception as err:
        print(f"[start] force-sub check error: {err}")

    add_user(m.from_user.id)
    await m.reply_photo(
        "https://graph.org/file/d57d6f83abb6b8d0efb02.jpg",
        caption=START_CAPTION.format(
            m.from_user.mention,
            "https://t.me/telegram/153",
        ),
        reply_markup=CHANNEL_BUTTONS,
    )

# ─────────────────────────────── Callback: chk ───────────────────────────────

@app.on_callback_query(filters.regex("chk"))
async def chk(_, cb: CallbackQuery):
    try:
        await app.get_chat_member(cfg.CHID, cb.from_user.id)  # BUG FIX: was `m.from_user.id`
    except errors.UserNotParticipant:
        await cb.answer(
            "🙅 You haven't joined the channel yet. Join first, then tap Check Again.",
            show_alert=True,
        )
        return
    except Exception as err:
        print(f"[chk] {err}")
        await cb.answer("Something went wrong. Try again later.", show_alert=True)
        return

    add_user(cb.from_user.id)  # BUG FIX: was `m.from_user.id`
    await cb.edit_message_text(
        text=START_CAPTION.format(
            cb.from_user.mention,
            "https://t.me/telegram/153",
        ),
        reply_markup=CHANNEL_BUTTONS,
    )

# ─────────────────────────────── /users ──────────────────────────────────────

@app.on_message(filters.command("users") & filters.user(cfg.SUDO))
async def stats(_, m: Message):
    u = all_users()
    g = all_groups()
    await m.reply_text(
        f"**📊 Bot Stats**\n\n"
        f"👤 Users : `{u}`\n"
        f"👥 Groups/Channels : `{g}`\n"
        f"🔢 Total : `{u + g}`"
    )

# ─────────────────────────────── /bcast ──────────────────────────────────────

async def _broadcast(m: Message, forward: bool = False):
    lel = await m.reply_text("`⚡️ Broadcasting...`")
    success = failed = deactivated = blocked = 0

    for doc in users.find():
        uid = int(doc["user_id"])
        try:
            if forward:
                await m.reply_to_message.forward(uid)
            else:
                await m.reply_to_message.copy(uid)
            success += 1
        except FloodWait as ex:
            await asyncio.sleep(ex.value)
            try:
                if forward:
                    await m.reply_to_message.forward(uid)
                else:
                    await m.reply_to_message.copy(uid)
                success += 1
            except Exception:
                failed += 1
        except errors.InputUserDeactivated:
            deactivated += 1
            remove_user(uid)
        except errors.UserIsBlocked:
            blocked += 1
        except Exception as e:
            print(f"[broadcast] {e}")
            failed += 1

    await lel.edit(
        f"✅ Sent to `{success}` users.\n"
        f"❌ Failed: `{failed}`\n"
        f"🚫 Blocked: `{blocked}`\n"
        f"👻 Deactivated: `{deactivated}`"
    )


@app.on_message(filters.command("bcast") & filters.user(cfg.SUDO) & filters.reply)
async def bcast(_, m: Message):
    await _broadcast(m, forward=False)


@app.on_message(filters.command("fcast") & filters.user(cfg.SUDO) & filters.reply)
async def fcast(_, m: Message):
    await _broadcast(m, forward=True)


# ─────────────────────────────── Run ─────────────────────────────────────────

print("🤖 Bot is starting...")
app.run()
