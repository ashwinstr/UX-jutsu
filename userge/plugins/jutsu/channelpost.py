# made for USERGE-X by @Kakashi_HTK(TG)/@ashwinstr(GH)


from userge import Message, userge


@userge.on_cmd(
    "post",
    about={
        "header": "post to channel",
        "usage": "{tr}post [reply to message]",
    },
)
async def post_(message: Message):
    await message.edit("`Processing...`")
    reply_ = message.reply_to_message

    if not reply_:
        return await message.edit("`Reply to a message...`")

    chat_ = message.input_str
    try:
        chat_ = await userge.get_chat(chat_)
    except (TypeError, ValueError):
        return await message.edit("`Invalid link provided...`")

    await userge.copy_message(chat_.id, message.chat.id, reply_.message_id)
    await message.edit(f"**Posted in** `{chat.title}`**!**")
