# credits: mrconfused
# imported by AshSTR

import asyncio

from pyrogram import filters
from userge import Config, userge


@userge.on_message(filters.incoming & ~filters.bot)
async def gp_lgger(_, message: Message):
    chat_id = message.chat.id

    if Config.PM_LOG_GROUP_ID:
        u_id = message.from_user.id
        await asyncio.sleep(5)
        if message.chat.type in ["group", "supergroup"]:
            await userge.send_message(
                Config.PM_LOG_GROUP_ID,
                f"#TAGS \n<b>Sent by : </b><a href = 'tg://user?id={u_id}'> {message.from_user.first_name}</a>\
                        \n<b>Group : </b><code>{message.chat.title}</code>\
                        \n<b>Message : </b><a href = 'https://t.me/c/{chat_id}/{message.message_id}'> link</a>",
                parse_mode="html",
                link_preview=True,
            )
            try:
                await message.forward(Config.PM_LOG_GROUP_ID, disable_notification=True)
            except FloodWait as e:
                await asyncio.sleep(e.x)


@userge.on_message((filters.incoming or filters.outgoing) & ~filters.bot)
async def gp_lgger(_, message: Message):
    message.chat.id

    if Config.PM_LOG_GROUP_ID:
        u_id = message.from_user.id
        if message.chat.type in ["private"] and chat.id != 777000:
            if u_id != self_user.id:
                global RECENT_USER
                global COUNT
                if RECENT_USER != u_id or COUNT > 4:
                    RECENT_USER = u_id
                    await userge.send_message(
                        Config.PM_LOG_GROUP_ID,
                        f"👤 {message.from_user.first_name} sent a new message.\
                            \n<b>ID : </b><code>{u_id}</code>",
                        parse_mode="html",
                        link_preview=True,
                    )
                    COUNT = 0
                COUNT = COUNT + 1
                try:
                    await message.forward(
                        Config.PM_LOG_GROUP_ID, disable_notification=True
                    )
                except FloodWait as e:
                    await asyncio.sleep(e.x)
            else:
                try:
                    await message.forward(
                        Config.PM_LOG_GROUP_ID, disable_notification=True
                    )
                except FloodWait as e:
                    await asyncio.sleep(e.x)
                await userge.send_message(
                    Config.PM_LOG_GROUP_ID,
                    "#Conversation\n"
                    + "With "
                    + f"[{chat.first_name}](tg://user?id={chat.id})",
                )
