# made for USERGE-X by @Kakashi_HTK(tg)/@ashwinstr(gh)

from userge import userge, Message


@userge.on_cmd(
    "fstat",
    about={
        "header": "Fstat of user",
        "description": "fetch fstat of user using @missrose_bot",
        "usage": "{tr}fstat UserID/username",
    },
)
async def f_stat(message: Message):
    """Fstat of user"""
    user_ = message.input_str
    await message.edit(f"Fetching fstat of user <b>{user_}</b>...")
    try:
        get_u = await userge.get_users(user_)
        user_ = get_u.id
    except:
        await message.edit(f"Fetching fstat of user <b>{user_}</b>...\nWARNING: User not found in your database, checking Rose's database.")
    bot_ = "MissRose_bot"
    async with userge.conversation(bot_) as conv:
        await conv.send_message("/start")
        await conv.get_response(mark_read=True)
        await conv.send_message(f"/fstat {user_}")
        resp = await conv.get_response(mark_read=True)
    fail = "Could not find a user"
    if fail in resp.text:
        await message.edit(f"User <code>{user_}</code> could not be found in @MissRose_bot database")
    else:
        await message.edit(resp.text)
