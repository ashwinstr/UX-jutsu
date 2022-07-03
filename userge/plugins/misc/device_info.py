# by @fnixdev


from pyrogram.errors import YouBlockedUser

from userge import Message, userge
from userge.plugins.utils.translate import _translate_this as tr


@userge.on_cmd(
    "d",
    about={
        "header": "Get Device description",
        "description": "Get all Specs of a device.",
        "usage": "{tr}d Device name",
    },
)
async def ln_user_(message: Message):
    """device desc"""
    device_ = message.input_str
    bot_ = "@vegadata_bot"
    async with userge.conversation(bot_, timeout=30) as conv:
        try:
            await conv.send_message(f"!d {device_}")
        except YouBlockedUser:
            await message.err("Unblock @vegadata_bot first...", del_in=5)
            return
        response = await conv.get_response(mark_read=True)
    resp = response.text
    src, dest = "auto", "en"
    trtxt = await tr(resp, dest, src)
    pic_ = resp.split()
    for photo in pic_:
        if (".jpg" or ".png" or ".jpeg") in photo:
            pic = photo
    await message.delete()
    await message.reply_photo(pic)
    await message.reply_text(trtxt.text, disable_web_page_preview=True)
