import os

from userge import Message, userge
from userge.helpers import msg_type


@userge.on_cmd(
    "comp",
    about={
        "header": "document to compressed media and vice versa",
        "flags": {
            "-d": "convert to document",
        },
        "usage": "{tr}comp [flag (optional)]",
    },
)
async def compress_(message: Message):
    """document to compressed media and vice versa"""
    reply_ = message.reply_to_message
    if not reply_:
        return await message.edit("`Reply to media...`", del_in=5)
    down_ = await userge.download_media(reply_)
    if "-d" in message.flags:
        await userge.send_document(
            message.chat.id, down_, reply_to_message_id=reply_.message_id
        )
        await message.delete()
        os.remove(down_)
        return
    if msg_type(reply_) == "photo":
        await userge.send_photo(
            message.chat.id, down_, reply_to_message_id=reply_.message_id
        )
    elif msg_type(reply_) == "video":
        await userge.send_video(
            message.chat.id, down_, reply_to_message_id=reply_.message_id
        )
    else:
        await reply_.reply("The replied document is not compressable...", del_in=5)
    await message.delete()
    os.remove(down_)
