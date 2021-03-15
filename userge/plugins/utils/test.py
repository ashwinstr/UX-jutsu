# by Kakashi_HTK

from userge import userge, Message
from pyrogram import filters

@userge.on_message(
    filters.me,
    group=1
)
async def test(_, message: Message):
    if message.text == "test" or "Test":
        await message.reply("Logging is working...")
