# Creator @midnightmadwalk to be found on tg
# on github as https://github.com/iMBadBoi
# improved by @Lostb053
# further improvement by @Kakashi_HTK/ashwinstr

from json import dumps

from google_trans_new import google_translator
from googletrans import LANGUAGES

from userge import Message, userge
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
    reply = message.reply_to_message
    if reply:
        x = message.reply_to_message.text or message.reply_to_message.caption
        replied = x.message_id
    if not x:
        await message.edit("`No input found...`")
        return
    flags = message.flags
    if flags:
        flag = list(flags)[0]
        flag = flag.replace("-", "")
        if len(flags) > 1:
            await message.edit("`Only one flag please...`")
            return
        if len(flags) == 1:
            tran = await _translate_this(x, flag, "auto")
            await message.edit("`romanising...`")
            z = translator.detect(tran.text)
            y = (tran.text).split("\n")
    else:
        await message.edit("`romanising...`")
        z = translator.detect(x)
        y = x.split("\n")
    result = translator.translate(y, lang_src=z, lang_tgt="en", pronounce=True)
    k = result[1]
    if k is None:
        result = translator.translate(y, lang_src="en", lang_tgt="ja", pronounce=True)
        k = result[2]
    out = k.replace("', '", "\n").replace("['", "").replace("']", "").replace("[", "").replace("]", ".")
    if reply:
        await message.delete()
        await userge.send_message(message.chat.id, out, reply_to_message_id=replied)
    else:
        await message.edit(out)
