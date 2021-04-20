# import from oub-remix to ux by Itachi_HTK/ashwinstr

import os

from userge import Config, Message, userge
from userge.utils import media_to_image


@userge.on_cmd(
    "imgs",
    about={
        "header": "Convert to image",
        "description": "Convert GIF/sticker/video/music_thumbnail to jpg format image",
        "usage": "{tr}imgs [reply to media]",
    },
)
async def img(message: Message):
    if not message.reply_to_message:
        await message.edit("Reply to media...", del_in=5)
        return
    reply_to = message.reply_to_message.message_id
    await message.edit("Converting...", del_in=5)
    file_name = "image.jpg"
    down_file = os.path.join(Config.DOWN_PATH, file_name)
    if os.path.isfile(down_file):
        os.remove(down_file)
    image = await media_to_image(message)
    await message.reply_photo(image, reply_to_message_id=reply_to)
