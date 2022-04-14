
# test build by Kakashi

from pyrogram import filters
from pyrogram.types import User, Chat
from pyrogram.raw.types import UpdatePeerBlocked
from pyrogram.raw.base.update import Update
from pyrogram.errors import PeerIdInvalid, UsernameInvalid, UsernameNotOccupied

from userge import userge, Config, Message, get_collection


BLOCKED_USERS = get_collection("BLOCKED_USERS")


async def _init() -> None:
    async for one in BLOCKED_USERS.find():
        Config.BLOCKED_USERS.append(one)


@userge.on_cmd(
    "block",
    about={
        "header": "block user with reason",
        "usage": "{tr}block [reply to user || user id || username] [reason]",
    },
)
async def block_ing(message: Message):
    "block user with reason"
    input_ = message.input_str
    if not input_:
        return await message.edit("`Provide a reason to block the user.`", del_in=5)
    if message.chat.type == "private":
        user_ = message.chat.id
        reason_ = input_
    else:
        reply_ = message.replied
        if reply_:
            user_ = reply_.from_user.id
            reason_ = input_
        else:
            split_ = input_.split(" ", 1)
            user_ = split_[0]
            try:
                reason_ = split_[1]
            except IndexError:
                return await message.edit("`Provide a user_id/username and reason to block.`", del_in=5)
    try:
        user_ = await userge.get_users(user_)
    except (PeerIdInvalid, UsernameNotOccupied, UsernameInvalid):
        return await message.edit(f"Provided user_id/username `{user_}` is not valid...")
    update_reason = False
    await message.edit("`Blocking user...`")
    if user_.id in Config.BLOCKED_USERS:
        try:
            async with userge.conversation(message.chat.id, timeout=15) as conv:
                confirm_ = await conv.send_message(f"User <b>{user_.first_name}</b> is already blocked.\nDo you want to update the reason? Reply `y` if you want to.")
                response = await conv.get_response(mark_read=True, filters=filters.user(Config.OWNER_ID[0]))
        except TimeoutError:
            return await confirm_.edit(str(confirm_.text) + "\n\n<b>TIMEOUT... block reason is not updated.<b>")
        if response.text not in ["y", "Y"]:
            return
        update_reason = True
    if update_reason:
        found = await BLOCKED_USERS.find({"_id": user_.id})
        if not found:
            return await message.edit("`Something unexpected happended...`", del_in=5)
        await BLOCKED_USERS.update_one(
            {"_id": user_.id}, {"$set": {"reason": reason_}}, upsert=True
        )
        action = "updated "
    else:
        dict_ = {
            "_id": user_.id,
            "data": {
                "user_name": user_.first_name,
                "username": user_.username,
            },
            "reason": reason_,
        }
        await BLOCKED_USERS.insert_one(dict_)
        await userge.block_user(user_.id)
        Config.BLOCKED_USERS.append(user_.id)
        action = ""
    await message.edit(f"User <b>@{user_.username}</b> is blocked with {action}reason <b>{reason_}</b>.")


@userge.on_cmd(
    "unblock",
    about={
        "header": "unblock user",
        "usage": "{tr}unblock [reply to user || user id || username]"
    },
    allow_channels=False
)
async def unblock_ing(message: Message):
    "unblock user"
    reply_ = message.replied
    if reply_:
        user_ = reply_.from_user.id
    else:
        user_ = message.input_str
        if not user_:
            return await message.edit("`Provide user_id/username or reply to user...`", del_in=5)
    try:
        user_ = await userge.get_users(user_)
    except (PeerIdInvalid, UsernameInvalid, UsernameNotOccupied):
        return await message.edit(f"Provided user_id/username `{user_}` is not valid...", del_in=5)
    if user_.id not in Config.BLOCKED_USERS:
        return await message.edit(f"User {user_.mention} not blocked to begin with...", del_in=5)
    await message.edit("`Unblocking user...`")
    reason_ = (await BLOCKED_USERS.find_one({"_id": user_.id}))['reason']
    try:
        async with userge.conversation(message.chat.id, timeout=15) as conv:
            confirm_ = await conv.send_message(f"User {user_.mention} is blocked with reason <b>{reason_}</b>.\nDo you want to unblock? Reply `y` if you want to.")
            response = await conv.get_response(mark_read=True, filters=filters.user(Config.OWNER_ID[0]))
    except TimeoutError:
        return await confirm_.edit(str(confirm_.text) + "\n\n<b>TIMEOUT... unblock unsuccessful.<b>")
    if response.text not in ['y', 'Y']:
        return
    await BLOCKED_USERS.delete_one({"_id": user_.id})
    Config.BLOCKED_USERS.remove(user_.id)
    await userge.unblock_user(user_.id)
    await message.edit(f"User <b>@{user_.username}</b> is unblocked now.")


# i'm noob with raw updates, any suggestion to improve the code is welcome

@userge.on_raw_update()
async def manual_block_unblock(_, update: Update, users: User, chats: Chat):
    if update is UpdatePeerBlocked:
        user_ = update.peer_id.user_id
        if update.blocked == True:
            Config.BLOCKED_USERS.append(user_)
        elif update.blocked == False:
            Config.BLOCKED_USERS.remove(user_)
        else:
            pass


@userge.on_cmd(
    "vblocked",
    about={
        "header": "see blocked user list",
        "flags": {
            "-u": "username",
            "-r": "reason"
        },
        "usage": "{tr}vblocked",
    },
    allow_channels=False,
)
async def v_block_ed(message: Message):
    await message.editt("`Fetching blocked user list...`")
    auto_blocked = "<b>Users blocked by userbot:</b> [{}]\n\n"
    auto_ = 0
    manual_blocked = "<b>Users blocked manually:</b> [{}]\n\n"
    manual_ = 0
    for one in Config.BLOCKED_USERS:
        found = await BLOCKED_USERS.find_one({"_id": one})
        if found:
            reason_ = f"for <i>{found['reason']}</i>" if "-r" in message.flags else ""
            user_ = found['data']['username'] if "-u" in message.flags else found['data']['user_name']
            auto_blocked += f"• `{found['_id']}` - <b>{user_}</b> {reason_}\n"
            auto_ +=1
        else:
            manual_blocked += f"• `{one}`\n"
            manual_ += 1
    await message.edit(f"{auto_blocked.format(auto_)}\n{manual_blocked.format(manual_)}")