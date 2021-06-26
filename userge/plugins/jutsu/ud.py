import asyncurban

from userge import Message, userge


@userge.on_cmd(
    "ud",
    about={
        "header": "Searches Urban Dictionary for the query",
        "usage": "{tr}ud [query] or [reply to message]",
        "examples": ["{tr}ud userge"],
    },
)
async def urban_dict(message: Message):
    word = message.input_str or message.reply_to_message.text
    urban = asyncurban.UrbanDictionary()
    try:
        mean = await urban.get_word(word)
        await message.edit(
            f"<b>Text:</b> {mean.word}\n\n<b>Meaning:</b> {mean.definition}\n\n<b>Example:</b> {mean.example}"
        )
    except asyncurban.WordNotFoundError:
        await message.edit("No result found for " + word + "")
