# made for USERGE-X by @Kakashi_HTK/@ashwinstr

from userge import userge, Message


@userge.on_cmd(
    "num",
    about={
        "header": "Filter numbers",
        "description": "Filter numbers from replied message",
        "usage": "{tr}num [reply to message]",
    },
)
async def num_(message: Message):
    reply = message.reply_to_message
    if not reply:
        await message.edit("Please reply to a message...", del_in=5)
        return
    msg = reply.text or reply.caption
    msg = msg.replace(",", "").replace(".", "")
    msg = msg.split()
    list = []
    total = 0
    for num in msg:
        if num.isdigit():
            total += 1
            list.append(num)
    list = "\n".join(list)
    await message.edit(
        f"<b>Filtered numbers from message</b>:[<b>{total}</b>\n"
        f"{list}"
    )
