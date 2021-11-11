# plugin made for USERGE-X by @Kakashi_HTK(TG)/@ashwinstr(GH)
# before porting please ask to Kakashi


from asyncio import gather

from userge import Config, Message, userge
from userge.helpers import capitaled


@userge.on_cmd(
    "flac",
    about={
        "header": "download music with FlacBot",
        "description": "change quality with flac_q",
        "usage": "{tr}flac [artist and song name]",
    },
)
async def flac_bot(message: Message):
    """download music with FlacBot"""
    query_ = message.input_str
    if not query_:
        return await message.edit("`Provide input to search...`", del_in=5)
    query_ = capitaled(query_)
    await message.edit(f"Searching <b>{query_}</b> on deezer...")
    bot_ = "FlacStoreBot"
    results = await userge.get_inline_bot_results(bot_, query_)
    if not results:
        return await message.edit("`Results not found...`", del_in=5)
    log_send = await userge.send_inline_bot_result(
        chat_id=Config.LOG_CHANNEL_ID,
        query_id=results.query_id,
        result_id=results.results[0].id,
    )
    reply_ = message.reply_to_message
    if reply_:
        reply_to = reply_.message_id
    else:
        reply_to = None
    try:
        await userge.copy_message(
            chat_id=bot_,
            from_chat_id=Config.LOG_CHANNEL_ID,
            message_id=log_send.updates[0].id,
        ),
        async with userge.conversation(bot_) as conv:
            await conv.get_response(mark_read=True)
            music_ = await conv.get_response(mark_read=True)
        await userge.copy_message(message.chat.id, bot_, music_.message_id, reply_to_message_id=reply_to)
        await message.delete()
    except BaseException as e:
        await message.edit(
            f"`Something unexpected happened.`\n<b>Error:</b> `{e}`", del_in=5
        )


@userge.on_cmd(
    "flac_q",
    about={
        "header": "set quality of flacbot",
        "flags": {
            "-c": "check set quality",
        },
        "options": {
            "flac": "FLAC quality",
            "320": "MP3_320",
            "256": "MP3_256",
            "128": "MP3_128",
        },
        "usage": "{tr}flac_q flac or 320 or 256 or 128",
    },
)
async def flac_quality(message: Message):
    """set quality of flacbot"""
    bot_ = "FlacStoreBot"
    if "-c" in message.flags:
        async with userge.conversation(bot_) as conv:
            await conv.send_message("/settings")
            check = await conv.get_response(mark_read=True)
        quality_ = check.reply_markup.inline_keyboard[0][0].text
        qual = quality_.split()[1]
        await message.edit(f"`Current quality set in the bot is: {qual}`", del_in=5)
        return
    input_ = message.input_str
    if not input_:
        return await message.edit("`Provide quality to set...`", del_in=5)
    if input_ not in ['flac', '320', '256', '128']:
        return await message.edit("`Input not found in available options, see 'help flac_q'...`", del_in=5)
    if input_ == "flac":
        q_ = 0
        quality = "FLAC"
    elif input_ == "320":
        q_ = 1
        quality = "MP3_320"
    elif input_ == "256":
        q_ = 2
        quality = "MP3_256"
    else:
        q_ = 3
        quality = "MP3_128"
    await message.edit("`Changing quality...`")
    async with userge.conversation(bot_) as conv:
        try:
            await conv.send_message("/settings")
        except BaseException:
            return await message.edit("`Unblock` @FlacStoreBot `first.`", del_in=5)
        resp_one = await conv.get_response(mark_read=True)
        await resp_one.click()
        resp_two = await conv.get_response(mark_read=True)
        await resp_two.click(x=q_)
    await message.edit(f"Changed music quality to <b>{quality}</b>.", del_in=5)
