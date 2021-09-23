# plugin made for USERGE-X by @Kakashi_HTK(tg)/@ashwinstr(gh)
# v1.0.11


from json import dumps

from googletrans import LANGUAGES, Translator

from userge import Config, Message, userge

translator = Translator()


CHANNEL = userge.getCLogger(__name__)


@userge.on_cmd(
    "pro",
    about={
        "header": "Check pronunciation",
        "description": "translate and see pronunciation of words/phrases",
        "supported languages": dumps(LANGUAGES, indent=4),
        "flags": {
            "-s": "secret transcription",
        },
        "usage": "{tr}pro [language flag] [query]",
    },
)
async def pronun_(message: Message):
    """check pronunciation"""
    flags = message.flags
    query_ = message.filtered_input_str
    if not query_:
        reply_ = message.reply_to_message
        if reply_:
            query_ = reply_.text or reply_.caption
        else:
            await message.err("`No input found...`", del_in=5)
            return
    out_ = ""
    secret = False
    no_f = False
    if "-s" in flags:
        secret = True
        if len(flags) > 3:
            await message.edit("`Maximum two language flags supported...`", del_in=5)
            return
        elif len(flags) == 3:
            if list(flags)[0] == "-s":
                src = list(flags)[1]
                dest = list(flags)[2]
            else:
                await message.edit("`Keep secret flag at start...`", del_in=5)
                return
        elif len(flags) == 2:
            if list(flags)[0] == "-s":
                src = "auto"
                dest = list(flags)[1]
            else:
                await message.edit("`Keep secret flag at start...`", del_in=5)
                return
        else:
            no_f = True
    else:
        if len(flags) > 2:
            await message.edit("`Maximum two language flags supported...`", del_in=5)
            return
        elif len(flags) == 2:
            src = list(flags)[0]
            dest = list(flags)[1]
        elif len(flags) == 1:
            src = "auto"
            dest = list(flags)[0]
        else:
            no_f = True
    if no_f:
        await message.edit("`Need a language flag to work or use translate plugin...`")
        return
    if not secret:
        await message.edit("`Transcribing...`")
    src = src.replace("-", "")
    dest = dest.replace("-", "")
    if src and dest:
        try:
            trans = translator.translate(query_, dest=dest, src=src)
            lang_dest = LANGUAGES[f"{trans.dest.lower()}"]
            lang_dest = lang_dest.title()
            lang_src = LANGUAGES[f"{trans.src.lower()}"]
            lang_src = lang_src.title()
            pronun = trans.pronunciation
        except BaseException:
            await message.edit(
                f"Language not supported, see <code>{Config.CMD_TRIGGER}help pro</code>... ",
                del_in=5,
            )
            return
    success = True
    if not pronun:
        pronun = trans.text
        success = False
    if not success:
        line_ = f"Translated text to <b>{lang_dest}</b>:"
    else:
        line_ = f"Pronunciation in <b>{lang_dest}</b>:"
    if not secret:
        out_ += (
            f"Original text from <b>{lang_src}</b>:\n"
            f"<code>{query_}</code>\n\n"
            f"{line_}\n"
            f"<code>{pronun}</code>"
        )
    else:
        out_ += pronun
        if not success:
            await CHANNEL.log(
                f"Couldn't find pronunciation for <code>{query_}</code> in <b>{lang_dest}</b>, translation done..."
            )
    await message.edit(out_)
