
import re
import traceback
from asyncio import gather

from pyrogram import filters
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQuery,
    InlineQueryResultPhoto,
    InlineQueryResultArticle,
    InputTextMessageContent,
)

from userge import Config, Message, get_collection, userge

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
        ),
    )


@userge.bot.on_callback_query(filters.regex(pattern=r"vote_.*"))
async def vote_callback(_, c_q: CallbackQuery):
    try:
        id_ = (c_q.data).split("_")[-1]
        anon = True if "anon" in c_q.data else False
        found = await VOTE.find_one({"_id": f"vote_{id_}"})
        if not found:
            await VOTE.insert_one(
                {
                    "_id": f"vote_{id_}",
                    "up": [],
                    "up_names": [],
                    "down": [],
                    "down_names": [],
                    "anonymous": anon,
                }
            )
        found = await VOTE.find_one({"_id": f"vote_{id_}"})
        votes_up = found["up"]
        votes_up_names = found["up_names"]
        votes_down = found["down"]
        votes_down_names = found["down_names"]
        anon = found["anonymous"]
        tapper = c_q.from_user.id
        if "up" in c_q.data:
            text_up = len(votes_up)
            text_down = len(votes_down)
            if tapper in votes_up:
                votes_up.remove(tapper)
                votes_up_names.remove((await userge.get_users(tapper)).first_name)
                text_up -= 1
            else:
                votes_up.append(tapper)
                votes_up_names.append((await userge.get_users(tapper)).first_name)
                text_up += 1
            await VOTE.update_one(
                {"_id": f"vote_{id_}"},
                {"$set": {"up": votes_up}},
                upsert=True,
            )
            await VOTE.update_one(
                {"_id": f"vote_{id_}"},
                {"$set": {"up_names": votes_up_names}},
                upsert=True,
            )
        elif "down" in c_q.data:
            text_up = len(votes_up)
            text_down = len(votes_down)
            if tapper in votes_down:
                votes_down.remove(tapper)
                votes_down_names.remove((await userge.get_users(tapper)).first_name)
                text_down -= 1
            else:
                votes_down.append(tapper)
                votes_down_names.append((await userge.get_users(tapper)).first_name)
                text_down += 1
            await VOTE.update_one(
                {"_id": f"vote_{id_}"},
                {"$set": {"down": votes_down}},
                upsert=True,
            )
            await VOTE.update_one(
                {"_id": f"vote_{id_}"},
                {"$set": {"down_names": votes_down_names}},
                upsert=True,
            )
        elif "list" in c_q.data:
            if (
                c_q.from_user.id not in Config.OWNER_ID
                and c_q.from_user.id not in Config.TRUSTED_SUDO_USERS
            ):
                return await c_q.answer(
                    "Only the bot owner can see this list.", show_alert=True
                )
            list_ = "𝗩𝗼𝘁𝗲 𝗹𝗶𝘀𝘁:\n\n𝗨𝗣 𝗩𝗢𝗧𝗘𝗦\n"
            for one in found["up_names"]:
                list_ += f"{one}\n"
            list_ += "\n𝗗𝗢𝗪𝗡 𝗩𝗢𝗧𝗘𝗦\n"
            for one in found["down"]:
                list_ += f"{one}\n"
            return await c_q.answer(list_, show_alert=True)
        btn_ = vote_buttons(text_up, text_down, anon, id_)
        await c_q.edit_message_reply_markup(reply_markup=btn_)
    except BaseException:
        tb = traceback.format_exc()
        await userge.send_message(Config.LOG_CHANNEL_ID, f"```{tb}```")


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


@userge.on_inline_query()
async def alive_inline_q(_, inline_query: InlineQuery):
    results = []
    i_q = inline_query.query
    str_y = i_q.split(" ", 1)
    if str_y[0] == "voting" and len(str_y) == 2:
        id_ = userge.rnd_id()
        up = 0
        down = 0
        anon = False
        tele_ = bool(
            re.search(
                r"http[s]?\:\/\/telegra\.ph\/file\/.*\.(gif|jpg|png|jpeg)$",
                str_y[1],
            )
        )
        if tele_:
            results.append(
                InlineQueryResultPhoto(
                    photo_url=str_y[1],
                    title="Vote.",
                    description="Vote your opinion.",
                    caption="Vote your opinion.",
                    reply_markup=vote_buttons(up, down, anon, id_),
                )
            )
        else:
            results.append(
                InlineQueryResultArticle(
                    title="Vote.",
                    input_message_content=InputTextMessageContent(str_y[1]),
                    description="Vote your opinion.",
                    reply_markup=vote_buttons(up, down, anon, id_),
                )
            )

    if str_y[0] == "anon_vote" and len(str_y) == 2:
        id_ = userge.rnd_id()
        up = 0
        down = 0
        anon = True
        tele_ = bool(
            re.search(
                r"http[s]?\:\/\/telegra\.ph\/file\/.*\.(gif|jpg|png|jpeg)$",
                str_y[1],
            )
        )
        if tele_:
            results.append(
                InlineQueryResultPhoto(
                    photo_url=str_y[1],
                    title="Vote.",
                    description="Vote your opinion.",
                    caption="Vote your opinion.",
                    reply_markup=vote_buttons(up, down, anon, id_),
                )
            )
        else:
            results.append(
                InlineQueryResultArticle(
                    title="Vote.",
                    input_message_content=InputTextMessageContent(str_y[1]),
                    description="Vote your opinion.",
                    reply_markup=vote_buttons(up, down, anon, id_),
                )
            )