# created for USERGE-X by @Kakashi_HTK/@ashwinstr


import asyncio
import os

import aiofiles
import ujson
from pyrogram import filters
from pyrogram.errors import FloodWait, MessageIdInvalid

from userge import Config, Message, get_collection, userge

SAVED_SETTINGS = get_collection("CONFIGS")

GROUP_LOG_GROUP_ID = int(os.environ.get("GROUP_LOG_GROUP_ID", 0))
NO_LOG_GROUP_ID = int(os.environ.get("NO_LOG_GROUP_ID", 0))


async def _init() -> None:
    data = await SAVED_SETTINGS.find_one({"_id": "TAG_LOGGING"})
    if data:
        Config.TAG_LOGGING = bool(data["is_active"])
    async with aiofiles.open("userge/xcache/get_me.json", "w+") as fn:
        json_data = str(await userge.get_me())
        await fn.write(json_data)


tagLoggingFilter = filters.create(lambda _, __, ___: Config.TAG_LOGGING)


@userge.on_message(
    filters.group & ~filters.bot & ~filters.service & tagLoggingFilter, group=5
)
async def grp_log(_, message: Message):
    if not GROUP_LOG_GROUP_ID:
        return
    if NO_LOG_GROUP_ID:
        if message.chat.id == NO_LOG_GROUP_ID:
            return
    dash = "==========================="
    try:
        sender_id = message.from_user.id
    except BaseException:
        return
    sender_m_id = message.message_id
    reply = message.reply_to_message
    me_id = user(info="id")
    if reply:
        replied_m_id = reply.message_id
        try:
            replied_id = reply.from_user.id
        except BaseException:
            return
        if sender_id == me_id:
            replied_name = " ".join(
                [reply.from_user.first_name, reply.from_user.last_name or ""]
            )
            replied_men = f"<a href='tg://user?id={replied_id}'>{replied_name}</a>"
            log1 = f"""
↪️ #YOU_REPLIED
👤 <b>Replied to :</b> {replied_men}
🔢 <b>ID :</b> <code>{replied_id}</code>
👥 <b>Group :</b> {message.chat.title}
🔗 <b>Message link :</b> <a href={message.link}>link</a>
💬 <b>Message :</b> ⬇
"""
        if replied_id == me_id:
            sender_name = " ".join(
                [message.from_user.first_name, message.from_user.last_name or ""]
            )
            sender_men = f"<a href='tg://user?id={sender_id}'>{sender_name}</a>"
            log1 = f"""
↪️ #GOT_A_REPLY
👤 <b>Replied by :</b> {sender_men}
🔢 <b>ID :</b> <code>{sender_id}</code>
👥 <b>Group :</b> {message.chat.title}
🔗 <b>Message link :</b> <a href={message.link}>link</a>
💬 <b>Message :</b> ⬇
"""
        if replied_id == me_id or sender_id == me_id:
            try:
                await asyncio.sleep(0.2)
                await userge.send_message(GROUP_LOG_GROUP_ID, dash)
                await asyncio.sleep(0.2)
                replied_msg = await userge.forward_messages(
                    GROUP_LOG_GROUP_ID,
                    message.chat.id,
                    replied_m_id,
                    disable_notification=True,
                )
                await asyncio.sleep(0.2)
                await userge.send_message(
                    GROUP_LOG_GROUP_ID,
                    log1,
                    reply_to_message_id=replied_msg.message_id,
                    parse_mode="html",
                    disable_web_page_preview=True,
                )
                await asyncio.sleep(0.2)
                await userge.forward_messages(
                    GROUP_LOG_GROUP_ID,
                    message.chat.id,
                    sender_m_id,
                    disable_notification=True,
                )
            except FloodWait as e:
                await asyncio.sleep(e.x + 3)
            except MessageIdInvalid:
                pass
            return
    mention = f'@{user(info="username")}'
    text = message.text or message.caption
    if text and mention in text:
        text_id = message.message_id
        sender_name = " ".join(
            [message.from_user.first_name, message.from_user.last_name or ""]
        )
        sender_men = f"<a href='tg://user?id={sender_id}'>{sender_name}</a>"
        log2 = f"""
#⃣ #TAGS
👤 <b>Sent by :</b> {sender_men}
🔢 <b>ID :</b> <code>{sender_id}</code>
👥 <b>Group :</b> {message.chat.title}
🔗 <b>Message link :</b> <a href={message.link}>link</a>
💬 <b>Message :</b> ⬇
"""
        try:
            await asyncio.sleep(0.2)
            await userge.send_message(GROUP_LOG_GROUP_ID, dash)
            await asyncio.sleep(0.2)
            await userge.send_message(
                GROUP_LOG_GROUP_ID,
                log2,
                parse_mode="html",
                disable_web_page_preview=True,
            )
            await asyncio.sleep(0.2)
            await userge.forward_messages(
                GROUP_LOG_GROUP_ID, message.chat.id, message_ids=text_id
            )
        except FloodWait as e:
            await asyncio.sleep(e.x + 3)
        except MessageIdInvalid:
            pass
        return
    if (not reply) and (sender_id == me_id):
        sent_m_id = message.message_id
        log3 = f"""
#⃣ #MESSAGE_SENT
👥 <b>Group :</b> {message.chat.title}
🔗 <b>Message link :</b> <a href={message.link}>link</a>
💬 <b>Message :</b> ⬇
"""
        try:
            await asyncio.sleep(0.2)
            await userge.send_message(GROUP_LOG_GROUP_ID, dash)
            await asyncio.sleep(0.2)
            await userge.send_message(
                GROUP_LOG_GROUP_ID,
                log3,
                parse_mode="html",
                disable_web_page_preview=True,
            )
            await asyncio.sleep(0.2)
            await userge.forward_messages(
                GROUP_LOG_GROUP_ID,
                message.chat.id,
                message_ids=sent_m_id,
            )
        except FloodWait as e:
            await asyncio.sleep(e.x + 3)
        except MessageIdInvalid:
            pass
        return


@userge.on_message(
    filters.private & ~filters.bot & ~filters.edited & tagLoggingFilter, group=5
)
async def pm_log(_, message: Message):
    sender_id = message.from_user.id
    if not Config.PM_LOG_GROUP_ID:
        return
    chat_id = message.chat.id
    if chat_id in Config.TG_IDS:
        return
    chat = await userge.get_chat(chat_id)
    if chat.type == "bot":
        return
    chat_name = " ".join([chat.first_name, chat.last_name or ""])
    id = message.message_id
    log = f"""
🗣 #CONVERSATION_WITH:
🔢 <b>ID :</b> <code>{chat_id}</code>
👤 <a href="tg://user?id={chat_id}">{chat_name}</a> ⬇
"""
    try:
        dash = "==========================="
        me_id = user(info="id")
        if sender_id == me_id and not message.reply_to_message:
            await asyncio.sleep(0.2)
            await userge.send_message(Config.PM_LOG_GROUP_ID, dash)
            await asyncio.sleep(0.2)
            await userge.send_message(
                Config.PM_LOG_GROUP_ID,
                log,
                parse_mode="html",
                disable_web_page_preview=True,
            )
            await asyncio.sleep(0.2)
            await userge.forward_messages(
                Config.PM_LOG_GROUP_ID, chat_id, id, disable_notification=True
            )
            return
        if message.reply_to_message:
            replied_id = message.reply_to_message.message_id
            await asyncio.sleep(0.2)
            await userge.send_message(Config.PM_LOG_GROUP_ID, dash)
            await asyncio.sleep(0.2)
            fwd = await userge.forward_messages(
                Config.PM_LOG_GROUP_ID, chat_id, replied_id, disable_notification=True
            )
            await asyncio.sleep(0.2)
            await userge.send_message(
                Config.PM_LOG_GROUP_ID,
                f"↪️ #REPLIED_WITH...⬇",
                reply_to_message_id=fwd.message_id,
            )
            await asyncio.sleep(0.2)
            await userge.forward_messages(
                Config.PM_LOG_GROUP_ID, chat_id, id, disable_notification=True
            )
            return
        if message.sticker:
            await userge.send_message(
                Config.PM_LOG_GROUP_ID,
                f"👤 <a href='tg://user?id={chat_id}'>{chat_name}</a> ⬇",
            )
        await asyncio.sleep(0.2)
        await userge.send_message(Config.PM_LOG_GROUP_ID, dash)
        await asyncio.sleep(0.2)
        await userge.forward_messages(
            Config.PM_LOG_GROUP_ID, chat_id, id, disable_notification=True
        )
    except FloodWait as e:
        await asyncio.sleep(e.x + 3)
    except MessageIdInvalid:
        pass


def user(info):
    with open("userge/xcache/get_me.json", "r") as fp:
        data = ujson.load(fp)
    return data[info]
