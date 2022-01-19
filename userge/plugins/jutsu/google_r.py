import os

from userge import Message, userge


async def _init() -> None:
    os.system(
        "wget -c https://raw.githubusercontent.com/jarun/googler/v4.3.2/googler &&  chmod +x googler"
    )


@userge.on_cmd(
    "googler",
    about={
        "header": "google search",
        "usage": "{tr}googler sharingan",
    },
)
async def googl_er(message: Message):
    """google search"""
    query_ = message.input_str
    if not query_:
        return await message.edit("`Query not found.`", del_in=5)
    await message.edit("`Searching...`")
    response = os.popen(f"./googler {query_}").read()
    resp = response.split("\n\n")
    out_ = f"<u><b>The google search for '{query_}' is as below...</u></b>\n\n"
    len_ = len(resp)
    no_ = 1
    for one in resp:
        if no_ == len_:
            break
        two = one.split("\n", 2)
        title = two[0]
        link_ = (two[1]).strip()
        try:
            desc = (two[2]).strip()
        except BaseException:
            desc = ""
        out_ += f"<b>{title}</b>\n{link_}\n<i>{desc}</i>\n\n"
        no_ += 1
    await message.edit_or_send_as_file(out_, disable_web_page_preview=True)
