# made for USERGE-X by @Kakashi_HTK(tg)/@ashwinstr(gh)

from userge import userge, Message, Config
from userge.helpers import msg_type
from userge.utils import post_to_telegraph as pt

@userge.on_cmd(
    "tb",
    about={
        "header": "get last traceback from main account",
        "flags": {
            "-e": "executor(eval) traceback",
        },
        "usage": "{tr}tb [number of previous messages to search (default 5)]",
    },
)
async def last_logged(message: Message):
    """get last traceback from main account"""
    limit_ = message.input_str
    if not limit_:
        limit_ = 5
    elif not limit_.isdigit():
        return await message.edit("`Provide a number as limit.`", del_in=5)
    if limit_ > 10:
        return await message.edit("`Can't search more than 10 messages.`", del_in=5)
    await message.edit("`Looking for last traceback...`")
    num = 0
    me_ = (await userge.get_users(Config.OWNER_ID)).first_name
    async for msg_ in userge.search_messages(Config.LOG_CHANNEL_ID):
        if msg_type(msg_) == "text":
            num += 1
            if "-e" in message.flags:
                search_ = "#EXECUTOR"
                found_ = "eval traceback"
            else:
                search_ = "#TRACEBACK"
                found_ = "traceback"
            if search_ in msg_.text:
                text_ = msg_.text.html
                text_ = text_.replace("\n", "<br>")
                link_ = pt(f"{found_.capitalize()} from log channel of {me_}.", text_)
                return await message.edit(f"Last <b>{found_}</b> is [<b>HERE</b>]({link_}).", disable_web_page_preview=True)
            if num == limit_:
                return await message.edit(f"`Couldn't find {found_} in last {limit_} messages.`", del_in=5)
