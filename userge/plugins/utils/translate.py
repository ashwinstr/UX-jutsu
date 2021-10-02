# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

import time
from json import dumps

from googletrans import LANGUAGES, Translator

from userge import Config, Message, pool, userge
from userge.utils.functions import get_emoji_regex


@userge.on_cmd(
    "tr",
    about={
        "header": "Translate the given text using Google Translate",
        "supported languages": dumps(LANGUAGES, indent=4),
        "flags": {
            "-s": "secret translation",
        },
        "usage": "from english to sinhala\n"
        "{tr}tr -en -si i am userge\n\n"
        "from auto detected language to sinhala\n"
        "{tr}tr -si i am userge\n\n"
        "from auto detected language to preferred\n"
        "{tr}tr i am userge\n\n"
        "reply to message you want to translate from english to sinhala\n"
        "{tr}tr -en -si\n\n"
        "reply to message you want to translate from auto detected language to sinhala\n"
        "{tr}tr -si\n\n"
        "reply to message you want to translate from auto detected language to preferred\n"
        "{tr}tr",
    },
    del_pre=True,
)
async def translateme(message: Message):
    text = message.filtered_input_str
    flags = message.flags
    if not text:
        reply_ = message.reply_to_message
        text = reply_.text or reply_.caption
    if not text:
        await message.err(
            text="Give a text or reply to a message to translate!\nuse `.help tr`"
        )
        return
    if len(flags) == 3:
        if "s" in flags:
            src, dest = list(flags)[1], list(flags)[2]
        else:
            await message.edit("Language flags can't be more than 2...", del_in=5)
            return
    elif len(flags) == 2:
        if "s" not in flags:
            src, dest = list(flags)
        else:
            src, dest = "auto", list(flags)[1]
    elif len(flags) == 1:
        if "s" not in flags:
            src, dest = "auto", list(flags)[0]
        else:
            src, dest = "auto", Config.LANG
    else:
        src, dest = "auto", Config.LANG
    text = get_emoji_regex().sub("", text)
    if "s" not in flags:
        await message.edit("`Translating ...`")
    try:
        reply_text = await _translate_this(text, dest, src)
    except ValueError:
        await message.err(
            text="Invalid destination language.\nuse `.help tr`"
        ) if "s" not in flags else await message.delete()
        return
    if "s" not in flags:
        source_lan = LANGUAGES[f"{reply_text.src.lower()}"]
        transl_lan = LANGUAGES[f"{reply_text.dest.lower()}"]
        output = f"**Source ({source_lan.title()}):**`\n{text}`\n\n\
**Translation ({transl_lan.title()}):**\n`{reply_text.text}`"
        caption = "translated"
    else:
        output = reply_text.text
        caption = None
    await message.edit_or_send_as_file(text=output, caption=caption)


@pool.run_in_thread
def _translate_this(text: str, dest: str, src: str):
    for i in range(10):
        try:
            return Translator().translate(text, dest=dest, src=src)
        except AttributeError:
            if i == 9:
                raise
            time.sleep(0.3)
