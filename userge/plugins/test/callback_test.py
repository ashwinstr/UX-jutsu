from pyrogram import filters
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from userge import Message, userge

CHANNEL = userge.getCLogger(__name__)


@userge.on_cmd(
    "call",
    about={
        "header": "testing callback query",
        "usage": "{tr}call",
    },
)
async def test_call(message: Message):
    btn_ = InlineKeyboardMarkup(
        [[InlineKeyboardButton(text="one", callback_data="testing")]]
    )
    await userge.bot.send_message(
        message.chat.id,
        "testing",
        reply_to_message_id=message.message_id,
        reply_markup=btn_,
    )


@userge.bot.on_callback_query(filters.regex(pattern=r"^testing$"))
async def call_test(_, c_q: CallbackQuery):
    try:
        match_ = c_q
        await c_q.edit_message_text(f"{match_}\nWorking.")
    except Exception as e:
        await CHANNEL.log(e)
