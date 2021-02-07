import os
import shutil

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
    reply_id = message.message_id
    if message.reply_to_message and not message.input_str:
        query = message.reply_to_message.text
    else:
        query = message.input_str
    if not query:
        return await message.edit("Reply to a message or pass a query to search!")
    await edit("`Processing...`")
    if message.input_str.split()[1] != "":
        lim = int(message.input_str.split()[1])
        if lim > 10:
            lim = int(10)
        if lim <= 0:
            lim = int(1)
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
        return await cat.edit(f"Error: \n`{e}`")
    lst = paths[0][query]
    await message.client.send_file(message.chat.id, lst, reply_to=reply_id)
    shutil.rmtree(os.path.dirname(os.path.abspath(lst[0])))
    await message.delete()
