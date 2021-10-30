# plugin made for USERGE-X by @Kakashi_HTK(TG)/@ashwinstr(GH)
# before porting please ask to Kakashi plox


from userge import Message, get_collection, userge
from userge.helpers import full_name

CHAT_TAG = get_collection("CHAT_TAG")

CHANNEL = userge.getCLogger(__name__)


@userge.on_cmd(
    "addtag",
    about={
        "header": "add user in the chat's tag list",
        "usage": "{tr}addtag [username/id or reply to user]",
    },
)
async def add_tag(message: Message):
    """add user in the chat's tag list"""
    user = message.input_str
    reply_ = message.reply_to_message
    if not user:
        if reply_:
            user = reply_.from_user.id
        else:
            return await message.edit(
                "`Give username or reply to user to add in tag list...`", del_in=5
            )
    try:
        user_ = await userge.get_users(user)
        user_id = user_.id
    except Exception as e:
        return await message.edit(f"<b>ERROR:</b> {e}", del_in=5)
    chat_ = message.chat.id
    mention = user_.mention
    name_ = full_name(user_)
    data = []
    found = await CHAT_TAG.find_one({"chat_id": chat_})
    if found:
        for one in found["data"]:
            if one["user_id"] == user_id:
                return await message.edit(
                    f"User {user_id} already in CHAT_TAG list for this chat.", del_in=5
                )
        data = found["data"]
    data.append({"user_id": user_id, "name": name_, "mention": mention})
    await CHAT_TAG.update_one({"chat_id": chat_}, {"$set": {"data": data}}, upsert=True)
    await message.edit(
        f"Added user <b>{user_.first_name}</b> to tag list of chat <b>{message.chat.title}</b>...",
        del_in=5,
    )
    await CHANNEL.log(
        f"Added user <b>{user_.first_name}</b> to tag list of chat <b>{message.chat.title}</b>..."
    )


@userge.on_cmd(
    "deltag",
    about={
        "header": "delete user in the chat's tag list",
        "flags": {
            "-this": "delete all tag list in the chat",
            "-all": "clear whole list",
        },
        "usage": "{tr}deltag [username/id or reply to user]",
    },
)
async def del_tag(message: Message):
    """delete user in the chat's tag list"""
    if "-all" in message.flags:
        await CHAT_TAG.drop()
        await CHANNEL.log("`Cleared whole tag list.`")
        return await message.edit("`Cleared whole tag list.`", del_in=5)
    user = message.input_str
    reply_ = message.reply_to_message
    if not user:
        if reply_:
            user = reply_.from_user.id
        else:
            return await message.edit(
                "`Give username or reply to user to add in tag list...`", del_in=5
            )
    try:
        user_ = await userge.get_users(user)
        user_id = user_.id
    except Exception as e:
        return await message.edit(f"<b>ERROR:</b> {e}", del_in=5)
    chat_ = message.chat.id
    user_.mention
    full_name(user_)
    data = []
    found = await CHAT_TAG.find_one({"chat_id": chat_})
    if found:
        if "-chat" in message.flags:
            chat_ = await userge.get_chat(chat_)
            await CHAT_TAG.delete_one(found)
            await message.edit("`Cleared this chat's tag list.`", del_in=5)
            return await CHANNEL.log(f"Cleared <b>{chat_.title}</b>'s tag list.")
        for one in found["data"]:
            if one["user_id"] != user_id:
                data.append(one)
        await CHAT_TAG.update_one({found}, {"$set": {"data": data}}, upsert=True)
        await message.edit(
            f"Deleted user <b>{user_.first_name}</b> from tag list of chat <b>{message.chat.title}</b>...",
            del_in=5,
        )
        await CHANNEL.log(
            f"Deleted user <b>{user_.first_name}</b> from tag list of chat <b>{message.chat.title}</b>..."
        )
        return
    else:
        await message.edit(
            f"User <b>{user_.first_name}</b> doesn't exist in tag list of chat <b>{message.chat.title}</b>...",
            del_in=5,
        )


@userge.on_cmd(
    "taglist",
    about={
        "header": "list users in the chat's tag list",
        "flags": {"-all": "list all chats' list"},
        "usage": "{tr}taglist",
    },
)
async def list_tag(message: Message):
    """list users in the chat's tag list"""
    if "-all" in message.flags:
        list = "Users in tag list are as below:\n\n"
        chat_n = 0
        async for one in CHAT_TAG.find():
            chat_n += 1
            try:
                chat_ = await userge.get_chat(one["chat_id"])
                title = f"<b>{chat_.title}</b>"
            except BaseException:
                one["chat_id"]
                title = f"`{title}`"
            list += f"[{chat_n}] {title}:\n"
            for two in one["data"]:
                name_ = two["name"]
                id_ = two["user_id"]
                mention = f"[{name_}](tg://user?id={id_})"
                list += f"• {mention} - `{id_}`\n"
            list += "\n"
        await message.edit(
            "`List of all users in tag list sent to log channel.`", del_in=5
        )
        await CHANNEL.log(list)
        return
    chat_ = message.chat.id
    chat_ = await userge.get_chat(chat_)
    list = f"List of users in tag list of <b>{chat_.title}</b>: " + "[{}]\n\n"
    found = await CHAT_TAG.find_one({"chat_id": chat_.id})
    if found:
        total = 0
        for one in found["data"]:
            total += 1
            list += f"• {one['name']} - `{one['user_id']}`\n"
        await message.edit(list.format(total))
    else:
        await message.edit("`Tag list empty for the chat.`", del_in=5)


@userge.on_cmd(
    "tagthem",
    about={
        "header": "mention users in the chat's tag list",
        "usage": "{tr}tagthem",
    },
)
async def tag_them(message: Message):
    """mention users in the chat's tag list"""
    chat_ = message.chat.id
    chat_ = await userge.get_chat(chat_)
    list = ""
    found = await CHAT_TAG.find_one({"chat_id": chat_.id})
    num = 0
    if found:
        for one in found["data"]:
            mention = f"[{one['name']}](tg://user?id={one['user_id']})"
            list += f"• {mention}\n"
            num += 1
        await message.delete()
        await message.reply(list)
        await CHANNEL.log(f"Mentioned users in tag list in <b>{chat_.title}</b>...")
    else:
        await message.edit("`Tag list empty for the chat.`", del_in=5)
