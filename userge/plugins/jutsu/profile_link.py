# plugin for USERGE-X by @Kakashi_HTK/@ashwinstr

from pyrogram.errors import YouBlockedUser

from userge import Message, userge


@userge.on_cmd(
    "prof",
    about={
        "header": "Get profile link",
        "description": "Get known/unknown profile link using user_id",
        "usage": "{tr}prof [user_id]",
    },
)
async def prof_ile(message: Message):
    """Get known/unknown profile links"""
    id_ = message.input_str
    if not id_:
        await message.err("Please provide user id...", del_in=5)
        return
    async with userge.conversation("missrose_bot") as conv:
        try:
            await conv.send_message(f"!info {id_}")
        except YouBlockedUser:
            await message.err("Unblock @missrose_bot first...", del_in=5)
            return
        info_ = await conv.get_response(mark_read=True)
    u_info = info_.text
    pass_ = "User info:"
    if pass_ in u_info:
        name_l = u_info.split("\n")[2]
    else:
        await message.err(
            f"Sorry, ID <code>{id_}</code> was not found in database...", del_in=5
        )
        return
    name_s = name_l.split(":")
    name = name_s[1] if (len(name_s) == 2) else "<b>Deleted account</b> (or blank name)"
    out = (
        f"<b>👤 User:</b> [{name}](tg://user?id={(id_)})\n"
        f"<b>#⃣ ID:</b> <code>{id_}</code>"
    )
    await message.edit(out)
