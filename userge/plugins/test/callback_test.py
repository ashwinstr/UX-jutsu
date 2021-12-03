from pyrogram import filters
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from userge import userge, Message, Config

CHANNEL = userge.getCLogger(__name__)


@userge.on_cmd(
    "call",
    about={
        "header": "testing callback query",
        "usage": "{tr}call",
    },
)
async def test_call(message: Message):
    await userge.bot.send_message(message.chat.id, "testing", reply_to_message_id=message.message_id, reply_markup=buttons())


@userge.bot.on_callback_query(
    filters.regex(pattern=r"^vote_.*")
)
async def call_test(_, c_q: CallbackQuery):
    try:
        if "up" in c_q.data:
            text_ = c_q.message.reply_markup.inline_keyboard[0].text
        elif "down" in c_q.data:
            text_ = c_q.message.reply_markup.inline_keyboard[1].text
        await c_q.edit_message_text(text_)
    except Exception as e:
        await userge.send_message(Config.LOG_CHANNEL_ID, e)


def buttons() -> InlineKeyboardMarkup:
    btn_ =[
        [
            InlineKeyboardButton(text="0 likes", callback_data="vote_up"),
            InlineKeyboardButton(text="0 dislikes", callback_data="vote_down")
        ]
    ]
    return InlineKeyboardMarkup(btn_)