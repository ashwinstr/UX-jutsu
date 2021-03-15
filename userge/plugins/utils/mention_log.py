# by Kakashi_HTK

from pyrogram import filters

from userge import Message, userge


@userge.on_message(filters.group & ~filters.bot & filters.me)
async def test(_, message: Message):
    if not Config.PM_LOG_GROUP_ID:
        return
    me = await userge.get_me()
    id = message.message_id
    reply = message.reply_to_message
    if reply:
        replied = reply.from_user.id
        if replied == me.id:
            try:
                await userge.send_message(
                    Config.PM_LOG_GROUP_ID,
                    (
                        f"#TAGS\n<b>Sent by :</b> {message.from_user.mention}\n"
                        f"<b>Group :</b> <code>{message.chat.title}</code>\n"
                        f"<b>Message :</b> <a href={message.link}>link</a>",
                    ),
                    parse_mode="html",
                )
                await userge.forward_messages(Config.PM_LOG_GROUP_ID, message.chat.id, message_ids=id)
            except FloodWait as e:
                await asyncio.sleep(e.x + 3)
    if ("@" + me.username) in message.text:
        try:
            await userge.send_message(
                Config.PM_LOG_GROUP_ID,
                (
                    f"#TAGS\n<b>Sent by :</b> {message.from_user.mention}\n"
                    f"<b>Group :</b> <code>{message.chat.title}</code>\n"
                    f"<b>Message :</b> <a href={message.link}>link</a>",
                ),
                parse_mode="html",
            )
            await userge.forward_messages(Config.PM_LOG_GROUP_ID, message.chat.id, message_ids=id)
        except FloodWait as e:
            await asyncio.sleep(e.x + 3)
