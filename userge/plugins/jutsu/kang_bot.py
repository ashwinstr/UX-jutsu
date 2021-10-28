# plugin made for USERGE-X by @Kakashi_HTK(TG)/@ashwinstr(GH)
# before porting please ask to Kakashi


import io
import os
import random

from PIL import Image
from pyrogram import emoji, filters
from pyrogram.errors import StickersetInvalid, YouBlockedUser
from pyrogram.raw.functions.messages import GetStickerSet
from pyrogram.raw.types import InputStickerSetShortName

from userge import Config, Message, get_collection, userge

STICK_GROUP = int(os.environ.get("STICK_GROUP", 0))

STICK_MSG = get_collection("STICK_MSG")

StickerGroupFilter = filters.create(lambda _, __, ___: STICK_GROUP)


@userge.on_cmd(
    "kangbot",
    about={
        "header": "kang with sudo on bot mode",
        "usage": "{tr}kangbot [reply to sticker]",
    },
)
async def kang_bot(message: Message):
    """kang with sudo on bot mode"""
    if not STICK_GROUP:
        return await message.edit(
            "Add var `STICK_GROUP` with private group ID as value to kang using a tg bot...",
            del_in=5,
        )
    try:
        await userge.get_chat(STICK_GROUP)
    except BaseException:
        return await message.edit("`The provided STICK_GROUP is not a valid group...`")
    reply_ = message.reply_to_message
    if not reply_:
        return await message.edit("`Reply to sticker or image to kang...`", del_in=5)
    if not reply_.sticker:
        return await message.edit("`Reply to sticker or image to kang...`", del_in=5)
    await userge.bot.copy_message(STICK_GROUP, message.chat.id, reply_.message_id)
    bot_msg = await message.edit("`Kanging...`")
    await STICK_MSG.insert_one(
        {"chat_id": message.chat.id, "msg_id": bot_msg.message_id}
    )


@userge.on_message(filters.sticker & filters.chat([int(STICK_GROUP)]), group=1)
async def kang_on_send(_, message: Message):
    try:
        start_ = await userge.send_message(message.chat.id, "`Kanging...`")
        user = await userge.get_me()
        replied = message
        photo = None
        emoji_ = None
        is_anim = False
        resize = False
        if replied and replied.media:
            if replied.photo:
                resize = True
            elif replied.document and "image" in replied.document.mime_type:
                resize = True
            elif replied.document and "tgsticker" in replied.document.mime_type:
                is_anim = True
            elif replied.sticker:
                if not replied.sticker.file_name:
                    await start_.edit("`Sticker has no Name!`")
                    return
                emoji_ = replied.sticker.emoji
                is_anim = replied.sticker.is_animated
                if not replied.sticker.file_name.endswith(".tgs"):
                    resize = True
            else:
                await start_.edit("`Unsupported File!`")
                return
            await start_.edit(f"`{random.choice(KANGING_STR)}`")
            photo = await userge.download_media(
                message=replied, file_name=Config.DOWN_PATH
            )
        else:
            await start_.edit("`I can't kang that...`")
            return
        if photo:
            pack = 1

            if emoji_ and emoji_ not in (
                getattr(emoji, _) for _ in dir(emoji) if not _.startswith("_")
            ):
                emoji_ = None
            if not emoji_:
                emoji_ = "🤔"

            u_name = user.username
            u_name = "@" + u_name if u_name else user.first_name or user.id
            packname = f"a{user.id}_by_{user.username}_{pack}"
            custom_packnick = Config.CUSTOM_PACK_NAME or f"{u_name}'s kang pack"
            packnick = f"{custom_packnick} vol.{pack}"
            cmd = "/newpack"
            if resize:
                photo = resize_photo(photo)
            if is_anim:
                packname += "_anim"
                packnick += " (Animated)"
                cmd = "/newanimated"
            exist = False
            try:
                exist = await userge.send(
                    GetStickerSet(
                        stickerset=InputStickerSetShortName(short_name=packname)
                    )
                )
            except StickersetInvalid:
                pass
            if exist is not False:
                async with userge.conversation("Stickers", limit=30) as conv:
                    try:
                        await conv.send_message("/addsticker")
                    except YouBlockedUser:
                        await start_.edit("first **unblock** @Stickers")
                        return
                    await conv.get_response(mark_read=True)
                    await conv.send_message(packname)
                    msg = await conv.get_response(mark_read=True)
                    limit = "50" if is_anim else "120"
                    while limit in msg.text:
                        pack += 1
                        packname = f"a{user.id}_by_userge_{pack}"
                        packnick = f"{custom_packnick} Vol.{pack}"
                        if is_anim:
                            packname += "_anim"
                            packnick += " (Animated)"
                        await start_.edit(
                            "`Switching to Pack "
                            + str(pack)
                            + " due to insufficient space`"
                        )
                        await conv.send_message(packname)
                        msg = await conv.get_response(mark_read=True)
                        if msg.text == "Invalid pack selected.":
                            await conv.send_message(cmd)
                            await conv.get_response(mark_read=True)
                            await conv.send_message(packnick)
                            await conv.get_response(mark_read=True)
                            await conv.send_document(photo)
                            await conv.get_response(mark_read=True)
                            await conv.send_message(emoji_)
                            await conv.get_response(mark_read=True)
                            await conv.send_message("/publish")
                            if is_anim:
                                await conv.get_response(mark_read=True)
                                await conv.send_message(
                                    f"<{packnick}>", parse_mode=None
                                )
                            await conv.get_response(mark_read=True)
                            await conv.send_message("/skip")
                            await conv.get_response(mark_read=True)
                            await conv.send_message(packname)
                            await conv.get_response(mark_read=True)
                            out = f"[kanged](t.me/addstickers/{packname})"

                            await start_.edit(
                                f"**Sticker** {out} __in a Different Pack__**!**"
                            )
                            return
                    await conv.send_document(photo)
                    rsp = await conv.get_response(mark_read=True)
                    if "Sorry, the file type is invalid." in rsp.text:
                        await start_.edit(
                            "`Failed to add sticker, use` @Stickers "
                            "`bot to add the sticker manually.`"
                        )
                        return
                    await conv.send_message(emoji_)
                    await conv.get_response(mark_read=True)
                    await conv.send_message("/done")
                    await conv.get_response(mark_read=True)
            else:
                await start_.edit("`Brewing a new Pack...`")
                async with userge.conversation("Stickers") as conv:
                    try:
                        await conv.send_message(cmd)
                    except YouBlockedUser:
                        await start_.edit("first **unblock** @Stickers")
                        return
                    await conv.get_response(mark_read=True)
                    await conv.send_message(packnick)
                    await conv.get_response(mark_read=True)
                    await conv.send_document(photo)
                    rsp = await conv.get_response(mark_read=True)
                    if "Sorry, the file type is invalid." in rsp.text:
                        await start_.edit(
                            "`Failed to add sticker, use` @Stickers "
                            "`bot to add the sticker manually.`"
                        )
                        return
                    await conv.send_message(emoji_)
                    await conv.get_response(mark_read=True)
                    await conv.send_message("/publish")
                    if is_anim:
                        await conv.get_response(mark_read=True)
                        await conv.send_message(f"<{packnick}>", parse_mode=None)
                    await conv.get_response(mark_read=True)
                    await conv.send_message("/skip")
                    await conv.get_response(mark_read=True)
                    await conv.send_message(packname)
                    await conv.get_response(mark_read=True)
            out = f"[kanged](t.me/addstickers/{packname})"
            await start_.edit(f"**Sticker** {out}**!**")
            if os.path.exists(str(photo)):
                os.remove(photo)
        async for data in STICK_MSG.find():
            chat_ = data["chat_id"]
            msg_ = data["msg_id"]
        await userge.bot.edit_message_text(
            int(chat_), int(msg_), f"**Sticker** {out}**!**"
        )
        await STICK_MSG.drop()
    except Exception as e:
        await userge.send_message(Config.LOG_CHANNEL_ID, e)


def resize_photo(photo: str) -> io.BytesIO:
    """Resize the given photo to 512x512"""
    image = Image.open(photo)
    maxsize = 512
    scale = maxsize / max(image.width, image.height)
    new_size = (int(image.width * scale), int(image.height * scale))
    image = image.resize(new_size, Image.LANCZOS)
    resized_photo = io.BytesIO()
    resized_photo.name = "sticker.png"
    image.save(resized_photo, "PNG")
    os.remove(photo)
    return resized_photo


KANGING_STR = (
    "Using Witchery to kang this sticker...",
    "Plagiarising hehe...",
    "Inviting this sticker over to my pack...",
    "Kanging this sticker...",
    "Hey that's a nice sticker!\nMind if I kang?!..",
    "hehe me stel ur stikér\nhehe.",
    "Ay look over there (☉｡☉)!→\nWhile I kang this...",
    "Roses are red violets are blue, kanging this sticker so my pacc looks cool",
    "Imprisoning this sticker...",
    "Mr.Steal Your Sticker is stealing this sticker... ",
)
