# plugin for USERGE-X made by @Kakashi_HTK(telegram)/@ashwinstr(github)

from userge import Message, userge


@userge.on_cmd(
    "chr",
    about={
        "header": "search unicodes",
        "description": "search unicode corresponding code",
        "usage": "{tr}chr [unicode character(s)]",
        "example": "{tr}chr > (\n" "Note: one character per space",
    },
)
async def uni_chr(message: Message):
    """search unicodes"""
    char_ = message.input_str
    if not char_:
        await message.edit("Provide a <b>character</b> to search...", del_in=5)
        return
    char_ = char_.split()
    list_ = []
    total = 0
    await message.edit("Searching unicodes...")
    for char in char_:
        if len(char) > 1:
            await message.edit(
                f"Enter one character per space!\nError at <b>{char}</b>", del_in=5
            )
            return
        total += 1
        for num in range(0, 1114112):
            if chr(num) == char:
                list_.append(f'"<b>{char}</b>" - <code>chr({num})</code>')
                break
    if len(char_) == 1:
        plural = "its"
    else:
        plural = "their"
    ans = f"<b>UNICODE(s)</b> and {plural} corresponding code: <b>[{total}]</b>\n\n"
    ans += "\n".join(list_)
    await message.edit(ans)
