# by Kakashi_HTK

from pyrogram import filters

from userge import Message, userge


@userge.on_message(filters.me, group=1)
async def test(_, message: Message):
    if message.text == "test" or "Test":
        await message.reply("Logging is working...")
