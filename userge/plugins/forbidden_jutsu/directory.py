# time saving plugin for USERGE-X by @Kakashi_HTK


from pyrogram import errors as e

from userge import Message, userge
from userge.utils import post_to_telegraph as pt


@userge.on_cmd(
    "dir",
    about={
        "header": "dir any instance",
        "usage": "{tr}dir [query]",
    },
)
async def dir_(message: Message):
    """dir any instance"""
    input_ = message.input_str
    await message.edit("`Checking directory...`")
    if input_ == "errors":
        to_dir = e
    elif input_ == "userge":
        to_dir = userge
    elif input_ == "message":
        to_dir = message
    else:
        return await message.edit("`Give valid input...`")
    list_ = f"List of stuff in <b>{input_}</b> are as below...\n\n"
    for one in dir(to_dir):
        list_ += f"{one}<br>"
    link = pt(f"dir({input_})", list_)
    await message.edit(f"List of content in <b>{input_}</b> is [<b>HERE</b>]({link}).")
