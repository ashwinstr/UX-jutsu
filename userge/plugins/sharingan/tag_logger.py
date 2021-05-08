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


@userge.on_cmd(
    "tag_log",
    about={
        "header": "Toggle logging of PM and groups[all]",
        "description": "Logs all PMs and group mentions",
        "flag": {
            "-c": "Check tag_log status",
        },
        "usage": "{tr}tag_log",
    },
    allow_channels=False,
)
async def all_log(message: Message):
    """enable / disable [all Logger]"""
    if not hasattr(Config, "TAG_LOGGING"):
        setattr(Config, "TAG_LOGGING", False)
    if not Config.PM_LOG_GROUP_ID:
        return await message.edit(
            "Make a group and provide it's ID in `PM_LOG_GROUP_ID` var.",
            del_in=5,
        )
    flag = message.flags
    if "-c" in flag:
        if Config.TAG_LOGGING:
            switch = "enabled"
        else:
            switch = "disabled"
        await message.edit(f"Tag logger is {switch}...", del_in=3)
        return
    if Config.TAG_LOGGING:
        Config.TAG_LOGGING = False
        await message.edit("`Tag logger disabled !`", del_in=3)
    else:
        Config.TAG_LOGGING = True
        await message.edit("`Tag logger enabled !`", del_in=3)
    await SAVED_SETTINGS.update_one(
        {"_id": "TAG_LOGGING"}, {"$set": {"is_active": Config.TAG_LOGGING}}, upsert=True
    )


@userge.on_message(
    filters.group
    & filters.me
    & ~filters.bot
    & ~filters.service
    & ~filters.reply
    & tagLoggingFilter,
    group=5,
)
async def grp_log1(_, message: Message):
    if not GROUP_LOG_GROUP_ID:
        return
    if NO_LOG_GROUP_ID:
        if message.chat.id == NO_LOG_GROUP_ID:
            return
    dash = "==========================="
    message.message_id
    log = f"""
#⃣ #MESSAGE_SENT
👥 <b>Group :</b> {message.chat.title}
🔗 <b>Message link :</b> <a href={message.link}>link</a>
💬 <b>Message :</b> ⬇
"""
    try:
        await asyncio.sleep(0.5)
        await userge.send_message(GROUP_LOG_GROUP_ID, dash)
        await asyncio.sleep(0.5)
        await userge.send_message(
            GROUP_LOG_GROUP_ID,
            log,
            parse_mode="html",
            disable_web_page_preview=True,
        )
        await asyncio.sleep(0.5)
        await userge.forward_messages(
            GROUP_LOG_GROUP_ID,
            message.chat.id,
            message_ids=sent_m_id,
        )
    except FloodWait as e:
        await asyncio.sleep(e.x + 3)
    except MessageIdInvalid:
        pass


@userge.on_message(
    filters.group
    & ~filters.me
    & ~filters.bot
    & ~filters.service
    & filters.reply
    & tagLoggingFilter,
    group=5,
)
async def grp_log2(_, message: Message):
    if not GROUP_LOG_GROUP_ID:
        return
    if NO_LOG_GROUP_ID:
        if message.chat.id == NO_LOG_GROUP_ID:
            return
    dash = "==========================="
    try:
        sender_id = message.from_user.id
        sender_m_id = message.message_id
        reply = message.reply_to_message
        replied_id = reply.from_user.id
        replied_m_id = reply.message_id
    except BaseException:
        return
    me_id = user(info="id")
    if sender_id == me_id:
        replied_name = " ".join(
            [reply.from_user.first_name, reply.from_user.last_name or ""]
        )
        replied_men = f"<a href='tg://user?id={replied_id}'>{replied_name}</a>"
        log = f"""
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
        log = f"""
↪️ #GOT_A_REPLY
👤 <b>Replied by :</b> {sender_men}
🔢 <b>ID :</b> <code>{sender_id}</code>
👥 <b>Group :</b> {message.chat.title}
🔗 <b>Message link :</b> <a href={message.link}>link</a>
💬 <b>Message :</b> ⬇
"""
    try:
        await asyncio.sleep(0.5)
        await userge.send_message(GROUP_LOG_GROUP_ID, dash)
        await asyncio.sleep(0.5)
        replied_msg = await userge.forward_messages(
            GROUP_LOG_GROUP_ID,
            message.chat.id,
            replied_m_id,
            disable_notification=True,
        )
        await asyncio.sleep(0.5)
        await userge.send_message(
            GROUP_LOG_GROUP_ID,
            log,
            reply_to_message_id=replied_msg.message_id,
            parse_mode="html",
            disable_web_page_preview=True,
        )
        await asyncio.sleep(0.5)
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


@userge.on_message(
    filters.group
    & filters.mentioned
    & ~filters.me
    & ~filters.bot
    & ~filters.service
    & tagLoggingFilter,
    group=5,
)
async def grp_log3(_, message: Message):
    if not GROUP_LOG_GROUP_ID:
        return
    if NO_LOG_GROUP_ID:
        if message.chat.id == NO_LOG_GROUP_ID:
            return
    dash = "==========================="
    me_username = f'@{user(info="username")}'
    if not (message and message.text):
        return
    text_ = message.text or message.caption
    if text_ and me_username in text_:
        text_id = message.message_id
        sender_name = " ".join(
            [message.from_user.first_name, message.from_user.last_name or ""]
        )
        sender_men = f"<a href='tg://user?id={sender_id}'>{sender_name}</a>"
        log = f"""
#⃣ #TAGS
👤 <b>Sent by :</b> {sender_men}
🔢 <b>ID :</b> <code>{sender_id}</code>
👥 <b>Group :</b> {message.chat.title}
🔗 <b>Message link :</b> <a href={message.link}>link</a>
💬 <b>Message :</b> ⬇
"""
        try:
            await asyncio.sleep(0.5)
            await userge.send_message(GROUP_LOG_GROUP_ID, dash)
            await asyncio.sleep(0.5)
            await userge.send_message(
                GROUP_LOG_GROUP_ID,
                log,
                parse_mode="html",
                disable_web_page_preview=True,
            )
            await asyncio.sleep(0.5)
            await userge.forward_messages(
                GROUP_LOG_GROUP_ID, message.chat.id, message_ids=text_id
            )
        except FloodWait as e:
            await asyncio.sleep(e.x + 3)
        except MessageIdInvalid:
            pass


def user(info):
    with open("userge/xcache/get_me.json", "r") as fp:
        data = ujson.load(fp)
    return data[info]
