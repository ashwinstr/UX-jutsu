# Creator @midnightmadwalk to be found on tg
# on github as https://github.com/iMBadBoi
# improved by @Lostb053
# further improvement by @Kakashi_HTK/ashwinstr

import time
from json import dumps

from google_trans_new import google_translator
from googletrans import LANGUAGES, Translator

from userge import Message, pool, userge
from userge.plugins.utils.translate import _translate_this

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
    x = message.filtered_input_str
    if message.reply_to_message:
        x = message.reply_to_message.text or message.reply_to_message.caption
    if not x:
        await message.edit("`No input found...`")
        return
    flags = message.flags
    if flag:
        flag = list(flags)[0]
        flag = flag.replace("-", "")
        if len(flags) > 1:
            await message.edit("`Only one flag please...`")
        if len(flags) == 1:
            tran = await _translate_this(x, flag, "auto")
            await message.edit("`romanising...`")
            await message.edit(
                f"**Translation...**\n{tran.text}\n\n**Pronunciation**\n{tran.pronunciation}"
            )
        return
    else:
        await message.edit("`romanising...`")
        z = translator.detect(x)
        y = x.split("\n")
    result = translator.translate(y, lang_src=z, lang_tgt="en", pronounce=True)
    k = result[1]
    if k is None:
        result = translator.translate(y, lang_src="en", lang_tgt="ja", pronounce=True)
        k = result[2]
    await message.reply(k.replace("', '", "\n").replace("['", "").replace("']", ""))


@pool.run_in_thread
def _translate_this(x: str, dest: str, src: str):
    for i in range(10):
        try:
            return Translator().translate(x, dest=dest, src=src)
        except AttributeError:
            if i == 9:
                raise
            time.sleep(0.3)
