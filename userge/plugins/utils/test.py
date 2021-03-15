# by Kakashi_HTK

from pyrogram import filters

from userge import Message, userge


@userge.on_message(filters.group & ~filters.bot & filters.me)
async def test(_, message: Message):
    me = await userge.get_me()
    reply = message.reply_to_message
    if reply:
        replied = reply.from_user.id
        if replied == me.id:
            await message.reply("Reply is working...")
    await message.reply(f"outside mention, @{me.username} {message.text}")
    if ("@" + me.username) in message.text:
        await message.reply("Mention is working...")
