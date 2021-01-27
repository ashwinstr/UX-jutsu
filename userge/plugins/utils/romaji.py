## Creator @midnightmadwalk to be found on tg
## on github as https://github.com/iMBadBoi
## i just improvised it a lil'...phew..

from google_trans_new import google_translator
from userge import Message, userge

translator = google_translator()


@userge.on_cmd(
    "rom",
    about={
        "header": "Romaji Converter",
        "usage": "reply to message or text after cmd",
        "examples": "{tr}rom こんばんは　or　{tr}reply to msg",
    },
)
async def romaji_(message: Message):
    x = str(
        message.input_str
        or message.reply_to_message.text
        or message.reply_to_message.caption
    )
    if not x:
        await message.err("No Input Found")
    else:
        y = x.split("\n")
        result = translator.translate(y, lang_src="ja", lang_tgt="en", pronounce=True)
        k = result[1]
        if k == None:
            result = translator.translate(
                y, lang_src="en", lang_tgt="ja", pronounce=True
            )
            k = result[2]
        await message.reply(k.replace("', '", "\n").replace("['", "").replace("']", ""))
