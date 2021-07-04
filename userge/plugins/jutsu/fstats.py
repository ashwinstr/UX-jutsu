# made for USERGE-X by @Kakashi_HTK(tg)/@ashwinstr(gh)

from pyrogram.errors import YouBlockedUser

from userge import Config, Message, userge


@userge.on_cmd(
    "fstat",
    about={
        "header": "Fstat of user",
        "description": "fetch fstat of user using @missrose_bot",
        "usage": "{tr}fstat [UserID/username] or [reply to user]",
    },
)
async def f_stat(message: Message):
    """Fstat of user"""
    reply = message.reply_to_message
    user_ = message.input_str if not reply else reply.from_user.id
    if not user_:
        user_ = message.from_user.id
    try:
        get_u = await userge.get_users(user_)
        user_name = " ".join([get_u.first_name, get_u.last_name or ""])
        user_id = get_u.id
    except BaseException:
        await message.edit(
            f"Fetching fstat of user <b>{user_}</b>...\nWARNING: User not found in your database, checking Rose's database."
        )
        user_name = user_
        user_id = user_
    await message.edit(
        f"Fetching fstat of user <a href='tg://user?id={user_id}'><b>{user_name}</b></a>..."
    )
    bot_ = "MissRose_bot"
    async with userge.conversation(bot_, timeout=1000) as conv:
        try:
            await conv.send_message(f"/fstat {user_id}")
        except YouBlockedUser:
            await message.err("Unblock @missrose_bot first...", del_in=5)
            return
        response = await conv.get_response(mark_read=True)
    fail = "Could not find a user"
    resp = response.text
    if fail in resp:
        await message.edit(
            f"User <code>{user_name}</code> could not be found in @MissRose_bot's database."
        )
    else:
        await message.edit(resp.html, parse_mode="html")
