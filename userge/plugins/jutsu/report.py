# plugin for USERGE-X made by @Kakashi_HTK(tg)/@ashwinstr(gh)
# v1.3.3


from userge import Config, Message, userge
from userge.helpers import report_user

CHANNEL = userge.getCLogger(__name__)


@userge.on_cmd(
    "rep",
    about={
        "header": "Report user for spam",
        "description": "Report users for spam or pornographic content",
        "flags": {
            "-r": "report remotely using message link",
        },
        "usage": "{tr}rep [spam (default)] or [nsfw (if pornographic spam)(optional)] [reply to spam message]\n"
        "Do NOT reply to innocent users with this.",
    },
)
async def report_(message: Message):
    """Report user for spam"""
    reply_ = message.reply_to_message
    flags = message.flags
    if not reply_ and "-r" not in flags:
        await message.edit(
            "`Reply to spammer or provide spam message link to report...`", del_in=5
        )
        return
    if "-r" in flags:
        input_ = message.filtered_input_str
        try:
            link_ = input_.split()[0]
        except BaseException:
            await message.edit("`Provide a spam message link to report...`", del_in=5)
            return
        try:
            reason_ = " ".join(input_.split()[1:])
        except BaseException:
            reason_ = "spam"
        try:
            chat_id = link_.split("/")[-2]
            if chat_id.isdigit():
                chat_id = "-100" + str(chat_id)
                chat_id = int(chat_id)
            else:
                pass
            msg_id = link_.split("/")[-1]
        except BaseException:
            await message.edit(
                "`Provide a proper spam message link to report...`", del_in=5
            )
            return
        try:
            msg_en = await userge.get_messages(chat_id, int(msg_id))
            user_id = msg_en.from_user.id
        except BaseException:
            await message.edit(
                "`Provide a proper spam message link to report...`", del_in=5
            )
            return
    else:
        user_id = reply_.from_user.id
        reason_ = message.input_str
        if not reason_:
            reason_ = "spam"
        chat_id = message.chat.id
        msg_en = reply_
    await message.edit("`Checking replied user...`")
    user_ = await userge.get_users(user_id)
    me_ = await userge.get_me()
    if user_.id in (Config.SUDO_USERS or Config.OWNER_ID) or user_.id == me_.id:
        await message.edit(
            f"Can not report user <b>{user_.mention}</b> since they're owner or sudo user...",
            del_in=5,
        )
        return
    rep = report_user(
        chat=chat_id,
        user_id=user_.id,
        msg=msg_en,
        msg_id=msg_en.message_id,
        reason=reason_,
    )
    msg_ = (
        f"❯❯❯ <b>Reported {user_.mention}</b> \n"
        f"<b>User ID:</b> <code>{user_.id}</code>\n"
        f"<b>Reason:</b> <i>{rep}</i>"
    )
    await message.edit(msg_)
    await CHANNEL.log(msg_)
