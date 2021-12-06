import logging
import re

from pyrogram import filters
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from userge import Config, Message, get_collection, userge

VOTE = get_collection("VOTES")

CHANNEL = userge.getCLogger(__name__)


async def _init() -> None:
    no = 0
    async for one in VOTE.find():
        no += 1
    if no > 20:
        del_ = no - 20
        deleted = 0
        async for one in VOTE.find():
            await VOTE.delete_one(one)
            deleted += 1
            if deleted == del_:
                break


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
async def test_call(message: Message):
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
        up = "0 likes"
        down = "0 dislikes"
        await VOTE.insert_one(
            {
                "_id": f"{message.chat.id}_{reply_id}",
                "up": up,
                "down": down,
                "anonymous": anon,
            }
        )
    btn_ = vote_buttons(up, down, anon)
    await userge.bot.send_message(
        message.chat.id,
        head_,
        reply_to_message_id=reply_id,
        reply_markup=btn_,
    )


@userge.bot.on_callback_query(filters.regex(pattern=r"^vote_.*"))
async def vote_callback(_, c_q: CallbackQuery):
    try:
        vote_msg = c_q.message.reply_to_message.message_id
        found = await VOTE.find_one({"_id": f"{c_q.message.chat.id}_{vote_msg}"})
        if not found:
            return await c_q.answer(
                "This voting message has been stopped.", show_alert=True
            )
        votes_up = found["up"]
        votes_down = found["down"]
        anon = found["anonymous"]
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
        btn_ = vote_buttons(text_up, text_down, anon)
        await c_q.edit_message_text("Thanks for the vote.", reply_markup=btn_)
    except Exception as e:
        await userge.send_message(Config.LOG_CHANNEL_ID, e)
        logging.exception(e)
        raise


def vote_buttons(up_, down_, anon_) -> InlineKeyboardMarkup:
    if anon_:
        btn_ = [
            [
                InlineKeyboardButton(text=up_, callback_data="vote_up"),
                InlineKeyboardButton(text=down_, callback_data="vote_down"),
            ],
        ]
    else:
        btn_ = [
            [
                InlineKeyboardButton(text=up_, callback_data="vote_up"),
                InlineKeyboardButton(text=down_, callback_data="vote_down"),
            ],
            [InlineKeyboardButton(text="List of votes.", callback_data="vote_list")],
        ]
    return InlineKeyboardMarkup(btn_)
