# plugin made for USERGE-X by @Kakashi_HTK(TG)/@ashwinstr(GH)
# before porting please ask to Kakashi

import asyncio
import os
import time

from pyrogram import filters
from pyrogram.errors import FloodWait
from pyrogram.types import ChatPermissions

from userge import Message, get_collection, userge
from userge.helpers import admin_or_creator, full_name, msg_type

from .block_functions import (
    animation_,
    audio_,
    document_,
    media_,
    photo_,
    sticker_,
    video_,
    video_note_,
    voice_,
)

BLOCKED = get_collection("BLOCKED")
BLOCKLISTING = os.environ.get("BLOCKLISTING")


TYPES_ = [
    "audio",
    "video",
    "photo",
    "document",
    "animation",
    "sticker",
    "voice",
    "video_note",
    "media",
]

MODE_ = ["kick", "ban", "mute", "tmute", "None"]


DATA_ = {}


@userge.on_cmd(
    "bl",
    about={
        "header": "enable/disable blocklist",
        "flags": {"-c": "check blocklist toggle"},
        "usage": "{tr}bl",
    },
)
async def bl_ock(message: Message):
    """toggle blocklist"""
    if not BLOCKLISTING:
        return await message.edit("Set `BLOCKLISTING` as `True` in vars...", del_in=5)
    me_ = await userge.get_me()
    check = await admin_or_creator(message.chat.id, me_.id)
    if not check["is_admin"] and not check["is_creator"]:
        return await message.edit("`Need admin rights...`", del_in=5)
    blocking = await BLOCKED.find_one({"chat_id": message.chat.id})
    if blocking:
        block_tog = blocking["block_tog"]
    else:
        await BLOCKED.insert_one(
            {
                "chat_id": message.chat.id,
                "block_tog": True,
                "block_mode": None,
                "seconds": 0,
                "blocked": {
                    "audio": False,
                    "video": False,
                    "photo": False,
                    "document": False,
                    "animation": False,
                    "sticker": False,
                    "voice": False,
                    "video_note": False,
                    "media": False,
                },
            }
        )
        block_tog = True
    flags = message.flags
    if "-c" in flags:
        if block_tog:
            switch = "enabled"
        else:
            switch = "disabled"
        return await message.edit(f"`BLOCKLIST is {switch}.`", del_in=5)
    if block_tog:
        await BLOCKED.update_one(
            {"chat_id": message.chat.id}, {"$set": {"block_tog": False}}, upsert=True
        )
        await message.edit("`BLOCKLIST is now disabled.`", del_in=5)
    else:
        await BLOCKED.update_one(
            {"chat_id": message.chat.id}, {"$set": {"block_tog": True}}, upsert=True
        )
        await message.edit("`BLOCKLIST is now enabled.`", del_in=5)


@userge.on_cmd(
    "blmode",
    about={
        "header": "set action on bl trigger",
        "options": {
            "kick": "kick on trigger",
            "ban": "ban on trigger",
            "mute": "mute on trigger",
            "tmute": "time mute on trigger with -m(minutes) -h(hours) -d(days)",
            "None": "only delete message",
        },
        "usage": "{tr}blmode kick",
    },
)
async def bl_mode(message: Message):
    """set action on bl trigger"""
    mode = message.filtered_input_str
    if "tmute" in mode:
        flags = message.flags
        if not flags:
            return await message.edit("`Give time to tmute user...`", del_in=5)
        minutes = flags.get("-m", 0)
        hours = flags.get("-h", 0)
        days = flags.get("-d", 0)
        global _time
        if minutes:
            time = int(minutes) * 60
            _time = f"{int(minutes)}m"
        elif hours:
            time = int(hours) * 3600
            _time = f"{int(hours)}h"
        elif days:
            time = int(days) * 86400
            _time = f"{int(days)}d"
    else:
        time = 0
    if mode not in MODE_:
        return await message.edit("`Send a valid mode to set to...`", del_in=5)
    await BLOCKED.update_one(
        {"chat_id": message.chat.id}, {"$set": {"block_mode": mode}}, upsert=True
    )
    await BLOCKED.update_one(
        {"chat_id": message.chat.id}, {"$set": {"time": _time}}, upsert=True
    )
    await BLOCKED.update_one(
        {"chat_id": message.chat.id}, {"$set": {"seconds": time}}, upsert=True
    )
    await message.edit(f"BlockMode: {mode}\nTime: {_time}")


@userge.on_cmd(
    "addbl",
    about={
        "header": "add to blocklist",
        "options": TYPES_,
        "usage": "{tr}addbl [type of message]",
    },
)
async def add_bl_(message: Message):
    """add to blocklist"""
    input_ = message.input_str
    if not input_:
        return await message.edit("`Provide input to add to blocklist...`", del_in=5)
    input_ = input_.split()
    out_ = ""
    found = await BLOCKED.find_one({"chat_id": message.chat.id})
    for block in input_:
        if block not in TYPES_:
            continue
        up_block = found["blocked"]
        up_block.update({block: True})
        await BLOCKED.update_one(
            {"chat_id": message.chat.id}, {"$set": {"blocked": up_block}}, upsert=True
        )
        out_ += f"• <b>{block}</b> = True\n"
    if not out_:
        await message.edit("`Nothing has changed...`", del_in=5)
    else:
        await message.edit(f"`Changed the following:\n\n{out_}")


@userge.on_cmd(
    "delbl",
    about={"header": "remove from blocklist", "usage": "{tr}delbl [type of message]"},
)
async def add_bl_(message: Message):
    """remove from blocklist"""
    input_ = message.input_str
    if not input_:
        return await message.edit(
            "`Provide input to remove from blocklist...`", del_in=5
        )
    input_ = input_.split()
    out_ = ""
    found = await BLOCKED.find_one({"chat_id": message.chat.id})
    for block in input_:
        if block not in TYPES_:
            continue
        up_block = found["blocked"]
        up_block.update({block: False})
        await BLOCKED.update_one(
            {"chat_id": message.chat.id}, {"$set": {"blocked": up_block}}, upsert=True
        )
        out_ += f"• <b>{block}</b> = False\n"
    if not out_:
        await message.edit("`Nothing has changed...`", del_in=5)
    else:
        await message.edit(f"`Changed the following:\n\n{out_}")


@userge.on_cmd(
    "listbl",
    about={"header": "list the blocklist for current chat", "usage": "{tr}listbl"},
)
async def list_bl(message: Message):
    """list the blocklist for current chat"""
    await message.edit("`Checking blocklist...`")
    found = await BLOCKED.find_one({"chat_id": message.chat.id})
    if found:
        out_ = (
            f"### <b>BLOCKLIST for chat {message.chat.title}</b> ###\n"
            f"<b>Blocklist:</b> {found['block_tog']}\n\n"
            f"<b>Photos:</b> {found['blocked']['photo']}\n"
            f"<b>Videos:</b> {found['blocked']['video']}\n"
            f"<b>Audios:</b> {found['blocked']['audio']}\n"
            f"<b>Documents:</b> {found['blocked']['document']}\n"
            f"<b>GIFs:</b> {found['blocked']['animation']}\n"
            f"<b>Stickers:</b> {found['blocked']['sticker']}\n"
            f"<b>Voice notes:</b> {found['blocked']['voice']}\n"
            f"<b>Video notes:</b> {found['blocked']['video_note']}\n"
            f"<b>Media:</b> {found['blocked']['media']}"
        )
        await message.edit(out_)
    else:
        await message.edit("`Blocklist not enabled here...`", del_in=5)


@userge.on_cmd(
    "resetbl",
    about={"header": "reset the blocklist for current chat", "usage": "{tr}resetbl"},
)
async def reset_bl(message: Message):
    """reset the blocklist for current chat"""
    found = await BLOCKED.find_one({"chat_id": message.chat.id})
    if not found:
        return await message.edit("`Current chat not blocklisting...`", del_in=5)
    await BLOCKED.delete_one(found)
    await message.edit("`Current chat removed from blocklisting...`")


BlockFilter = filters.create(lambda _, __, ___: BLOCKLISTING)
Audio = filters.create(audio_)
Video = filters.create(video_)
Photo = filters.create(photo_)
Document = filters.create(document_)
Animation = filters.create(animation_)
Sticker = filters.create(sticker_)
Voice = filters.create(voice_)
VideoNote = filters.create(video_note_)
Media = filters.create(media_)


@userge.on_message(
    filters.group
    & ~filters.bot
    & BlockFilter
    & (
        (Audio & filters.audio)
        | (Video & filters.video)
        | (Photo & filters.photo)
        | (Document & filters.document)
        | (Animation & filters.animation)
        | (Sticker & filters.sticker)
        | (Voice & filters.voice)
        | (VideoNote & filters.video_note)
        | (Media & filters.media)
    ),
    group=1,
)
async def bl_action(_, message: Message):
    try:
        found = await BLOCKED.find_one({"chat_id": message.chat.id})
        if not found:
            return
        if not found["block_tog"]:
            return
        if found["blocked"][msg_type(message)]:
            user_ = message.from_user.id
            full_name(await userge.get_users(user_))
            chat_id = message.chat.id
            await message.delete()
            msg = await take_action(chat_id, user_)
            if found["block_mode"] == "None":
                return
            await userge.bot.send_message(message.chat.id, msg)
    except FloodWait as e:
        await asyncio.sleep(e.x + 3)


async def take_action(chat_id: int, user_id: int):
    found = await BLOCKED.find_one({"chat_id": chat_id})
    if not found:
        return
    time_ = found["seconds"]
    if found["block_mode"] == "kick":
        await userge.kick_chat_member(chat_id, user_id)
        await userge.unban_chat_member(chat_id, user_id)
        type_ = "KICKED"
    elif found["block_mode"] == "ban":
        await userge.kick_chat_member(
            chat_id, user_id, until_date=int(time.time() + time_)
        )
        type_ = "BANNED"
    elif found["block_mode"] in ["mute", "tmute"]:
        await userge.restrict_chat_member(
            chat_id, user_id, ChatPermissions(), until_date=int(time.time() + time_)
        )
        type_ = "MUTED"
        if time_ == 0:
            pass
        else:
            pass
    user_ = await userge.get_users(user_id)

    msg = (
        f"### <b>{type_}</b> ###\n"
        f"<b>USER:</b> {user_.mention} (`{user_id}`)\n"
        f"<b>FOR:</b> {found['time']}"
    )
    return msg
