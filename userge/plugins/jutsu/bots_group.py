# plugin made for USERGE-X by @Kakashi_HTK(TG)/@ashwinstr(GH)
# before porting please ask to Kakashi


from userge import Message, userge


@userge.on_cmd(
    "bots",
    about={
        "header": "Bots in group",
        "description": "Check how many bots are there in the group",
        "usage": "{tr}bots",
    },
)
async def botz(message: Message):
    """Check the bots present in group."""
    chat = message.input_str
    if not chat:
        chat = message.chat.id
    try:
        chat_ = await userge.get_chat(chat)
        if chat_.type == "private":
            await message.edit(
                "`You can't use this command for private chats...`", del_in=5
            )
            return
        chat = chat_.id
    except BaseException:
        await message.edit("`Provide a valid chat as input...`", del_in=5)
        return
    admin_b = []
    member_b = []
    total = 0
    async for bot in userge.iter_chat_members(chat, filter="bots"):
        total += 1
        mention = bot.user.mention
        if bot.status == "administrator":
            admin_b.append(mention)
        else:
            member_b.append(mention)
    adm = len(admin_b)
    mem = len(member_b)
    out = f"<b>BOTS</b> in <b>{chat_.title}</b>: `[{total}]`\n\n"
    out += f"<b>Admin bot(s)</b>: [{adm}]\n"
    out += "🤖 " if admin_b else ""
    out += "\n🤖 ".join(admin_b)
    out += "\n\n" if admin_b else "\n"
    out += f"<b>Member bot(s)</b>: [{mem}]\n"
    out += "🤖 " if member_b else ""
    out += "\n🤖 ".join(member_b)
    await message.edit(out)
