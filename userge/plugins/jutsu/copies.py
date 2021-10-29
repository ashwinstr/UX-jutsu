# plugin made for USERGE-X by @Kakashi_HTK(TG)/@ashwinstr(GH)
# before porting please ask to Kakashi


import asyncio

from pyrogram.errors import FloodWait, PeerIdInvalid

from userge import Config, Message, get_collection, userge
from userge.helpers import admin_or_creator, msg_type
from userge.helpers.jutsu_tools import get_response

COPIED = get_collection("COPIED")


CHANNEL = userge.getCLogger(__name__)


@userge.on_cmd(
    "copy_ch",
    about={
        "header": "copy your channel content",
        "description": "copy your channel content from one channel to another\nNOTE: it'll post in latest to older order",
        "usage": "{tr}copy_ch [from_channel_id] [to_channel_id]",
    },
)
async def copy_channel_(message: Message):
    """copy channel content"""
    await message.edit("`Checking channels...`")
    me_ = await userge.get_me()
    input_ = message.input_str
    from_chann = input_.split()[0]
    to_chann = input_.split()[1]
    try:
        if from_chann.isdigit():
            from_chann = int(from_chann)
        from_ = await userge.get_chat(from_chann)
    except BaseException:
        return await message.edit(
            f"`Given from_channel '{from_chann}' is invalid...`", del_in=5
        )
    try:
        if to_chann.isdigit():
            to_chann = int(to_chann)
        to_ = await userge.get_chat(to_chann)
    except BaseException:
        return await message.edit(
            f"`Given to_channel '{to_chann}' is invalid...`", del_in=5
        )
    if from_.type != "channel" or to_.type != "channel":
        return await message.edit(
            "`One or both of the given chat is/are not channel...`", del_in=5
        )
    from_owner = await admin_or_creator(from_.id, me_.id)
    if not from_owner["is_admin"] and not from_owner["is_creator"]:
        return await message.edit(
            f"`Owner or admin required in ('{from_.title}') to copy posts...`", del_in=5
        )
    to_admin = await admin_or_creator(to_.id, me_.id)
    if not to_admin["is_admin"] and not to_admin["is_creator"]:
        return await message.edit(
            f"Need admin rights to copy posts to {to_.title}...", del_in=5
        )
    total = 0
    del_list = []
    await message.edit(
        f"`Copying posts from `<b>{from_.title}</b>` to `<b>{to_.title}</b>..."
    )
    async for post in userge.search_messages(from_.id):
        total += 1
        try:
            # first posting, which'll be in reverse order of original posts
            first_post = await userge.copy_messages(to_.id, from_.id, post.message_id)
            del_list.append(first_post.message_id)
        except FloodWait as e:
            await asyncio.sleep(e.x + 3)
    await message.edit(
        f"`Posting the {total} posts again to correct the their order...`"
    )
    for post_again in del_list:
        try:
            # second posting to correct the order
            await userge.copy_messages(message.chat.id, message.chat.id, post_again)
        except FloodWait as e:
            await asyncio.sleep(e.x + 3)
    try:
        await userge.delete_messages(del_list)
    except FloodWait as e:
        await asyncio.sleep(e.x + 3)
    out_ = f"`Forwarded `<b>{total}</b>` from `<b>{from_.title}</b>` to `<b>{to_.title}</b>`.`"
    await message.edit(out_)
    await CHANNEL.log(out_)


@userge.on_cmd(
    "copy_msg",
    about={
        "header": "copy message to database",
        "description": "copy message to database, which can later be pasted to other chats",
        "usage": "{tr}copy_msg [reply to message]",
    },
)
async def copy_message(message: Message):
    """copy message to database"""
    reply_ = message.reply_to_message
    if not reply_:
        return await message.edit(
            "`Reply to a message to put it in copied list...`", del_in=5
        )
    await message.edit("`Copying...`")
    log_ = Config.LOG_CHANNEL_ID
    info_ = await CHANNEL.log("### <b>COPIED MESSAGE BELOW</b> ###")
    fwd_ = await reply_.forward(log_)
    link_ = fwd_.link
    type_ = msg_type(reply_)
    await COPIED.insert_one({"msg_id": fwd_.message_id, "type": type_, "link": link_})
    await message.edit("`Copied the replied message...`", del_in=5)


@userge.on_cmd(
    "copied",
    about={
        "header": "list of copied messages to database",
        "description": "list of copied messages to database, which will later be pasted to other chats",
        "usage": "{tr}copied",
    },
)
async def copied_messages(message: Message):
    """list of copied messages to database"""
    await message.edit("`Getting copied messages' list...`")
    list_ = "List of <b>copied messages</b> is as below: [{}]\n\n"
    total_ = 0
    async for msg_ in COPIED.find():
        total_ += 1
        link_ = msg_["link"]
        hyperlink = f"<a href={link_}>Link</a>"
        list_ += f"[{total_:02}] {hyperlink} - {msg_['type']}\n"
    await message.edit(list_.format(total_))


@userge.on_cmd(
    "paste_msg",
    about={
        "header": "paste the message copied in database",
        "usage": "{tr}paste_msg [in target chat]",
    },
)
async def paste_message(message: Message):
    """paste the message copied in database"""
    await message.edit("`Pasting copied messages...`", del_in=3)
    log_ = Config.LOG_CHANNEL_ID
    suc = 0
    fail = 0
    async for msg_ in COPIED.find():
        try:
            await userge.copy_message(message.chat.id, log_, msg_["msg_id"])
            suc += 1
        except FloodWait as e:
            await asyncio.sleep(e.x + 3)
        except PeerIdInvalid:
            fail += 1
    await CHANNEL.log(
        f"### <b>PASTE</b> ###\n<b>Pasted:</b> {suc} messages\n<b>Failed:</b> {fail} messages"
    )


@userge.on_cmd(
    "clearcopy",
    about={
        "header": "clear copied message list from database",
        "usage": "{tr}clearcopy",
    },
)
async def clear_copied(message: Message):
    """clear copied message list from database"""
    msg_ = await message.edit(
        "Are you sure? Reply '`Yes.`' <b>within 5 seconds</b> to clear the copied message list from database."
    )
    me_ = await userge.get_me()
    try:
        resp = await get_response(msg_, filter_user=me_.id, mark_read=True)
    except Exception as e:
        await CHANNEL.log(e)
        return await message.edit(f"<b>ERROR:</b> {e}", del_in=5)
    if resp.text == "Yes.":
        await COPIED.drop()
    await message.edit("`Copied message list cleared from database...`", del_in=5)
