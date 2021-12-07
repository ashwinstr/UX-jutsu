from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from userge import Message, get_collection, userge

VOTE = get_collection("VOTES")

CHANNEL = userge.getCLogger(__name__)


@userge.on_cmd(
    "voting",
    about={
        "header": "make voting button",
        "flags": {
            "-a": "anonymous",
        },
        "usage": "{tr}voting",
    },
)
async def vote_(message: Message):
    anon = False
    if "-a" in message.flags:
        anon = True
    reply_ = message.reply_to_message
    if not reply_:
        return await message.edit("`Reply to a message to vote for.`", del_in=5)
    reply_id = reply_.message_id
    head_ = "Anonymous voting." if anon else "Voting."
    found = await VOTE.find_one({"_id": f"{message.chat.id}_{reply_id}"})
    if found:
        up = found["up"]
        down = found["down"]
        anon = found["anonymous"]
    else:
        up = []
        down = []
        await VOTE.insert_one(
            {
                "_id": f"{message.chat.id}_{reply_id}",
                "up": [],
                "down": [],
                "anonymous": anon,
            }
        )
    btn_ = vote_buttons(len(up), len(down), anon)
    if anon:
        pic_ = "https://telegra.ph/file/b23ac25afde3d6b99a591.jpg"
    else:
        pic_ = "https://telegra.ph/file/fffb70c7b824b8c4e020b.jpg"
    await userge.bot.send_photo(
        message.chat.id,
        photo=pic_,
        caption=head_,
        reply_to_message_id=reply_id,
        reply_markup=btn_,
    )


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
    rnd_id = userge.rnd_id()
    query_ = f"anon_vote_{rnd_id}" if "-a" in message.flags else f"voting_{rnd_id}"
    res = await userge.get_inline_bot_results(bot_u, query_)
    await userge.send_inline_bot_result(
        chat_id=message.chat.id,
        query_id=res.query_id,
        result_id=res.results[0].id,
        reply_to_message_id=True,
    )


def vote_buttons(up_, down_, anon_, id_) -> InlineKeyboardMarkup:
    if anon_:
        btn_ = [
            [
                InlineKeyboardButton(text=f"{up_} likes", callback_data=f"anon_vote_up_{id_}"),
                InlineKeyboardButton(text=f"{down_} dislikes", callback_data=f"anon_vote_down_{id_}"),
            ],
        ]
    else:
        btn_ = [
            [
                InlineKeyboardButton(text=f"{up_} likes", callback_data=f"vote_up_{id_}"),
                InlineKeyboardButton(text=f"{down_} dislikes", callback_data=f"vote_down_{id_}"),
            ],
            [
                InlineKeyboardButton(
                    text="List of votes.", callback_data=f"vote_list_{id_}"
                )
            ],
        ]
    return InlineKeyboardMarkup(btn_)
