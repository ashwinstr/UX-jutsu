# made for USERGE-X by @Kakashi_HTK/@ashwinstr

import asyncio

from userge import Message, userge

CHANNEL = userge.getLogger(__name__)


@userge.on_cmd(
    "tc",
    about={
        "header": "Search number details",
        "description": "Get details using number with <code>@RespawnRobot</code>",
        "usage": "{tr}tc [number in international format] or [reply to number]",
        "example": "{tr}tc +12345678901",
    },
)
async def true_c_(message: Message):
    num = message.input_str
    reply = message.reply_to_message
    if not num:
        if reply:
            num = reply.text
            reply_to = reply.message_id
        else:
            await message.edit("Provide number to search...", del_in=5)
            return
    else:
        reply_to = message.message_id
    if not num.startswith("+"):
        await message.edit(
            "Provide number in <b><u>international</u></b> format...", del_in=5
        )
        return
    num_check = num.replace("+", "")
    if not num_check.isdigit():
        await message.edit("Provide a proper number...", del_in=5)
        return
    await message.edit("Searching the database...")
    bot = "@RespawnRobot"
    async with userge.conversation(bot) as conv:
        try:
            await conv.send_message("/start")
            await conv.get_response()
            await conv.send_message(num)
            await asyncio.sleep(5)
            check = await conv.get_response()
            info = check.text
            await userge.send_read_acknowledge(conv.chat_id)
        except BaseException as e:
            await message.edit(
                "Please unblock <code>@RespawnRobot</code> and try again...", del_in=5
            )
            await CHANNEL.log(e)
            return
        await userge.send_message(message.chat.id, info, reply_to_message_id=reply_to)
    await message.delete()
