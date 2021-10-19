# plugin made for USERGE-X by @Kakashi_HTK(TG)/@ashwinstr(GH)
# before porting please ask to Kakashi


from pyrogram.errors import YouBlockedUser

from userge import Config, Message, userge
from userge.helpers import full_name
from userge.helpers import get_response as gr


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
        user_name = full_name(get_u)
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
    try:
        query_ = await userge.send_message(bot_, f"!fstat {user_id}")
    except YouBlockedUser:
        await message.err("Unblock @missrose_bot first...", del_in=5)
        return
    try:
        response = await gr(query_, timeout=4, mark_read=True)
    except Exception as e:
        return await message.edit(f"<b>ERROR:</b> `{e}`")
    fail = "Could not find a user"
    resp = response.text.html
    resp = resp.replace("/fbanstat", f"`{Config.CMD_TRIGGER}fbanstat`")
    if fail in resp:
        await message.edit(
            f"User <b>{user_name}</b> (<code>{user_id}</code>) could not be found in @MissRose_bot's database."
        )
    else:
        await message.edit(resp, parse_mode="html")


@userge.on_cmd(
    "fbanstat",
    about={
        "header": "check fedban details",
        "usage": "{tr}fbanstat [user ID or reply to user] [fed ID]",
    },
)
async def fban_stat(message: Message):
    """check fban details"""
    input_ = message.input_str
    reply_ = message.reply_to_message
    if input_:
        split = input_.split()
    else:
        await message.edit("`ERROR: Provide user and FedID...`", del_in=5)
        return
    if len(split) >= 2:
        user = split[0]
        fed_id = split[1]
    elif len(split) == 1:
        if reply_:
            user = reply_.from_user.id
        else:
            user = message.from_user.id
        fed_id = split[0]
    try:
        user_ = await userge.get_users(user)
    except BaseException:
        await message.edit(
            f"<b>ERROR:</b> The given user `{user}` is not valid...", del_in=5
        )
        return
    await message.edit("`Fetching fban stats...`")
    user_id = user_.id
    bot_ = "@missrose_bot"
    try:
        query_ = await userge.send_message(bot_, f"!fbanstat {user_id} {fed_id}")
    except YouBlockedUser:
        await message.err("Unblock @MissRose_bot first...")
        return
    try:
        response = await gr(query_, timeout=4, mark_read=True)
    except Exception as e:
        await message.err(e)
        return
    fail = "No fed exists"
    resp = response.text
    if fail in resp:
        await message.edit(f"<b>ERROR:</b> Fed `{fed_id}` doesn't exist.")
    else:
        await message.edit(resp.html, parse_mode="html")
