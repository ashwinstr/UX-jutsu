# ported from catuserbot to USERGE-X by AshSTR/ashwinstr

import os
import shutil

from pyrogram.types import InputMediaPhoto

from userge import Message, userge
from userge.helpers.google_image_download import googleimagesdownload


@userge.on_cmd(
    "img",
    about={
        "header": "Fetch images from google",
        "flags": {"-l": "limit : defaults to 3"},
        "usage": "{tr}img [flag] [query] or {tr}img [flag] reply_to_message",
        "examples": ["{tr}img userge", "{tr}img -l3 userge"],
    },
)
async def img_sampler(message: Message):
    query = message.filtered_input_str or message.reply_to_message.text
    if not query:
        return await message.edit("Reply to a message or pass a query to search!")
    await message.edit("`Processing...`")
    flags_ = message.flags
    if "-l" in flags_:
        lim = flags_.get("-l", 0)
        if not str(lim).isdigit():
            await message.err('"-l" Flag only takes integers', del_in=5)
            return
        if lim > int(15):
            await message.err("limit can't be more than 15", del_in=5)
            return
    else:
        lim = int(3)
    response = googleimagesdownload()
    # creating list of arguments
    arguments = {
        "keywords": query,
        "limit": lim,
        "format": "jpg",
        "no_directory": "no_directory",
    }
    # passing the arguments to the function
    try:
        paths = response.download(arguments)
    except Exception as e:
        return await message.edit(f"Error: \n`{e}`")
    img = paths[0][query]
    media = []
    repeat = 0
    last = 1
    for a in img:
        media.append(InputMediaPhoto(media=a, caption=query))
        repeat += 1
        if repeat == (10 * last) or repeat == lim:
            if media:
                await message.client.send_media_group(message.chat.id, media)
            media = []
    shutil.rmtree(os.path.dirname(os.path.abspath(img[0])))
    await message.delete()
