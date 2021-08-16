from pyrogram import filters
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from userge import Config, Message, userge
from userge.utils import check_owner


@userge.on_cmd(
    "ideez",
    about={"header": "xyz", "description": "abc", "usage": "{tr}ideez,"},
)
async def ideez_er(message: Message):
    await userge.bot.get_me()
    song = "eminem till i collapse"
    bot_ = "deezermusicbot"
    x = await userge.get_inline_bot_results(bot_, song)
    if not x.results:
        await message.edit("Oops...", del_in=5)
        return
    y = await userge.send_inline_bot_result(
        Config.LOG_CHANNEL_ID, query_id=x.query_id, result_id=x.results[0].id
    )
    file_ = await userge.copy_message(
        Config.LOG_CHANNEL_ID, Config.LOG_CHANNEL_ID, y.updates[0].id
    )
    z = await userge.download_media(file_.audio.thumbs[0].file_id)
    buttons_ = [
        [
            InlineKeyboardButton(text="Previous", callback_data=f"btn_previous"),
            InlineKeyboardButton(text="Next", callback_data=f"btn_next"),
        ]
    ]
    await userge.bot.send_photo(
        message.chat.id,
        z,
        reply_markup=InlineKeyboardMarkup(buttons_),
    )


@userge.bot.on_callback_query(filters.regex(pattern=r"^btn_(previous|next)"))
@check_owner
async def test_(c_q: CallbackQuery):
    chosen_btn = c_q.matches[0].group(1)
    if chosen_btn == "next":
        await c_q.edit_message_media(
            media="downloads/photo_2021-08-16_08-05-12_6996936108293417984.jpg",
        )
