from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from pyrogram import filters, Client, errors
from pyrogram.errors.exceptions.flood_420 import FloodWait
from database import (
    add_user, add_group, all_users, all_groups,
    users, remove_user,
    set_custom_text, get_custom_text, clear_custom_text,
)
from configs import cfg
import asyncio

app = Client(
    "approver",
    api_id=cfg.API_ID,
    api_hash=cfg.API_HASH,
    bot_token=cfg.BOT_TOKEN,
)

# ── Static UI ──────────────────────────────────────────────────────────────

CHANNEL_BUTTONS = InlineKeyboardMarkup([[
    InlineKeyboardButton("🗯 Channel", url="https://t.me/realearningytofficial"),
]])

START_CAPTION = (
    "**🦊 Hello {}!\n"
    "I'm an auto approve [Admin Join Requests]({}) Bot.\n"
    "I can approve users in Groups/Channels. "
    "Add me to your chat and promote me to admin with **add members** permission.\n\n"
    "__Powered By : @Gentleman_09__**"
)

DEFAULT_APPROVAL_MSG = "✅ Your join request has been approved! Welcome."

# ── Helper ─────────────────────────────────────────────────────────────────

def _approval_text() -> str:
    """Return the owner-defined custom text, or the hardcoded default."""
    return get_custom_text() or DEFAULT_APPROVAL_MSG

# ── Auto-approve ───────────────────────────────────────────────────────────

@app.on_chat_join_request(filters.group | filters.channel)
async def approve(_, m: Message):
    try:
        add_group(m.chat.id)
        await app.approve_chat_join_request(m.chat.id, m.from_user.id)
        add_user(m.from_user.id)

        # Send the DM — works even if the user never started the bot,
        # because Telegram resolves the peer from the join-request event.
        await app.send_message(m.from_user.id, _approval_text())

    except errors.PeerIdInvalid:
        # Very rare edge-case: peer truly unresolvable — skip silently.
        pass
    except errors.UserIsBlocked:
        # User has blocked the bot — nothing we can do.
        pass
    except Exception as err:
        print(f"[approve] {err}")

# ── /start ─────────────────────────────────────────────────────────────────

@app.on_message(filters.private & filters.command("start"))
async def start(_, m: Message):
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
        "https://i.ibb.co/hx5t3dV7/chat-bot-icon-virtual-smart-600nw-2478937555.jpg",
        caption=START_CAPTION.format(m.from_user.mention, "https//t.me/AutoApproveJoinRequest59Bot"),
        reply_markup=CHANNEL_BUTTONS,
    )

# ── Callback: chk ──────────────────────────────────────────────────────────

@app.on_callback_query(filters.regex("chk"))
async def chk(_, cb: CallbackQuery):
    try:
        await app.get_chat_member(cfg.CHID, cb.from_user.id)
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

    add_user(cb.from_user.id)
    await cb.edit_message_text(
        text=START_CAPTION.format(cb.from_user.mention, "https//t.me/AutoApproveJoinRequest59Bot"),
        reply_markup=CHANNEL_BUTTONS,
    )

# ── /users ─────────────────────────────────────────────────────────────────

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

# ── Custom approval text commands (SUDO only) ──────────────────────────────

@app.on_message(filters.command("addCustomText") & filters.user(cfg.SUDO))
async def add_custom_text(_, m: Message):
    """
    Usage:
      • Reply to any message  →  that message's text becomes the custom DM.
      • Or: /addCustomText Your text here
    Supports Markdown formatting in the text.
    """
    text: str | None = None

    # Priority 1: replied-to message text
    if m.reply_to_message:
        text = m.reply_to_message.text or m.reply_to_message.caption

    # Priority 2: inline text after the command
    if not text:
        parts = m.text.split(None, 1)
        if len(parts) > 1:
            text = parts[1].strip()

    if not text:
        await m.reply_text(
            "**❌ No text provided.**\n\n"
            "Usage:\n"
            "• `/addCustomText Your welcome message here`\n"
            "• Or reply to a message with `/addCustomText`\n\n"
            "**Tip:** You can use Markdown formatting — **bold**, __italic__, `code`, etc.",
            quote=True,
        )
        return

    set_custom_text(text)
    preview = text if len(text) <= 200 else text[:200] + "…"
    await m.reply_text(
        f"✅ **Custom approval message saved!**\n\n"
        f"**Preview:**\n{preview}\n\n"
        f"This message will now be sent as a DM to every approved user.",
        quote=True,
    )


@app.on_message(filters.command("viewCustomText") & filters.user(cfg.SUDO))
async def view_custom_text(_, m: Message):
    """Show the currently active approval DM text."""
    text = get_custom_text()
    if text:
        await m.reply_text(
            f"📋 **Current custom approval message:**\n\n{text}",
            quote=True,
        )
    else:
        await m.reply_text(
            f"ℹ️ No custom text set. Currently using the default message:\n\n"
            f"`{DEFAULT_APPROVAL_MSG}`",
            quote=True,
        )


@app.on_message(filters.command("clearCustomText") & filters.user(cfg.SUDO))
async def clear_custom_text_cmd(_, m: Message):
    """Remove the custom text and revert to the default approval message."""
    existing = get_custom_text()
    if not existing:
        await m.reply_text(
            "ℹ️ There is no custom text to clear. The default message is already active.",
            quote=True,
        )
        return
    clear_custom_text()
    await m.reply_text(
        f"🗑️ **Custom text cleared.**\n\n"
        f"Reverted to default:\n`{DEFAULT_APPROVAL_MSG}`",
        quote=True,
    )

# ── Broadcast helpers ──────────────────────────────────────────────────────

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

# ── Run ────────────────────────────────────────────────────────────────────

print("🤖 Bot is starting...")
app.run()
