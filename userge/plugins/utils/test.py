# by Kakashi_HTK

from pyrogram import filters

from userge import Message, userge


@userge.on_message(filters.incoming, filters.group, ~filters.bot, ~filters.me, group=1)
async def test(_, message: Message):
    me = await userge.get_me()
    reply = message.reply_to_message
    replied = reply.from_user.id
    if replied == me.id or ("@" + me.username) in message.text:
        await message.reply("Logging is working...")
