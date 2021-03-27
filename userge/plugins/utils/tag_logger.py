# created for USERGE-X by @Kakashi_HTK/@ashwinstr

import asyncio

import aiofiles
import ujson
from pyrogram import filters
from pyrogram.errors import FloodWait

from userge import Config, Message, get_collection, userge

SAVED_SETTINGS = get_collection("CONFIGS")


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
    """ enable / disable [all Logger] """
    if not Config.TAG_LOGGING:
        return await message.edit(
            "Add <code>TAG_LOGGING = False</code> in config.py file...",
            del_in=5,
        )
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
    filters.group & ~filters.bot & ~filters.me & tagLoggingFilter,
)
async def grp_log(_, message: Message):
    if not Config.PM_LOG_GROUP_ID:
        return
    reply = message.reply_to_message
    sender = " ".join([message.from_user.first_name, message.from_user.last_name or ""])
    sender_id = message.from_user.id
    sender_m = f"<a href='tg://user?id={sender_id}'>{sender}</a>"
    log1 = f"""
↪️ #REPLIED
👤 <b>Replied by :</b> {sender_m}
🔢 <b>ID :</b> <code>{sender_id}</code>
👥 <b>Group :</b> {message.chat.title}
🔗 <b>Message link :</b> <a href={message.link}>link</a>
💬 <b>Message :</b> ⬇
"""
    log2 = f"""
#⃣ #TAGS
👤 <b>Sent by :</b> {sender_m}
🔢 <b>ID :</b> <code>{sender_id}</code>
👥 <b>Group :</b> {message.chat.title}
🔗 <b>Message link :</b> <a href={message.link}>link</a>
💬 <b>Message :</b> ⬇
"""
    if reply:
        sender_m_id = message.message_id
        replied = reply.from_user.id
        replied_m_id = reply.message_id
        me_id = user(info="id")
        if replied == me_id:
            try:
                await asyncio.sleep(0.5)
                fwd = await userge.forward_messages(
                    Config.PM_LOG_GROUP_ID,
                    message.chat.id,
                    message_ids=replied_m_id,
                )
                await userge.send_message(
                    Config.PM_LOG_GROUP_ID,
                    log1,
                    parse_mode="html",
                    reply_to_message_id=fwd.message_id,
                    disable_web_page_preview=True,
                )
                await userge.forward_messages(
                    Config.PM_LOG_GROUP_ID, message.chat.id, message_ids=sender_m_id
                )
            except FloodWait as e:
                await asyncio.sleep(e.x + 3)
    mention = f"""@{user(info="username")}"""
    text = message.text or message.caption
    if text and mention in text:
        text_id = message.message_id 
        try:
            await asyncio.sleep(0.5)
            await userge.send_message(
                Config.PM_LOG_GROUP_ID,
                log2,
                parse_mode="html",
                disable_web_page_preview=True,
            )
            await asyncio.sleep(0.5)
            await userge.forward_messages(
                Config.PM_LOG_GROUP_ID, message.chat.id, message_ids=text_id
            )
        except FloodWait as e:
            await asyncio.sleep(e.x + 3)


@userge.on_message(
    filters.private & ~filters.bot & ~filters.edited & tagLoggingFilter, group=5
)
async def pm_log(_, message: Message):
    sender_id = message.from_user.id
    if not Config.PM_LOG_GROUP_ID:
        return
    chat_id = message.chat.id
    chat = await userge.get_chat(chat_id)
    if chat.type == "bot":
        return
    chat_name = " ".join([chat.first_name, chat.last_name or ""])
    id = message.message_id
    log = f"""
🗣 <b>#Conversation</b> with:
🔢 <b>ID :</b> <code>{chat_id}</code>
👤 <a href="tg://user?id={chat_id}">{chat_name}</a> ⬇
"""
    try:
        me_id = user(info="id")
        if sender_id == me_id:
            await asyncio.sleep(0.5)
            await userge.send_message(
                Config.PM_LOG_GROUP_ID,
                log,
                parse_mode="html",
                disable_web_page_preview=True,
            )
        await asyncio.sleep(0.5)
        if message.reply_to_message:
            replied_id = message.reply_to_message.message_id
            fwd = await userge.forward_messages(
                Config.PM_LOG_GROUP_ID, chat_id, replied_id, disable_notification=True
            )
            await userge.send_message(
                Config.PM_LOG_GROUP_ID,
                f"↪️ #Replied with...⬇",
                reply_to_message_id=fwd.message_id,
            )
        await userge.forward_messages(
            Config.PM_LOG_GROUP_ID, chat_id, id, disable_notification=True
        )
    except FloodWait as e:
        await asyncio.sleep(e.x + 3)


def user(info):
    with open("userge/xcache/get_me.json", "r") as fp:
        data = ujson.load(fp)
    return data[info]
