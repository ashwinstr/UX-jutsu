import logging
import re

from pyrogram import filters
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from userge import Config, Message, get_collection, userge

VOTE = get_collection("VOTES")

CHANNEL = userge.getCLogger(__name__)


@userge.on_cmd(
    "voting",
    about={
        "header": "make voting button",
        "usage": "{tr}voting",
    },
)
async def test_call(message: Message):
    up = "0 likes"
    down = "0 dislikes"
    await userge.bot.send_message(
        message.chat.id,
        "Voting for replied message.",
        reply_to_message_id=message.reply_to_message.message_id,
        reply_markup=buttons(up, down),
    )


@userge.bot.on_callback_query(filters.regex(pattern=r"^vote_.*"))
async def call_test(_, c_q: CallbackQuery):
    try:
        vote_msg = c_q.message.reply_to_message.message_id
        found = await VOTE.find_one({"_id": f"{c_q.message.chat.id}_{vote_msg}"})
        if not found:
            await VOTE.insert_one(
                {
                    "_id": f"{c_q.message.chat.id}_{vote_msg}",
                    "up": [],
                    "down": [],
                },
            )
            found = await VOTE.find_one({"_id": f"{c_q.message.chat.id}_{vote_msg}"})
        votes_up = found["up"]
        votes_down = found["down"]
        tapper = c_q.from_user.id
        if "up" in c_q.data:
            text_up = c_q.message.reply_markup.inline_keyboard[0][0].text
            text_down = c_q.message.reply_markup.inline_keyboard[0][1].text
            number = (re.search(r"\d+", text_up)).group(0)
            if tapper in votes_up:
                votes_up.remove(tapper)
                text_up = re.sub(r"\d+", f"{int(number) - 1}", text_up, count=1)
            else:
                votes_up.append(tapper)
                text_up = re.sub(r"\d+", f"{int(number) + 1}", text_up, count=1)
            await VOTE.update_one(
                {"_id": f"{c_q.message.chat.id}_{vote_msg}"},
                {"$set": {"up": votes_up}},
                upsert=True,
            )
        elif "down" in c_q.data:
            text_up = c_q.message.reply_markup.inline_keyboard[0][0].text
            text_down = c_q.message.reply_markup.inline_keyboard[0][1].text
            number = (re.search(r"\d+", text_down)).group(0)
            if tapper in votes_down:
                votes_down.remove(tapper)
                text_down = re.sub(r"\d+", f"{int(number) - 1}", text_down, count=1)
            else:
                votes_down.append(tapper)
                text_down = re.sub(r"\d+", f"{int(number) + 1}", text_down, count=1)
            await VOTE.update_one(
                {"_id": f"{c_q.message.chat.id}_{vote_msg}"},
                {"$set": {"down": votes_down}},
                upsert=True,
            )
        elif "list" in c_q.data:
            if c_q.from_user.id not in Config.OWNER_ID:
                return await c_q.answer(
                    "Only the bot owner can see this list.", show_alert=True
                )
            list_ = "Vote list is as below:\n\nUP_VOTES BY:\n"
            for one in found["up"]:
                try:
                    user_ = f"• {(await userge.get_users(one)).first_name}\n"
                except BaseException:
                    user_ = f"{one}\n"
                list_ += user_
            list_ += "\nDOWN_VOTES BY:\n"
            for one in found["down"]:
                try:
                    user_ = f"• {(await userge.get_users(one)).first_name}\n"
                except BaseException:
                    user_ = f"{one}\n"
                list_ += user_
            return await c_q.answer(list_, show_alert=True)
        await c_q.edit_message_text(
            "Thanks for the vote.", reply_markup=buttons(text_up, text_down)
        )
    except Exception as e:
        await userge.send_message(Config.LOG_CHANNEL_ID, e)
        logging.exception(e)
        raise


def buttons(up_, down_) -> InlineKeyboardMarkup:
    btn_ = [
        [
            InlineKeyboardButton(text=up_, callback_data="vote_up"),
            InlineKeyboardButton(text=down_, callback_data="vote_down"),
        ],
        [InlineKeyboardButton(text="List of votes.", callback_data="vote_list")],
    ]
    return InlineKeyboardMarkup(btn_)
