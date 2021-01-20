# credits: mrconfused
# imported by AshSTR

import asyncio

from userge import Config


@userge.on_message(filters.incoming & ~filters.bot)
async def gp_logger(message: Message):
    chat = message.chat.id

    if Config.PM_LOG_GROUP_ID:
        u_id = message.from_user.id
        await asyncio.sleep(5)
        if message.chat.type in ["group", "supergroup"]:
            await userge.send_message(
                Config.PM_LOG_GROUP_ID,
                f"#TAGS \n<b>Sent by : </b><a href = 'tg://user?id={u_id}'> {message.from_user.first_name}</a>\
                        \n<b>Group : </b><code>{message.chat.title}</code>\
                        \n<b>Message : </b><a href = 'https://t.me/c/{chat}/{message.message_id}'> link</a>",
                parse_mode="html",
                link_preview=True,
	    )
	    try:
                await message.forward(Config.PM_LOG_GROUP_ID, disable_notification=True)
            except FloodWait as e:
                await asyncio.sleep(e.x)
