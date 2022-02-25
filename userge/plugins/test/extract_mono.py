import re

from userge import Message, userge


@userge.on_cmd(
    "ex_mono",
    about={
        "header": "exctract mono",
        "usage": "{tr}ex_mono [reply to message]",
    },
)
async def extract_mono(message: Message):
    reply_ = message.reply_to_message
    if not reply_:
        return await message.edit("`Reply to text message...`", del_in=5)
    await message.edit("`Extracting mono text...`")
    text_ = reply_.text.html
    mono_ = re.findall(r"(\<(code|pre)\>(.|\n)*?\<\/\2\>)", text_)
    out_ = []
    for one in mono_:
        out_.append(one[0])
    await message.edit(out_)
