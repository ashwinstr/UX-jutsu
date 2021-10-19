# just for fun plugin for USERGE-X by @Kakashi_HTK(tg)/@ashwinstr(gh)

import asyncio

from userge import Message, userge


@userge.on_cmd(
    "dead",
    about={
        "header": "dead or alive",
        "usage": "{tr}dead",
    },
)
async def dead_(message: Message):
    """dead or alive"""
    await message.delete()
    reply_ = message.reply_to_message
    if reply_:
        reply_id = reply_.message_id
    else:
        reply_id = None
    link_ = "https://telegra.ph/file/55245d8d5cffdd6443994.mp4"
    msg_ = f"""
<b>DARE TO TEST ME MF.</b>

    🔥 <b>Status:</b> `I'm alive MF.`
    ⏱ <b>Dead since:</b> `Never died MF.`
    👤 <b>Who killed:</b> `No one dares MF.`
    🧬 <b>Why died:</b> `Nothing kills me MF.`

<b>Running at full capacity like no tomorrow MF.</b><a href='{link_}'>­</a>
"""
    send_ = await userge.send_message(
        chat_id=message.chat.id,
        text=msg_,
        reply_to_message_id=reply_id,
    )
    await asyncio.sleep(15)
    msg_ = msg_.replace("­", "")
    await send_.edit(msg_)
