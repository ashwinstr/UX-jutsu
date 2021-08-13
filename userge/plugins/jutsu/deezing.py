# made for USERGE-X by @Kakashi_HTK(tg)/@ashwinstr(gh)
# v2.0.1

from asyncio import gather

from userge import Config, Message, userge
from userge.utils import capitaled


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
    song_ = await capitaled(song_)
    await message.edit(f"Searching <b>{song_}</b> on deezer...")
    results = await userge.get_inline_bot_results(bot_, song_)
    if not results.results[0]:
        await message.edit(f"Song <code>{song_}</code> not found...", del_in=5)
        return
    try:
        log_send = await userge.send_inline_bot_result(
            chat_id=Config.LOG_CHANNEL_ID,
            query_id=results.query_id,
            result_id=results.results[int(num)].id,
        )
        await gather(
            userge.copy_message(
                chat_id=message.chat.id,
                from_chat_id=Config.LOG_CHANNEL_ID,
                message_id=log_send.updates[0].id,
            ),
            message.delete(),
        )
    except BaseException:
        await message.err(
            "Something unexpected happend, please try again later...", del_in=5
        )
        return
