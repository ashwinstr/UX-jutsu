# plugin made for USERGE-X by @Kakashi_HTK(TG)/@ashwinstr(GH)
# before porting please ask to Kakashi


import asyncio

from pyrogram.errors import FloodWait

from userge import Message, userge
from userge.helpers import admin_or_creator

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
