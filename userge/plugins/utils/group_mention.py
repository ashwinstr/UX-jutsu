# credits: mrconfused
# imported by AshSTR

import asyncio

from userge import Config


@userge.on_message(filters.incoming & ~filters.bot)
async def pm_logger(_, message: Message):
    message.chat.id

    if Config.PM_LOG_GROUP_ID:
        message.from_user.id
        await asyncio.sleep(5)
        if message.chat.type in ["group", "supergroup"]:
            await userge.send_message(
                Config.PM_LOG_GROUP_ID,
                f"#TAGS \n<b>Sent by : </b><a href = 'tg://user?id={sender.id}'> {sender.first_name}</a>\
			                  \n<b>Group : </b><code>{hmm.title}</code>\
                        \n<b>Message : </b><a href = 'https://t.me/c/{hmm.id}/{event.message.id}'> link</a>",
                parse_mode="html",
                link_preview=True,
                outgoing=True,
                incoming=True,
                func=lambda e: e.mentioned,
            )


async def log_tagged_messages(event):
    hmm = await event.get_chat()

    if PM_LOGGR_BOT_API_ID:
        sender = await event.get_sender()
        await asyncio.sleep(5)
        if not event.is_private and not (await event.get_sender()).bot:
            await event.client.send_message(
                PM_LOGGR_BOT_API_ID,
                f"#TAGS \n<b>Sent by : </b><a href = 'tg://user?id={sender.id}'> {sender.first_name}</a>\
			\n<b>Group : </b><code>{hmm.title}</code>\
                        \n<b>Message : </b><a href = 'https://t.me/c/{hmm.id}/{event.message.id}'> link</a>",
                parse_mode="html",
                link_preview=True,
            )
            e = await event.client.get_entity(int(PM_LOGGR_BOT_API_ID))
            fwd_message = await event.client.forward_messages(
                e, event.message, silent=True
            )
        else:
            if event.is_private:
                if not (await event.get_chat()).bot:
                    await event.client.send_message(
                        PM_LOGGR_BOT_API_ID,
                        f"#TAGS \n<b>Sent by : </b><a href = 'tg://user?id={sender.id}'> {sender.first_name}</a>\
                                \n<b>ID : </b><code>{sender.id}</code>",
                        parse_mode="html",
                        link_preview=True,
                    )
                    e = await event.client.get_entity(int(PM_LOGGR_BOT_API_ID))
                    fwd_message = await event.client.forward_messages(
                        e, event.message, silent=True
                    )
