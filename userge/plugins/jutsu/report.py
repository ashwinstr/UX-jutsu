# plugin for USERGE-X made by @Kakashi_HTK(tg)/@ashwinstr(gh)
# v1.3.3


from pyrogram.raw.functions.account import ReportPeer
from pyrogram.raw.types import (
    InputPeerUserFromMessage,
    InputReportReasonPornography,
    InputReportReasonSpam,
)

from userge import Config, Message, userge

CHANNEL = userge.getCLogger(__name__)


@userge.on_cmd(
    "rep",
    about={
        "header": "Report user for spam",
        "description": "Report users for spam or pornographic content",
        "usage": "{tr}rep [spam (default)] or [nsfw (if pornographic spam)(optional)] [reply to spam message]\n"
        "Do NOT reply to innocent users with this.",
    },
)
async def report_(message: Message):
    """Report user for spam"""
    reply_ = message.reply_to_message
    if not reply_:
        await message.edit("`Reply to message to report...`")
        return
    await message.edit("`Checking replied user...`")
    user_ = await userge.get_users(reply_.from_user.id)
    me_ = await userge.get_me()
    if user_.id in (Config.SUDO_USERS or Config.OWNER_ID) or user_.id == me_.id:
        await message.edit(
            f"Can not report user <b>{user_.mention}</b> since they're owner or sudo user...",
            del_in=5,
        )
        return
    reason_ = message.input_str
    if reason_ == "nsfw":
        reason_ = InputReportReasonPornography()
        for_ = "<b>pornographic</b> message"
    else:
        reason_ = InputReportReasonSpam()
        for_ = "<b>spam</b> message"
    peer_ = (
        InputPeerUserFromMessage(
            peer=message.chat.id,
            msg_id=reply_.message_id,
            user_id=user_.id,
        ),
    )
    ReportPeer(
        peer=peer_,
        reason=reason_,
        message=reply_,
    )
    msg_ = (
        "### <b>Reported user</b> ###\n"
        f"<b>User:</b> {user_.mention}\n"
        f"<b>Reason:</b> <i>{for_}</i>"
    )
    await message.edit(msg_)
    await CHANNEL.log(msg_)
