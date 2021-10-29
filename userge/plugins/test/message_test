from pyrogram import filters

from userge import Config, Message, userge


@userge.on_message(filters.me & filters.chat([Config.LOG_CHANNEL_ID]))
async def testing_(_, message: Message):
    try:
        await userge.aejfna()
        await userge.send_message(Config.LOG_CHANNEL_ID, "Testing")
    except Exception:
        await userge.send_message(Config.LOG_CHANNEL_ID, "TRY worked")
