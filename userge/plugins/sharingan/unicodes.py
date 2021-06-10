# plugin for USERGE-X made by @Kakashi_HTK(telegram)/@ashwinstr(github)

from userge import Message, userge


@userge.on_cmd(
    "chr",
    about={
        "header": "search unicodes",
        "description": "search unicode corresponding number",
        "usage": "{tr}chr [unicode character(s)]",
        "example": "{tr}chr > [",
    },
)
async def uni_chr(message: Message):
    """search unicodes"""
    char_ = message.input_str
    char_ = char_.split()
    list_ = []
    for char in char_:
        for num in range(0, 1114112):
            if chr(num) == char:
                list_.append(f"{char} - chr({num})")
                break
    ans = "\n".join(list_)
    await message.edit(ans)
