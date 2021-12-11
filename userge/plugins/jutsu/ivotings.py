
from asyncio import gather
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from userge import Message, get_collection, userge

VOTE = get_collection("VOTES")

CHANNEL = userge.getCLogger(__name__)


@userge.on_cmd(
    "ivoting",
    about={
        "header": "inline voting buttons",
        "flags": {
            "-a": "anonymous voting",
        },
        "usage": "{tr}ivoting [reply to message]",
    },
)
async def ivote_(message: Message):
    """inline voting buttons"""
    reply_ = message.reply_to_message
    if not reply_:
        return await message.edit("`Reply to a message to vote for.`", del_in=5)
    bot_u = (await userge.bot.get_me()).username
    q = message.filtered_input_str
    query_ = f"anon_vote {q}" if "-a" in message.flags else f"voting {q}"
    res = await userge.get_inline_bot_results(bot_u, query_)
    await gather(
        message.delete(),
        userge.send_inline_bot_result(
            chat_id=message.chat.id,
            query_id=res.query_id,
            result_id=res.results[0].id,
            reply_to_message_id=reply_.message_id,
        )
    )


def vote_buttons(up_, down_, anon_, id_) -> InlineKeyboardMarkup:
    if anon_:
        btn_ = [
            [
                InlineKeyboardButton(
                    text=f"{up_} likes", callback_data=f"anon_vote_up_{id_}"
                ),
                InlineKeyboardButton(
                    text=f"{down_} dislikes", callback_data=f"anon_vote_down_{id_}"
                ),
            ],
        ]
    else:
        btn_ = [
            [
                InlineKeyboardButton(
                    text=f"{up_} likes", callback_data=f"vote_up_{id_}"
                ),
                InlineKeyboardButton(
                    text=f"{down_} dislikes", callback_data=f"vote_down_{id_}"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="List of votes.", callback_data=f"vote_list_{id_}"
                )
            ],
        ]
    return InlineKeyboardMarkup(btn_)
