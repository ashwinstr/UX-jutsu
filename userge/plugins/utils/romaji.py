## Creator @midnightmadwalk to be found on tg
## on github as https://github.com/iMBadBoi
## improved by @Lostb053
## further improvement by @Kakashi_HTK/ashwinstr

import asyncio
import time
from json import dumps

from google_trans_new import google_translator
from googletrans import LANGUAGES

from userge import Message, pool, userge
from userge.utils.functions import get_emoji_regex

translator = google_translator()


@userge.on_cmd(
    "rom",
    about={
        "header": "Romaji Converter",
        "supported languages": dumps(LANGUAGES, indent=4, sort_keys=True),
        "usage": "[reply to message or text after cmd]",
        "examples": "for other language to latin\n"
        "{tr}rom こんばんは　or　{tr}rom [reply to msg]\n\n"
        "for english to other language translation then script to latin\n"
        "{tr}rom [flag] [[text] or [reply to msg]]",
    },
)
async def romaji_(message: Message):
    x = str(
        message.input_str
        or message.reply_to_message.text
        or message.reply_to_message.caption
    )
    flag = message.flags
    if not x:
        await message.err("No Input Found")
        return
    if len(flag) > 1:
        await message.err("provide only one language flag.")
        return
    elif len(flag) == 1:
        src, dest = "auto", list(flag)[0]
        x = get_emoji_regex().sub("", x)
        await message.edit("`Translating ...`")
        try:
            reply_text = await _translate_this(text, dest, src)
        except ValueError:
            await message.err(text="Invalid destination language.\nuse `.help tr`")
            return
        LANGUAGES[f"{reply_text.dest.lower()}"]
        tran = f"`{reply_text.text}`"
        if len(tran) <= 4096:
            await message.edit(tran)
        else:
            await message.err("too much text.")
            return
        await asyncio.sleep(1)
    await message.edit("`romanising...`")
    z = translator.detect(tran)
    y = tran.split("\n")
    result = translator.translate(y, lang_src=z, lang_tgt="en", pronounce=True)
    k = result[1]
    if k == None:
        result = translator.translate(y, lang_src="en", lang_tgt="ja", pronounce=True)
        k = result[2]
    await message.reply(k.replace("', '", "\n").replace("['", "").replace("']", ""))


@pool.run_in_thread
def _translate_this(text: str, dest: str, src: str):
    for i in range(10):
        try:
            return Translator().translate(text, dest=dest, src=src)
        except AttributeError:
            if i == 9:
                raise
            time.sleep(0.3)
