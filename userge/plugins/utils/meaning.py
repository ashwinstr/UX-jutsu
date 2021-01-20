from PyDictionary import PyDictionary

from userge import Message, userge


@userge.on_cmd(
    "mng",
    about={
        "header": "use this to find meaning of any word.",
        "examples": [
            "{tr}mng [word] or [reply to msg]",
        ],
    },
)
async def meaning_wrd(message: Message):
    """ meaning of word """
    await message.edit("`Searching for meaning...`")
    word = message.input_str or message.reply_to_message
    if not word:
        await message.err("no input!")
    else:
        dictionary = PyDictionary()
        words = dictionary.meaning(word)
        words1 = ""
        try:
            for a, b in words.items():
                
                word1 = word1 + f"**{a}**\n"
                for i in b:
                    word1 = word1 + f"◾ __{i}__\n"
            await message.edit(output)
        except Exception:
            await message.err(f"Couldn't fetch meaning of {word}")
