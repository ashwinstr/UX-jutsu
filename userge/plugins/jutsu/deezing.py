# plugin made for USERGE-X by @Kakashi_HTK(TG)/@ashwinstr(GH)
# before porting please ask to Kakashi
# v3.0.10

from asyncio import gather

from pyrogram import filters

from userge import Config, Message, userge
from userge.helpers import capitaled


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
        await message.edit("`Please enter a proper number after ';'...`", del_in=5)
        return
    bot_ = "deezermusicbot"
    song_ = capitaled(song_)
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
            "`Something unexpected happend.`\n<b>ERROR:</b> `{e}`", del_in=5
        )


@userge.on_cmd(
    "dzlist",
    about={
        "header": "deezer music list",
        "description": "get music list from deezer"
        "\nSudo users use dz after getting the list",
        "usage": "{tr}dzlist [query]",
    },
)
async def dlist_(message: Message):
    """get list and number corresponding to songs"""
    bot_ = "deezermusicbot"
    query_ = message.input_str
    if not query_:
        await message.err("`Input not found...`", del_in=5)
        return
    query_ = capitaled(query_)
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
            min_ = f"{int(min_):02}"
            sec_ = f"{int(sec_):02}"
            list_.append(f"• [<b>{one}</b>] `{title_}` <b>({min_}:{sec_})</b>")
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
    reply_ = []
    try:
        async with userge.conversation(message.chat.id, timeout=15) as conv:
            response = await conv.get_response(
                mark_read=True, filters=(filters.user(me_.id))
            )
            resp = response.text
            resp = resp.split()
            try:
                for one in resp:
                    int(one)
                    reply_.append(one)
            except BaseException:
                proverb = "is not" if len(resp) == 1 else "are not all"
                resp = "</b>, <b>".join(resp)
                out_ += f"\n\n### The response <b>{resp}</b> {proverb} a number, <b>please retry</b>. ###"
                await response.delete()
                await message.edit(out_, del_in=15)
                return
            try:
                for one in reply_:
                    result_id = result.results[int(one)].id
            except BaseException:
                out_ += f"\n\n### Response/s <b>{reply_}</b> gave out of index error, <b>please retry</b>. ###`"
                await response.delete()
                await message.edit(out_, del_in=15)
                return
            await response.delete()
    except BaseException:
        out_ += "\n\n### <b>Response time expired.</b> ###"
        await message.edit(out_)
        return
    try:
        for one in reply_:
            result_id = result.results[int(one)].id
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
        reply_ = ", ".join(reply_)
        out_ += f"\n\n### <b>Responded with {reply_}.</b> ###"
        await message.edit(out_)
    except BaseException:
        await message.edit(
            "`Something unexpected happend.`\n<b>ERROR:</b> `{e}`", del_in=5
        )
