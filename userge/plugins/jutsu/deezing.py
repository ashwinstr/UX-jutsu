# made for USERGE-X by @Kakashi_HTK(tg)/@ashwinstr(gh)
# v3.0.5

from asyncio import gather

from pyrogram import filters

from userge import Config, Message, userge
from userge.utils import capitaled


@userge.on_cmd(
    "dz",
    about={
        "header": "deezer music",
        "description": "download music from deezer",
        "usage": "{tr}dz [artist name] [song name] [; number](optional)",
    },
)
async def deezing_(message: Message):
    """download music from deezer"""
    query_ = message.input_str
    if ";" in query_:
        split_ = query_.split(";", 1)
        song_, num = split_[0], split_[1]
    else:
        song_ = query_
        num = "0"
    try:
        num = int(num)
    except BaseException:
        await message.edit("Please enter a proper number after ';'...", del_in=5)
        return
    bot_ = "deezermusicbot"
    song_ = await capitaled(song_)
    await message.edit(f"Searching <b>{song_}</b> on deezer...")
    results = await userge.get_inline_bot_results(bot_, song_)
    if not results.results:
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


@userge.on_cmd(
    "dzlist",
    about={
        "header": "deezer music list",
        "description": "get music list from deezer",
        "usage": "{tr}dzlist [query]",
    },
)
async def dlist_(message: Message):
    """get list and number corresponding to songs"""
    bot_ = "deezermusicbot"
    query_ = message.input_str
    if not query_:
        await message.err("Input not found...", del_in=5)
        return
    query_ = await capitaled(query_)
    await message.edit(f"Searching for <b>{query_}</b>...")
    result = await userge.get_inline_bot_results(bot_, query_)
    if not result:
        await message.edit(
            f"Results not found for <code>{query_}</code>, try something else...",
            del_in=5,
        )
        return
    list_ = []
    total_ = 0
    for one in range(0, 10):
        try:
            title_ = result.results[one].document.attributes[1].file_name
            dure_ = result.results[one].document.attributes[0].duration
            min_ = dure_ / 60
            sec_ = (min_ - int(min_)) * 60
            sec_ = f"{int(sec_):02}"
            list_.append(f"• [<b>{one}</b>] {title_} <b>({int(min_)}:{int(sec_)})</b>")
            total_ += 1
        except BaseException:
            break
    if not list_:
        await message.edit(
            f"Couldn't find results for <code>{query_}</code>...", del_in=5
        )
        return
    list_ = "\n".join(list_)
    out_ = f"Results found for <b>{query_}</b>: [<b>{total_}</b>]\n\n"
    out_ += list_
    out_ += (
        "\n\nReply with corresponding number <b>within 15 seconds</b> to get the music."
    )
    await message.edit(out_)
    me_ = await userge.get_me()
    try:
        async with userge.conversation(message.chat.id, timeout=15) as conv:
            response = await conv.get_response(
                mark_read=True, filters=(filters.user(me_.id))
            )
            resp = response.text
            try:
                reply_ = int(resp)
            except BaseException:
                await conv.send_message(
                    f"The response <b>{resp}</b> is not a number, please try again..."
                )
                return
            try:
                result_id = result.results[reply_].id
            except BaseException:
                await conv.send_message(
                    "Out of index error...", reply_to_message_id=response.message_id
                )
                return
            await response.delete()
    except BaseException:
        out_ += "\n\n### <b>Response time expired.</b> ###"
        await message.edit(out_)
        return
    try:
        log_send = await userge.send_inline_bot_result(
            chat_id=Config.LOG_CHANNEL_ID,
            query_id=result.query_id,
            result_id=result_id,
        )
        await userge.copy_message(
            chat_id=message.chat.id,
            from_chat_id=Config.LOG_CHANNEL_ID,
            message_id=log_send.updates[0].id,
        )
        out_ += f"\n\n### <b>Responded with {reply_}.</b> ###"
        await message.edit(out_)
    except BaseException:
        await message.err(
            "Something unexpected happend, please try again later...", del_in=5
        )


@userge.on_cmd(
    "dzsend",
    about={
        "header": "send dzlist response",
        "description": "for sudo users who can't respond to dzlist directly",
        "usage": "{tr}dzsend [responding number]",
    },
)
async def dsend_(message: Message):
    """send dzlist response"""
    resp_ = message.input_str
    try:
        resp_ = int(resp_)
    except BaseException:
        pass
    await message.edit(resp_)
