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
    word = message.filtered_input_str
    if not word:
        await message.err(text="no input!")
        return
    try:
        dictionary = PyDictionary()
        words = dictionary.meaning(word)
        output = f"**Word :** __{word}__\n\n"
        try:
            for a, b in words.items():
                output += f"**{a}**\n"
                for i in b:
                    output += f"◾ __{i}__\n"
            await message.edit(output)
    except Exception:
        await event.edit(f"Couldn't fetch meaning of {word}")
        return
