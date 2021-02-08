import os
import shutil

from pyrogram.types import InputMediaPhoto

from userge import Message, userge
from userge.img import googleimagesdownload


@userge.on_cmd(
    "imgs",
    about={
        "header": "Fetch images from google",
        "flags": {"-l": "limit : defaults to 3"},
        "usage": "{tr}imgs [flag] [query] or {tr}imgs [flag] reply_to_message",
        "examples": ["{tr}imgs userge", "{tr}imgs -l3 userge"],
    },
)
async def img_sampler(message: Message):
    query = message.filtered_input_str or message.reply_to_message.text
    if not query:
        return await message.edit(
            "Reply to a message or pass a query to search!", del_in=10
        )        
    cat = await message.edit("`Processing...`")
    lim = int(message.flags.get("-l", 3))
    if lim > 10:
        lim = int(10)
    if lim <= 0:
        lim = int(1)
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
        return await cat.edit(f"Error: \n{e}")
    lst = paths[0][query]
    await event.client.send_file(event.chat_id, lst, reply_to=reply_to_id)
    shutil.rmtree(os.path.dirname(os.path.abspath(lst[0])))
    await cat.delete()
