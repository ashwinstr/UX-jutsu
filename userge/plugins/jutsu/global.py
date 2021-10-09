# this plugin is made for USERGE-X by @Kakashi_HTK(TG)/@ashwinstr(GH)

import asyncio

from pyrogram.errors import ChatAdminRequired, FloodWait, UserNotParticipant

from userge import Message, userge
from userge.helpers import admin_chats

CHANNEL = userge.getCLogger(__name__)


@userge.on_cmd(
    "gpromote",
    about={
        "header": "global promote",
        "description": "promote in every chat you're admin in",
        "usage": "{tr}gpromote [reply to user or user id]",
    },
)
async def g_promote_(message: Message):
    """global promote"""
    input_ = message.input_str
    reply_ = message.reply_to_message
    if reply_:
        user_ = reply_.from_user.id
        if input_:
            pass
        else:
            pass
    else:
        try:
            userandrank = input_.split()
            user_ = userandrank[0]
            try:
                userandrank[1]
            except BaseException:
                pass
        except BaseException:
            await message.edit("`Provide a user ID or reply to targeted user...`")
            return
    try:
        user_ = await userge.get_users(user_)
    except BaseException:
        await message.edit(f"The target `{user_}` is not a user...", del_in=5)
        return

    user_name = " ".join([user_.first_name, user_.last_name or ""])
    await message.edit(f"Promoting <b>{user_name}</b> globally...")
    me_ = await userge.get_me()
    adm_chats = await admin_chats(me_.id)
    passed = 0
    chat_suc = ""
    for chat in adm_chats:
        try:
            await userge.get_chat_member(chat["chat_id"], user_.id)
            await userge.promote_chat_member(
                chat["chat_id"],
                user_.id,
                can_change_info=True,
                can_delete_messages=True,
                can_restrict_members=True,
                can_invite_users=True,
                can_pin_messages=True,
            )
            passed += 1
            chat_suc += f"[{passed}] <b>{chat['chat_name']}</b>\n"
        except UserNotParticipant:
            pass
        except ChatAdminRequired:
            pass
        except FloodWait as e:
            await asyncio.sleep(e.x + 5)
        except Exception as e:
            await message.edit(f"Something unexpected happened...\n<b>ERROR:</b> {e}")
            return
    msg_ = f"GPromoted user <b>{user_name}</b> successfully."
    await message.edit(msg_)
    log_ = (
        "#G_PROMOTED\n"
        f"<b>USER:</b> [{user_name}](tg://user?id={user_.id}) <b>ID:</b> `{user_.id}`\n"
        f"<b>IN:</b> {passed} chats as shown below...\n\n"
        f"{chat_suc}"
    )
    await CHANNEL.log(log_)
