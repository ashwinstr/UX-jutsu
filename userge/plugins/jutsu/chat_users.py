# created for USERGE-X by @Kakashi_HTK(tg)/@ashwinstr(github)

from userge import Message, userge


@userge.on_cmd(
    "c_users",
    about={
        "header": "find chat users",
        "description": "mention users from any chat",
        "usage": "{tr}c_users [limit] [chat username/id]\n"
        "or {tr}c_users [[limit] or [chat username/id]]\n"
        "or {tr}c_users (default limit 100) (current chat)",
    },
)
async def chat_users_(message: Message):
    """find chat users"""
    input_ = message.input_str
    if not input_:
        limit_ = 100
        chat_ = message.chat.id
    else:
        if len(input_.split()) > 1:
            chat_ = input_.split()[1:]
            limit_ = input_.split()[0]
            try:
                await userge.get_chat(chat_)
            except BaseException:
                await message.edit(f"Chat <code>{chat_}</code> is not a valid chat...")
                return
        else:
            chat_ = input_
            try:
                await userge.get_chat(chat_)
                limit_ = 100
            except BaseException:
                chat_ = message.chat.id
                limit_ = input_
                if limit_ > 10000:
                    await message.edit(
                        f"Current limit(<code>{limit_}</code>) can't be more than 10000..."
                    )
                    return
    title = (await userge.get_chat(chat_)).title
    await message.edit(f"Getting {limit_} members of chat {title}...")
    list_ = ""
    lim = 0
    async for mem in userge.iter_chat_members(chat_):
        list_ += f"@{mem.user.username}\n"
        lim += 1
        if limit_ != 10000:
            if lim == limit_:
                break
    await message.edit(list_)
