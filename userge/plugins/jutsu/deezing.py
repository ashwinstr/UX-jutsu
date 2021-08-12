# made for USERGE-X by @Kakashi_HTK(tg)/@ashwinstr(gh)

from asyncio import gather

from userge import userge, Message


@userge.on_cmd(
    "dz",
    about={
        "header": "deezer music",
        "description": "download music using @deezermusicbot",
        "usage": "{tr}dz [artist name] [song name] [; number](optional)",
    },
)
async def deezing_(message: Message):
    """download music using @deezermusicbot"""
    query_ = message.input_str
    if ";" in query_:
        split_ = query_.split(";", 1)
        song_, num = split_[0].strip, split_[1].strip
    else:
        song_ = query_
        num = "0"
    if not num.isdigit():
        await message.edit("Please enter a proper number after ';'...", del_in=5)
        return
    bot_ = "deezermusicbot"
    await message.edit(f"Searching <code>{song_}</code> on deezer...")
    results = await userge.get_inline_bot_results(bot_, song_)
    if not results.results[0]:
        await message.edit(f"Song <code>{song_}</code> not found...", del_in=5)
        return
    await gather(
        userge.send_inline_bot_result(
            chat_id=message.chat.id,
            query_id=results.query_id,
            result_id=results.results[num].id,
        ),
        message.delete(),
    )
