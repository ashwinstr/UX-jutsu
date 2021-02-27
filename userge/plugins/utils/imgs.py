# import from oub-remix to ux by Itachi_HTK/ashwinstr

import os

from userge import Config, Message, userge


@userge.on_cmd(
    "imgs",
    about={
        "header": "Convert to image",
        "description": "Convert GIF/sticker to jpg format image",
        "usage": "{tr}img [reply to media]",
    },
)
async def img(message: Message):
    if not message.reply_to_message:
        print("Reply to media.")
        return
    await message.edit("Converting...")
    stik = message.reply_to_message.message_id
    if not os.path.isdir(Config.DOWN_PATH):
        os.makedirs(Config.DOWN_PATH)
    file_name = "stkr.jpg"
    down_dir = Config.DOWN_PATH
    down_file = os.path.join(down_dir, file_name)
    reply_message = await userge.get_messages(message.chat.id, stik)
    down_file = await userge.download_media(reply_message, down_file)
    if os.path.exists(down_file):
        pic = await userge.send_photo(
            message.chat.id,
            down_file,
            reply_to_message_id=stik,
        )
        os.remove(down_file)
    else:
        await message.edit("Can't handle that...", del_in=5)
