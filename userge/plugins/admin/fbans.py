"""Plugin to manage federations"""
# Author: Copyright (C) 2020 KenHV [https://github.com/KenHV]

# For USERGE-X
# Ported to Pyrogram + Rewrite with Mongo DB
# by: (TG - @DeletedUser420) [https://github.com/code-rgb]
# Thanks @Lostb053  for writing help
# Added proof forward and mass fban by @Kakashi_HTK/@ashwinstr

import asyncio
import os

from pyrogram import filters
from pyrogram.errors import (
    ChannelInvalid,
    FloodWait,
    Forbidden,
    PeerIdInvalid,
    UserBannedInChannel,
)

from userge import Config, Message, get_collection, userge

FBAN_LOG_CHANNEL = os.environ.get("FBAN_LOG_CHANNEL")


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
            chat_id = chat_.id
            chat_.title
        except (PeerIdInvalid, IndexError):
            chat_id = message.input_str
            id_ = chat_id.replace("-", "")
            if not id_.isdigit() or not chat_id.startswith("-"):
                return await message.err("Provide a valid chat ID...", del_in=7)
        out = f"Chat ID: {chat_id}\n"
        found = await FED_LIST.find_one({"chat_id": int(chat_id)})
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
        "usage": "{tr}fban [username|reply to user|user_id] [reason (optional)]",
    },
    allow_bots=False,
    allow_channels=False,
)
async def fban_(message: Message):
    """Bans a user from connected Feds."""
    message.flags
    fban_arg = ["❯", "❯❯", "❯❯❯", "❯❯❯ <b>FBanned {}</b>"]
    PROOF_CHANNEL = FBAN_LOG_CHANNEL if FBAN_LOG_CHANNEL else Config.LOG_CHANNEL_ID
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
            d_err = f"Failed to detect user **{user}**, fban might not work..."
            await message.edit(d_err, del_in=7)
            await CHANNEL.log(d_err)
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
        u_id = user_.id
    except BaseException:
        u_link = user
        u_id = user
    failed = []
    total = 0
    reason = reason or "Not specified."
    await message.edit(fban_arg[1])
    async for data in FED_LIST.find():
        total += 1
        chat_id = int(data["chat_id"])
        try:
            await userge.send_message(
                chat_id,
                f"/fban {user} {reason}",
            )
        except UserBannedInChannel:
            pass
        try:
            async with userge.conversation(chat_id, timeout=8) as conv:
                response = await conv.get_response(
                    mark_read=True,
                    filters=(filters.user([609517172]) & ~filters.service),
                )
                resp = response.text
                if not (
                    ("New FedBan" in resp)
                    or ("starting a federation ban" in resp)
                    or ("start a federation ban" in resp)
                    or ("FedBan Reason update" in resp)
                ):
                    failed.append(f"{data['fed_name']}  \n__ID__: `{data['chat_id']}`")
        except FloodWait as f:
            await asyncio.sleep(f.x + 3)
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
    msg_ = (
        fban_arg[3].format(u_link)
        + f"\n**ID:** <code>{u_id}</code>\n**Reason:** {reason}\n**Status:** {status}"
    )
    await message.edit(msg_)
    await userge.send_message(int(PROOF_CHANNEL), msg_)


@userge.on_cmd(
    "fbanp",
    about={
        "header": "Fban with proof",
        "description": "Fban user from the list of feds with replied message as proof",
        "flags": {
            "-r": "give link to proof in reason, if FBAN_LOG_CHANNEL added",
            "-s": "won't send proof to feds (silent), but will log in log channel + '-r'"
            "\nWARNING: don't use -r or -s if any of the fed group has links blocklisted",
        },
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
    PROOF_CHANNEL = FBAN_LOG_CHANNEL if FBAN_LOG_CHANNEL else Config.LOG_CHANNEL_ID
    if ("-r" or "-s") in message.flags:
        if not FBAN_LOG_CHANNEL:
            await message.err(
                "Add <code>FBAN_LOG_CHANNEL</code> to use reason flags..."
            )
            return
        channel_ = await userge.get_chat(int(FBAN_LOG_CHANNEL))
        if channel_.username is None:
            await message.err(
                "<b>Proof</b> channel can't private channel for <b>reason</b> flags..."
            )
            return
    user = message.reply_to_message.from_user.id
    input = message.filtered_input_str
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
            d_err = f"Failed to detect user **{user}**, fban might not work..."
            await message.edit(d_err, del_in=7)
            await CHANNEL.log(d_err)
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
        u_id = user_.id
    except BaseException:
        u_link = user
        u_id = user
    await message.edit(fban_arg[0])
    failed = []
    r_update = []
    total = 0
    await message.edit(fban_arg[1])
    from_ = message.chat.id
    message.from_user.id
    reply = message.reply_to_message
    proof = reply.message_id
    log_fwd = await userge.forward_messages(
        int(PROOF_CHANNEL),
        from_chat_id=from_,
        message_ids=proof,
    )
    reason = reason or "Not specified"
    if FBAN_LOG_CHANNEL and ("-r" in message.flags or "-s" in message.flags):
        reason += " || {" + f"{log_fwd.link}" + "}"
    async for data in FED_LIST.find():
        total += 1
        chat_id = int(data["chat_id"])
        try:
            if chat_id != from_ and "-s" not in message.flags:
                fwd = await userge.forward_messages(
                    chat_id=chat_id,
                    from_chat_id=from_,
                    message_ids=proof,
                )
                fwd_id = fwd.message_id
            elif "-s" in message.flags:
                fwd_id = None
            else:
                fwd_id = message.reply_to_message.message_id
        except (Forbidden, ChannelInvalid, UserBannedInChannel):
            fwd_id = None
        try:
            await userge.send_message(
                chat_id,
                f"/fban {user} {reason}",
                reply_to_message_id=fwd_id,
                disable_web_page_preview=True,
            )
        except UserBannedInChannel:
            pass
        try:
            async with userge.conversation(chat_id, timeout=8) as conv:
                response = await conv.get_response(
                    mark_read=True,
                    filters=(filters.user([609517172]) & ~filters.service),
                )
                resp = response.text
                if not (
                    ("New FedBan" in resp)
                    or ("FedBan Reason update" in resp)
                    or ("starting a federation ban" in resp)
                    or ("start a federation ban" in resp)
                ):
                    failed.append(f"{data['fed_name']}  \n__ID__: {data['chat_id']}")
                elif "FedBan Reason update" in resp:
                    r_update.append(f"{data['fed_name']} - <i>Reason updated</i>")
        except FloodWait as f:
            await asyncio.sleep(f.x + 3)
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
        success = False
    else:
        status = f"<b>Success!</b> Fbanned in {total} feds."
        if len(r_update) != 0:
            for i in r_update:
                status += f"\n• {i}"
        success = True
    msg_ = (
        fban_arg[3].format(u_link)
        + f"\n**ID:** <code>{u_id}</code>\n**Reason:** {reason}\n**Status:** {status}"
    )
    break_line = "\n" if success else ""
    log_proof_in = (
        f"<a href='{log_fwd.link}'><b>channel</b></a>"
        if "-r" not in message.flags
        else "<b>channel</b>"
    )
    chat_proof_in = (
        f"<a href='{reply.link}'><b>{message.chat.title}</b></a>"
        if (message.chat.type != "private")
        else "<b>PRIVATE</b>"
    )
    chat_msg_ = f"{msg_}{break_line}<b>Proof</b> logged in {log_proof_in}."
    log_msg_ = f"{msg_}{break_line}<b>Proof</b> in {chat_proof_in} chat."
    await message.edit(chat_msg_)
    await userge.send_message(PROOF_CHANNEL, log_msg_)


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
    PROOF_CHANNEL = FBAN_LOG_CHANNEL if FBAN_LOG_CHANNEL else Config.LOG_CHANNEL_ID
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
            await userge.send_message(
                PROOF_CHANNEL,
                f"#FBAN\n**Fbanned:** {ban} out of {len(input)}\n**Failed:** {fail}\n**Can't fban:** {cant}",
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
    input = message.input_str
    if message.reply_to_message:
        reason = input
    else:
        reason = input[1:]
    PROOF_CHANNEL = FBAN_LOG_CHANNEL if FBAN_LOG_CHANNEL else Config.LOG_CHANNEL_ID
    error_msg = "Provide a User ID or reply to a User"
    if user is None:
        return await message.err(error_msg, del_in=7)
    try:
        user_ = await message.client.get_users(user)
    except (PeerIdInvalid, IndexError):
        return await message.err(error_msg, del_in=7)
    user = user_.id
    reason = reason or "Not specified"
    failed = []
    total = 0
    await message.edit(fban_arg[1])
    async for data in FED_LIST.find():
        total += 1
        chat_id = int(data["chat_id"])
        try:
            async with userge.conversation(chat_id, timeout=8) as conv:
                await conv.send_message(f"/unfban {user} {reason}")
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
    msg_ = (
        fban_arg[3].format(user_.mention)
        + f"\n<b>ID:</b> <code>{user}</code>\n<b>Reason:</b> {reason}\n**Status:** {status}"
    )
    await message.edit(msg_)
    await userge.send_message(int(PROOF_CHANNEL), msg_)


@userge.on_cmd(
    "listf",
    about={
        "header": "Fed Chat List",
        "description": "Get a list of chats added in fed",
        "flags": {
            "-id": "Show fed group id in list.",
        },
        "usage": "{tr}listf",
    },
)
async def fban_lst_(message: Message):
    """List all connected Feds."""
    out = ""
    total = 0
    async for data in FED_LIST.find():
        total += 1
        id_ = f"{data['chat_id']}" if "-id" in message.flags else ""
        br_line = "\n          " if "-id" in message.flags else ""
        out += f"• Fed: <b>{data['fed_name']}</b>{br_line}{id_}\n"
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
