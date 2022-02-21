# ported from oub-remix to USERGE-X by @Kakashi_HTK/@ashwinstr

import os

from userge import Config, Message, userge


@userge.on_cmd(
    "stick",
    about={
        "header": "Image to sticker",
        "description": "Convert any image to sticker w/o sticker bot",
        "usage": "{tr}stick [reply to image]",
    },
)
async def stik_(message: Message):
    reply = message.replied
    if not reply:
        return await message.edit("`Reply to image to convert...`", del_in=5)
    await message.edit("`Converting...`")
    if reply.photo:
        name_ = "sticker.webp"
        path_ = os.path.join(Config.DOWN_PATH, name_)
        if os.path.isfile(path_):
            os.remove(path_)
        down_ = await reply.download(path_)
        await reply.reply_sticker(down_)
        os.remove(down_)
        await message.delete()
    else:
        return await message.edit("`Unsupported file.`", del_in=5)
    
