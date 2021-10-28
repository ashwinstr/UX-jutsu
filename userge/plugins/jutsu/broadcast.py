# plugin made for USERGE-X by @Kakashi_HTK(TG)/@ashwinstr(GH)
# before porting please ask to Kakashi


import asyncio

from pyrogram import filters
from pyrogram.errors import FloodWait

from userge import Config, Message, get_collection, userge
from userge.helpers import full_name
from userge.utils import post_to_telegraph as pt

POST_LIST = get_collection("POST_LIST")
CHANNEL = userge.getCLogger(__name__)

SAVED_SETTINGS = get_collection("CONFIGS")
BROAD_TAGGING = False


async def _init() -> None:
    data = await SAVED_SETTINGS.find_one({"_id": "BROAD_TAG"})
    if data:
        bool(data["is_active"])


@userge.on_cmd(
    "broad_tog",
    about={
        "header": "toggle #Broadcast tag in post",
        "flags": {
            "-c": "check toggle",
        },
        "usage": "{tr}broad_tog",
    },
)
async def broad_toggle_(message: Message):
    """toggle #Broadcast tag"""
    global BROAD_TAGGING
    if "-c" in message.flags:
        if BROAD_TAGGING:
            tog = "enabled"
        else:
            tog = "disabled"
        await message.edit(f"Broadcast tag is <b>{tog}</b>.", del_in=3)
        return
    if BROAD_TAGGING:
        BROAD_TAGGING = False
        await message.edit("`Broadcast tag is now disabled.`", del_in=3)
    else:
        BROAD_TAGGING = True
        await message.edit("`Broadcast tag is now enabled.`", del_in=3)
    await SAVED_SETTINGS.update_one(
        {"_id": "BROAD_TAG"}, {"$set": {"is_active": BROAD_TAGGING}}
    )


@userge.on_cmd(
    "addp",
    about={
        "header": "add chat to POST LIST",
        "usage": "{tr}addp [chat username or id (optional)]",
    },
    allow_bots=False,
    allow_channels=False,
)
async def add_post(message: Message):
    """add chat to list for posting"""
    chat_ = message.input_str
    if not chat_:
        chat_ = message.chat.id
    try:
        chat_ = await userge.get_chat(chat_)
    except BaseException:
        await message.edit(f"`Provided input ({chat_}) is not a chat...`", del_in=5)
        return
    chat_type = chat_.type
    if chat_type == "private":
        chat_name = full_name(chat_)
    else:
        chat_name = chat_.title
    chat_id = chat_.id
    found = await POST_LIST.find_one({"chat_id": chat_id})
    if found:
        await message.edit(f"Chat <b>{chat_name}</b> is already in list.", del_in=5)
        return
    await POST_LIST.insert_one(
        {"chat_name": chat_name, "chat_id": chat_id, "chat_type": chat_type}
    )
    msg_ = f"Successfully added <b>{chat_name}</b> (`{chat_id}`) in POST LIST."
    await message.edit(msg_)
    await CHANNEL.log(msg_)


@userge.on_cmd(
    "delp",
    about={
        "header": "delete chat from POST LIST",
        "flags": {
            "-all": "delete all chats from list",
        },
        "usage": "{tr}delp [chat username or id (optional)]",
    },
    allow_bots=False,
    allow_channels=False,
)
async def del_post(message: Message):
    """delete chat from list for posting"""
    if "-all" in message.flags:
        msg_ = (
            "### <b>DELETING ALL CHATS FROM POST LIST</b> ###\n\n"
            "For confirmation of deleting all chats from POST LIST,\n"
            "please reply with '`Yes, delete all chats in list for posting.`' <b>within 10 seconds</b>."
        )
        await message.edit(msg_)
        me_ = await userge.get_me()
        try:
            async with userge.conversation(message.chat.id) as conv:
                response = await conv.get_response(
                    mark_read=True, filters=(filters.user(me_.id))
                )
        except BaseException:
            msg_ += "\n\n### Process cancelled as no response given. ###"
            await message.edit(msg_)
            return
        resp = response.text
        if resp == "Yes, delete all chats in list for posting.":
            await POST_LIST.drop()
            await resp.delete()
            del_ = "Deleted whole <b>POST LIST</b> successfully."
            await message.edit(del_)
            await CHANNEL.log(del_)
            return

    chat_ = message.input_str
    if not chat_:
        chat_ = message.chat.id
    try:
        chat_ = await userge.get_chat(chat_)
    except BaseException:
        await message.edit(f"`Provided input ({chat_}) is not a chat...`", del_in=5)
        return
    chat_id = chat_.id
    found = await POST_LIST.find_one({"chat_id": chat_id})
    if found:
        msg_ = f"Successfully removed <b>{found['chat_name']}</b> from POST LIST."
        await POST_LIST.delete_one(found)
        await message.edit(msg_)
        await CHANNEL.log(msg_)
        return
    else:
        await message.edit(f"The chat <b>{chat_id}</b> doesn't exist in POST LIST.")


@userge.on_cmd(
    "listp",
    about={
        "header": "list chats in POST LIST",
        "flags": {
            "-id": "list chat IDs as well",
        },
        "usage": "{tr}listp",
    },
    allow_bots=False,
    allow_channels=False,
)
async def list_post(message: Message):
    """list chats in POST LIST"""
    s_groups = ""
    s_total = 0
    groups = ""
    g_total = 0
    priv = ""
    p_total = 0
    out_ = "List of chats in <b>POST LIST</b>: [{}]\n\n"
    async for chat_ in POST_LIST.find():
        chat_id = chat_["chat_id"]
        chat_name = chat_["chat_name"]
        type_ = chat_["chat_type"]
        id_ = f"'`{chat_id}`' - " if "-id" in message.flags else ""
        if type_ == "supergroup":
            s_total += 1
            s_groups += f"• [{s_total}] {id_}<b>{chat_name}</b>\n"
        elif type_ == "group":
            g_total += 1
            groups += f"• [{g_total}] {id_}<b>{chat_name}</b>\n"
        else:
            p_total += 1
            priv += f"• [{p_total}] {id_}<b>{chat_name}</b>\n"
    total_ = s_total + g_total + p_total
    out_ += (
        f"<b>Supergroup/s:</b> [{s_total}]\n"
        f"{s_groups}\n"
        f"<b>Normal group/s:</b> [{g_total}]\n"
        f"{groups}\n"
        f"<b>Private chat/s:</b> [{p_total}]\n"
        f"{priv}"
    )
    out_ = out_.format(total_)
    if len(out_) <= 4096:
        await message.edit(out_)
    else:
        link_ = pt("List of chats in POST LIST.", out_)
        await message.edit(
            f"List of chats in POST LIST is <a href='{link_}'><b>HERE</b></a>."
        )


@userge.on_cmd(
    "post",
    about={
        "header": "post to channel",
        "flags": {
            "-all": "send to all chats in list",
            "-grp": "send to all groups in list",
            "-pvt": "send to all private chats in list",
        },
        "usage": "{tr}post [flag] [reply to message]",
    },
)
async def post_(message: Message):
    await message.edit("`Processing...`")
    reply_ = message.reply_to_message
    flags = message.flags
    if not reply_:
        return await message.edit("`Reply to a message...`")
    if ("-all" or "-grp" or "-pvt") not in flags:
        target = message.input_str
        if target.isdigit():
            target = int(target)
        try:
            chat_ = await userge.get_chat(target)
        except BaseException:
            await message.edit(
                f"Given target <b>{target}</b> is not valid, see `{Config.CMD_TRIGGER}help post` for help...",
                del_in=5,
            )
            return
        if BROAD_TAGGING:
            broad = await userge.send_message(chat_.id, "#BROADCAST")
            broad_id = broad.message_id
        else:
            broad_id = None
        await userge.copy_message(
            chat_.id, message.chat.id, reply_.message_id, reply_to_message_id=broad_id
        )
        if chat_.type in ["private", "bot"]:
            chat_name = full_name(chat_)
        else:
            chat_name = chat_.title
        await message.edit(f"Broadcasted a message to <b>{chat_name}</b> successfully.")
        await CHANNEL.log(
            f"#BROADCAST_SUCCESSFUL\n\nBroadcasted a message to <b>{chat_name}</b> (`{chat_.id}`) successfully."
        )
        return
    total = 0
    try:
        async for chats_ in POST_LIST.find():
            if "-all" in flags:
                if BROAD_TAGGING:
                    broad = await userge.send_message(chats_["chat_id"], "#BROADCAST")
                    broad_id = broad.message_id
                else:
                    broad_id = None
                await userge.copy_message(
                    chats_["chat_id"],
                    message.chat.id,
                    reply_.message_id,
                    reply_to_message_id=broad_id,
                )
                total += 1
            elif "-grp" in flags:
                if chats_["chat_type"] in ["group", "supergroup"]:
                    if BROAD_TAGGING:
                        broad = await userge.send_message(
                            chats_["chat_id"], "#BROADCAST"
                        )
                        broad_id = broad.message_id
                    else:
                        broad_id = None
                    await userge.copy_message(
                        chats_["chat_id"],
                        message.chat.id,
                        reply_.message_id,
                        reply_to_message_id=broad_id,
                    )
                    total += 1
            elif "-pvt" in flags:
                if chats_["chat_type"] == "private":
                    if BROAD_TAGGING:
                        broad = await userge.send_message(
                            chats_["chat_id"], "#BROADCAST"
                        )
                        broad_id = broad.message_id
                    else:
                        broad_id = None
                    await userge.copy_message(
                        chats_["chat_id"],
                        message.chat.id,
                        reply_.message_id,
                        reply_to_message_id=broad_id,
                    )
                    total += 1
    except FloodWait as e:
        await asyncio.sleep(e.x + 3)
    except Exception as e:
        await CHANNEL.log(f"`Something unexpected happened...`\n\n<b>ERROR:</b> `{e}`")
        return
    if "-all" in flags:
        to_ = "all chats"
    elif "-grp" in flags:
        to_ = "all groups"
    elif "-pvt" in flags:
        to_ = "all private chats"
    out_ = f"Broadcasted given message to <b>{to_} ({total})</b> in list successfully."
    await message.edit(out_)
    out_ = f"#BROADCAST_SUCCESSFUL\n\n{out_}"
    await CHANNEL.log(out_)
