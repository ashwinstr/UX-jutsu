from asyncio import gather

from userge import userge, Message
from userge.config import Config


@userge.on_cmd(
    "jmusic",
    about={
        "header": "jio music bot downloader",
        "usage": "{tr}jmusic [song name]",
    },
)
async def jio_music(message: Message):
    bot_ = "JioDLBot"
    query_ = message.input_str
    result = await userge.get_inline_bot_results(bot_, query_)
    if not result.results:
        await message.edit(f"Song <code>{query_}</code> not found...", del_in=5)
        return
    try:
        log_ = await userge.send_inline_bot_result(
            Config.LOG_CHANNEL_ID,
            query_id=result.query_id,
            result_id=result.results[0].id
        )
        await gather(
            userge.copy_message(
                chat_id=message.chat.id,
                from_chat_id=Config.LOG_CHANNEL_ID,
                message_id=log_.updates[0].id,
            ),
            message.delete(),
        )
    except BaseException as e:
        await message.err(
            f"`Something unexpected happend.`\n<b>ERROR:</b> `{e}`", del_in=5
        )