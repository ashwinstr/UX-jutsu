### Made by Ryuk ###
### based on code from ux ###

import os
import random

import requests
from nekosbest import Client, models
from pyrogram.errors import MediaEmpty, WebpageCurlFailed
from wget import download

from userge import Message, userge

client = Client()
API = os.environ.get("NEKO_API")

SFW_Tags = [tag for tag in (models.CATEGORIES)]
NSFW_Tags = requests.get(API).json()["/"]

Tags = "<b>SFW</b> :\n"
for TAG in SFW_Tags:
    Tags += f" <code>{TAG}</code>,  "
Tags += "\n\n<b>NSFW</b> : \n"
for tAg in NSFW_Tags:
    Tags += f" <code>{tAg}</code>,  "


@userge.on_cmd(
    "nekos",
    about={
        "header": "Get Nekos from nekos.best",
        "usage": "{tr}nekos for random\n{tr}nekos -nsfw for random nsfw\n{tr}nekos [Choice]",
        "Choice": Tags,
    },
)
async def neko_life(message: Message):
    choice = message.filtered_input_str
    if "-nsfw" in message.flags:
        link = (requests.get(API + random.choice(NSFW_Tags))).json()["url"]
    elif choice:
        input_choice = choice.lower()
        if input_choice in SFW_Tags:
            link = (await client.get_image(input_choice, 1)).url
        elif input_choice in NSFW_Tags:
            link = (requests.get(API + input_choice)).json()["url"]
        else:
            await message.err(
                "Choose a valid Input !, See Help for more info.", del_in=5
            )
            return
    else:
        link = (await client.get_image(random.choice(SFW_Tags), 1)).url
    await message.delete()

    try:
        await send_nekos(message, link)
    except (MediaEmpty, WebpageCurlFailed):
        link = download(link)
        await send_nekos(message, link)
        os.remove(link)


async def send_nekos(message: Message, link: str):
    reply = message.reply_to_message
    reply_id = reply.message_id if reply else None
    if link.endswith(".gif"):
        #  Bots can't use "unsave=True"
        bool_unsave = not message.client.is_bot
        await message.client.send_animation(
            chat_id=message.chat.id,
            animation=link,
            unsave=bool_unsave,
            reply_to_message_id=reply_id,
        )
    else:
        await message.client.send_photo(
            chat_id=message.chat.id, photo=link, reply_to_message_id=reply_id
        )
