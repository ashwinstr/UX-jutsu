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
    reply = message.reply_to_message
    if not reply:
        await message.edit("Please reply to image to convert...", del_in=5)
        return
    reply_m_id = reply.message_id
    await message.edit("Converting...")
    if not os.path.isdir(Config.DOWN_PATH):
        os.makedirs(Config.DOWN_PATH)
    file_n = "stick.webp"
    reply_img = await userge.get_messages(message.chat.id, reply_m_id)
    down_to = Config.DOWN_PATH
    down_file_n = os.path.join(down_to, file_n)
    down_file_n = await userge.download_media(reply_img, down_file_n)
    if os.path.exists(down_file_n):
        stikk = await userge.send_document(
            message.chat.id,
            down_file_n,
            force_document=False,
            reply_to_message_id=reply_m_id,
        )
        os.remove(down_file_n)
        await message.delete()
    else:
        await message.edit("Couldn't find the file...", del_in=5)
