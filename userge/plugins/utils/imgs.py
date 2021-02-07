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
    message.message_id
    query = message.input_str
    if not query:
        return await message.edit("Reply to a message or pass a query to search!")
    await message.edit("`Processing...`")
    if "-l" in message.flags:
        for flag in query:
            if "-l" in flag:
                lim = flag[-1]
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
    lst = paths[0][query]
    await message.client.send_photo(message.chat.id, lst, caption=query)
    shutil.rmtree(os.path.dirname(os.path.abspath(lst[0])))
    await message.delete()
