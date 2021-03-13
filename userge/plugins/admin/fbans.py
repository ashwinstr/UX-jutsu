"""Plugin to manage federations"""
# Author: Copyright (C) 2020 KenHV [https://github.com/KenHV]

# For USERGE-X
# Ported to Pyrogram + Rewrite with Mongo DB
# by: (TG - @DeletedUser420) [https://github.com/code-rgb]
# Thanks @Lostb053  for writing help
# Added proof forward and mass fban by @Kakashi_HTK/@ashwinstr

import asyncio

from pyrogram import filters
from pyrogram.errors import FloodWait, PeerIdInvalid

from userge import Config, Message, get_collection, userge

FED_LIST = get_collection("FED_LIST")
CHANNEL = userge.getCLogger(__name__)


@userge.on_cmd(
    "addf",
    about={
        "header": "Add a chat to fed list",
        "description": "Add a chat to fed list where message is to be sent",
        "usage": "{tr}addf",
    },
    allow_bots=False,
    allow_channels=False,
    allow_private=False,
)
async def addfed_(message: Message):
    """Adds current chat to connected Feds."""
    name = message.input_str or message.chat.title
    chat_id = message.chat.id
    found = await FED_LIST.find_one({"chat_id": chat_id})
    if found:
        await message.edit(
            f"Chat __ID__: `{chat_id}`\nFed: **{found['fed_name']}**\n\nAlready exists in Fed List !",
            del_in=7,
        )
        return
    await FED_LIST.insert_one({"fed_name": name, "chat_id": chat_id})
    msg_ = f"__ID__ `{chat_id}` added to Fed: **{name}**"
    await message.edit(msg_, del_in=7)
    await CHANNEL.log(msg_)


@userge.on_cmd(
    "delf",
    about={
        "header": "Remove a chat from fed list",
        "flags": {"-all": "Remove all the feds from fedlist"},
        "description": "Remove a chat from fed list",
        "usage": "{tr}delf",
    },
    allow_bots=False,
    allow_channels=False,
    allow_private=False,
)
async def delfed_(message: Message):
    """Removes current chat from connected Feds."""
    if "-all" in message.flags:
        msg_ = "**Disconnected from all connected federations!**"
        await message.edit(msg_, del_in=7)
        await FED_LIST.drop()
    else:
        try:
            chat_ = await message.client.get_chat(message.input_str or message.chat.id)
        except (PeerIdInvalid, IndexError):
            return await message.err("Provide a valid Chat ID", del_in=7)
        chat_id = chat_.id
        out = f"{chat_.title}\nChat ID: {chat_id}\n"
        found = await FED_LIST.find_one({"chat_id": chat_id})
        if found:
            msg_ = out + f"Successfully Removed Fed: **{found['fed_name']}**"
            await message.edit(msg_, del_in=7)
            await FED_LIST.delete_one(found)
        else:
            return await message.err(
                out + "**Does't exist in your Fed List !**", del_in=7
            )
    await CHANNEL.log(msg_)


@userge.on_cmd(
    "fban",
    about={
        "header": "Fban user",
        "description": "Fban the user from the list of fed",
        "flags": {
            "-p": "sends replied message as proof",
            "-m": "mass bans replied list of users",
        },
        "usage": "{tr}fban -p[optional] [username|reply to user|user_id] [reason (optional)]",
    },
    allow_bots=False,
    allow_channels=False,
)
async def fban_(message: Message):
    """Bans a user from connected Feds."""
    message.flags
    fban_arg = ["❯", "❯❯", "❯❯❯", "❯❯❯ <b>FBanned {}</b>"]
    d_err = ("Failed to detect user **{}**, fban might not work...",)
    input = message.filtered_input_str
    await message.edit(fban_arg[0])
    if not message.reply_to_message:
        user = input.split()[0]
        reason = input.split()[1:]
        reason = " ".join(reason)
    else:
        user = message.reply_to_message.from_user.id
        reason = input
    if user is None:
        return await message.err("Provide a user ID or reply to a user...", del_in=7)
    try:
        user_ = await message.client.get_users(user)
        user = user_.id
    except (PeerIdInvalid, IndexError):
        pass
    if (
        user in Config.SUDO_USERS
        or user in Config.OWNER_ID
        or user == (await message.client.get_me()).id
    ):
        if not input:
            await message.edit("Can't fban replied user, give user ID...", del_in=7)
            return
        user = input.split()[0]
        reason = input.split()[1:]
        reason = " ".join(reason)
        try:
            user_ = await message.client.get_users(user)
            user = user_.id
        except (PeerIdInvalid, IndexError):
            await message.edit(d_err.format(user))
            await CHANNEL.log(d_err.format(user))
        if (
            user in Config.SUDO_USERS
            or user in Config.OWNER_ID
            or user == (await message.client.get_me()).id
        ):
            return await message.err(
                "Can't fban user that exists in SUDO or OWNERS...", del_in=7
            )
    try:
        user_ = await userge.get_users(user)
        u_link = user_.mention
    except BaseException:
        u_link = user
    failed = []
    total = 0
    reason = reason or "Not specified."
    await message.edit(fban_arg[1])
    async for data in FED_LIST.find():
        total += 1
        chat_id = int(data["chat_id"])
        await userge.send_message(
            chat_id,
            f"/fban {user} {reason}",
        )
        try:
            async with userge.conversation(chat_id, timeout=8) as conv:
                response = await conv.get_response(
                    mark_read=True,
                    filters=(filters.user([609517172]) & ~filters.service),
                )
                resp = response.text
                if (
                    ("New FedBan" not in resp)
                    and ("Starting a federation ban" not in resp)
                    and ("Start a federation ban" not in resp)
                    and ("FedBan reason updated" not in resp)
                ):
                    failed.append(f"{data['fed_name']}  \n__ID__: `{data['chat_id']}`")

        except BaseException:
            failed.append(data["fed_name"])
    if total == 0:
        return await message.err(
            "You Don't have any feds connected!\nsee .help addf, for more info."
        )
    await message.edit(fban_arg[2])

    if len(failed) != 0:
        status = f"Failed to fban in {len(failed)}/{total} feds.\n"
        for i in failed:
            status += "• " + i + "\n"
    else:
        status = f"Success! Fbanned in `{total}` feds."
    msg_ = fban_arg[3].format(u_link) + f"\n**Reason:** {reason}\n**Status:** {status}"
    await message.edit(msg_)
    await CHANNEL.log(msg_)


@userge.on_cmd(
    "fbanp",
    about={
        "header": "Fban with proof",
        "description": "Fban user from the list of feds with replied message as proof",
        "usage": "{tr}fbanp [direct reply to spammer] {reason}\n{tr}fbanp [reply to proof forwarded by you] {user id} {reason}",
    },
    allow_bots=False,
    allow_channels=False,
)
async def fban_p(message: Message):
    """Fban user from connected feds with proof."""
    fban_arg = ["❯", "❯❯", "❯❯❯", "❯❯❯ <b>FBanned {}</b>"]
    d_err = ("Failed to detect user **{}**, fban might not work...",)
    if not message.reply_to_message:
        await message.err("Please reply to proof...", del_in=7)
        return
    user = message.reply_to_message.from_user.id
    input = message.input_str
    reason = input
    if (
        user in Config.SUDO_USERS
        or user in Config.OWNER_ID
        or user == (await message.client.get_me()).id
    ):
        if not input:
            await message.err("Can't fban replied user, give user ID...", del_in=7)
            return
        user = input.split()[0]
        reason = input.split()[1:]
        reason = " ".join(reason)
        try:
            user_ = await userge.get_users(user)
            user = user_.id
        except (PeerIdInvalid, IndexError):
            await message.edit(f_err.format(user))
            await CHANNEL.log(d_err.format(user))
        if (
            user in Config.SUDO_USERS
            or user in Config.OWNER_ID
            or user == (await message.client.get_me()).id
        ):
            return await message.err(
                "Can't fban user that exists in SUDO or OWNERS...", del_in=7
            )
    try:
        user_ = await userge.get_users(user)
        u_link = user_.mention
    except BaseException:
        u_link = user
    await message.edit(fban_arg[0])
    failed = []
    total = 0
    reason = reason or "Not specified"
    await message.edit(fban_arg[1])
    from_ = message.chat.id
    admin = message.from_user.id
    proof = message.reply_to_message.message_id
    async for data in FED_LIST.find():
        total += 1
        chat_id = int(data["chat_id"])
        if chat_id != from_:
            fwd = await userge.forward_messages(
                chat_id=chat_id,
                from_chat_id=from_,
                message_ids=proof,
            )
        if admin != "956525773":
            await userge.send_message(
                chat_id,
                f"/fban {user} {reason}",
                reply_to_message_id=fwd.message_id,
            )
        else:
            await userge.send_message(
                chat_id,
                f"/fban {user} {reason}",
            )
        try:
            async with userge.conversation(chat_id, timeout=8) as conv:
                response = await conv.get_response(
                    mark_read=True,
                    filters=(filters.user([609517172]) & ~filters.service),
                )
                resp = response.text
                if (
                    ("New FedBan" not in resp)
                    and ("Starting a federation ban" not in resp)
                    and ("Start a federation ban" not in resp)
                    and ("FedBan reason updated" not in resp)
                ):
                    failed.append(f"{data['fed_name']}  \n__ID__: {data['chat_id']}")
        except BaseException:
            failed.append(data["fed_name"])
    if total == 0:
        return await message.err(
            "You Don't have any feds connected!\nsee .help addf, for more info."
        )
    await message.edit(fban_arg[2])

    if len(failed) != 0:
        status = f"Failed to fban in {len(failed)}/{total} feds.\n"
        for i in failed:
            status += "• " + i + "\n"
    else:
        status = f"Success! Fbanned in {total} feds."
    msg_ = fban_arg[3].format(u_link) + f"\n**Reason:** {reason}\n**Status:** {status}"
    await message.edit(msg_)
    await CHANNEL.log(msg_)


@userge.on_cmd(
    "fbanm",
    about={
        "header": "Mass fban a list of users",
        "description": "Mass fban replied list of users from the list of feds",
        "usage": "{tr}fbanm [reply to list of spammers] [reason (optional)]",
    },
    allow_bots=False,
    allow_channels=False,
)
async def fban_m(message: Message):
    """Mass fban list of users."""
    if not message.reply_to_message:
        await message.edit("Reply to a list of users...", del_in=5)
        return
    fban_arg = ["❯", "❯❯", "❯❯❯", "❯❯❯ <b>FBan complete</b>"]
    input = message.reply_to_message.text.split()
    reason = message.input_str or "Not specified"
    user_n = 0
    ban, cant = 0, 0
    fban_prog = fban_arg[0]
    for user in input:
        user_n += 1
        if user.startswith("@"):
            try:
                user_ = await message.client.get_users(user)
                user = user_.id
            except BaseException:
                pass
        if (
            user in Config.SUDO_USERS
            or user in Config.OWNER_ID
            or user == (await message.client.get_me()).id
        ):
            cant += 1
            continue
        await mass_fban(user, reason)
        ban += 1
        prog = user_n / len(input) * 100
        prog_1, prog_2 = True, True
        if prog >= 33 and prog_1:
            fban_prog = fban_arg[1]
            prog_1 = False
        if prog >= 66 and prog_2:
            fban_prog = fban_arg[2]
            prog_2 = False
        if prog == 100:
            fban_prog = fban_arg[3]
        await message.edit(
            f"{fban_prog}\n"
            f"**Fbanned:** {ban} out of {len(input)}\n"
            f"**Can't fban:** {cant}"
        )
        if user_n == len(input):
            await CHANNEL.log(
                f"#FBAN\n**Fbanned:** {ban} out of {len(input)}\n**Failed:** {fail}\n**Can't fban:** {cant}"
            )


@userge.on_cmd(
    "unfban",
    about={
        "header": "Unfban user",
        "description": "Unfban the user from the list of fed",
        "usage": "{tr}unfban [username|reply to user|user_id]",
    },
    allow_bots=False,
    allow_channels=False,
)
async def unfban_(message: Message):
    """Unbans a user from connected Feds."""
    user = (message.extract_user_and_text)[0]
    fban_arg = ["❯", "❯❯", "❯❯❯", "❯❯❯ <b>Un-FBanned {}</b>"]
    await message.edit(fban_arg[0])
    error_msg = "Provide a User ID or reply to a User"
    if user is None:
        return await message.err(error_msg, del_in=7)
    try:
        user_ = await message.client.get_users(user)
    except (PeerIdInvalid, IndexError):
        return await message.err(error_msg, del_in=7)
    user = user_.id
    failed = []
    total = 0
    await message.edit(fban_arg[1])
    async for data in FED_LIST.find():
        total += 1
        chat_id = int(data["chat_id"])
        try:
            async with userge.conversation(chat_id, timeout=8) as conv:
                await conv.send_message(f"/unfban {user}")
                response = await conv.get_response(
                    mark_read=True,
                    filters=(filters.user([609517172]) & ~filters.service),
                )
                resp = response.text
                if (
                    ("New un-FedBan" not in resp)
                    and ("I'll give" not in resp)
                    and ("Un-FedBan" not in resp)
                ):
                    failed.append(f"{data['fed_name']}  \n__ID__: `{data['chat_id']}`")

        except BaseException:
            failed.append(data["fed_name"])
    if total == 0:
        return await message.err(
            "You Don't have any feds connected!\nsee .help addf, for more info."
        )
    await message.edit(fban_arg[2])

    if len(failed) != 0:
        status = f"Failed to un-fban in `{len(failed)}/{total}` feds.\n"
        for i in failed:
            status += "• " + i + "\n"
    else:
        status = f"Success! Un-Fbanned in `{total}` feds."
    msg_ = fban_arg[3].format(user_.mention) + f"\n**Status:** {status}"
    await message.edit(msg_)
    await CHANNEL.log(msg_)


@userge.on_cmd(
    "listf",
    about={
        "header": "Fed Chat List",
        "description": "Get a list of chats added in fed",
        "usage": "{tr}listf",
    },
)
async def fban_lst_(message: Message):
    """List all connected Feds."""
    out = ""
    total = 0
    async for data in FED_LIST.find():
        total += 1
        out += f"• Fed: <b>{data['fed_name']}</b>\n"
    await message.edit_or_send_as_file(
        f"**Connected federations: [{total}]**\n\n" + out
        if out
        else "**You haven't connected to any federations yet!**",
        caption="Connected Fed List",
    )


async def mass_fban(user, reason):
    async for data in FED_LIST.find():
        chat_id = int(data["chat_id"])
        try:
            await userge.send_message(chat_id, f"/fban {user} {reason}")
            await asyncio.sleep(0.5)
        except FloodWait as e:
            await asyncio.sleep(e.x + 5)
