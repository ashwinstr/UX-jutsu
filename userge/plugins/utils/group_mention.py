# credits: mrconfused
# imported by AshSTR

import asyncio
from pyrogram import filters
from userge import Config, userge
from pyrogram.errors import FloodWait
allow_gp_logger = filters.create(lambda _, __, ___: Config.PM_LOG_GROUP_ID)

@userge.on_message(allow_gp_logger & filters.incoming & filters.group & ~filters.me & ~filters.bot, group=2)
async def gp_lgger(_, message: Message):
    try:
        await userge.send_message(
            Config.PM_LOG_GROUP_ID,
            (
                f"#TAGS \nSent by : {message.from_user.mention}"
                f"\nGroup :</b> <code>{message.chat.title}</code>"
                f"\n<b>Message :</b> <a href={message.link}>link</a>",
            ),
            parse_mode="html",
         )
        await asyncio.sleep(0.5)
    except FloodWait as e:
        await asyncio.sleep(e.x + 3)


@userge.on_message()
async def gp_lgger1(_, message: Message):
    message.chat.id

    if (message.incoming or message.outgoing) and chat.type != "bot":
        if Config.PM_LOG_GROUP_ID:
            u_id = message.from_user.id
            if message.chat.type in ["private"] and chat.id != 777000:
                if message.reply_to_message.from_user.id != True:
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
