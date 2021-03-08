# Creator @midnightmadwalk to be found on tg
# on github as https://github.com/iMBadBoi
# improved by @Lostb053
# further improvement by @Kakashi_HTK/ashwinstr

import time
from json import dumps

from google_trans_new import google_translator
from googletrans import LANGUAGES, Translator

from userge import Message, pool, userge
from userge.plugins.utils.translate import translateme

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
    flag = message.flags
    if not x:
        await message.edit("`No input found...`")
        return
    if len(flag) > 1:
        await message.edit("`Only one flag please...`")
        return
    if len(flag) == 1:
        tran = await translateme(x)
        await message.edit("`romanising...`")
        z = translator.detect(tran)
        y = tran.split("\n")
    if not flag:
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
