# ported from catuserbot to USERGE-X by @Kakashi_HTK(TG)/@ashwinstr(GH)


import io
import os
import requests

from textwrap import wrap
from PIL import Image, ImageDraw, ImageFont

from userge import userge, Message
from userge.helpers import msg_type, get_profile_pic
from userge.utils import media_to_image

CHANNEL = userge.getCLogger(__name__)

FONT_FILE_TO_USE = "resources/DejavuSansMono.ttf"


def get_warp_length(width):
    return int((20.0 / 1024.0) * (width + 0.0))


@userge.on_cmd(
    "qpic",
    about={
        "header": "get quoted picture",
        "flags": {
            "-b": "b/w result",
            "-s": "sticker result",
        },
        "usage": "{tr}qpic [input or reply to message]",
    },
)
async def q_pic(message: Message):
    """get quoted picture"""
    input_ = message.filtered_input_str
    reply_ = message.reply_to_message
    if not input_ and not reply_:
        return await message.edit("`Either reply to message or provide input...`", del_in=5)
    elif input_:
        input_str = input_.strip()
    else:
        reply_to = reply_.message_id
        input_str = reply_.text or reply_.caption
    pfp_ = None
    msg_ = await message.edit("`Making quote pic...`")
    mediatype = msg_type(reply_)
    if (
        (not reply_)
        or (not mediatype)
        or (mediatype not in ["photo", "sticker"])
        or (
            mediatype == "sticker"
            and reply_.document.mime_type == "application/i-tgsticker"
        )
    ):
        user_ = reply_.from_user.id if reply_ else message.from_user.id
        pfp_ = await get_profile_pic(user_)
    else:
        pfp_ = await media_to_image(reply_)
        user_ = message.from_user.id
    try:
        user_e = await userge.get_users(user_)
    except Exception as e:
        await CHANNEL.log(str(e))
        user_e = None
    if not pfp_:
        pfp_ = "profilepic.jpg"
        with open(pfp_, "wb") as f:
            f.write(
                requests.get(
                    "https://telegra.ph/file/1fd74fa4a4dbf1655f3ec.jpg"
                ).content
            )
    text = "\n".join(wrap(input_str, 25))
    text = "“" + text + "„"
    font = ImageFont.truetype(FONT_FILE_TO_USE, 50)
    img = Image.open(pfp_)
    if "-b" in message.flags:
        img = img.convert("L")
    img = img.convert("RGBA").resize((1024, 1024))
    w, h = img.size
    nw, nh = 20 * (w // 100), 20 * (h // 100)
    nimg = Image.new("RGBA", (w - nw, h - nh), (0, 0, 0))
    nimg.putalpha(150)
    img.paste(nimg, (nw // 2, nh // 2), nimg)
    draw = ImageDraw.Draw(img)
    tw, th = draw.textsize(text=text, font=font)
    x, y = (w - tw) // 2, (h - th) // 2
    draw.text((x, y), text=text, font=font, fill="#ffffff", align="center")
    if user_e is not None:
        credit = "\n".join(
            wrap(f"by {user_e.first_name}", int(get_warp_length(w / 2.5)))
        )
        tw, th = draw.textsize(text=credit, font=font)
        draw.text(
            ((w - nw + tw) // 1.6, (h - nh - th)),
            text=credit,
            font=font,
            fill="#ffffff",
            align="left",
        )
    output = io.BytesIO()
    if "-s" in message.flags:
        output.name = "Jutsu.Webp"
        img.save(output, "webp")
        sticker = True
    else:
        output.name = "Jutsu.png"
        img.save(output, "PNG")
        sticker = False
    output.seek(0)
    if sticker:
        await userge.send_sticker(message.chat.id, output, reply_to_message_id=reply_to)
    else:
        await userge.send_photo(message.chat.id, output, reply_to_message_id=reply_to)
    await msg_.delete()
    for i in [pfp_]:
        if os.path.lexists(i):
            os.remove(i)


@userge.on_cmd(
    "q_n",
    about={
        "header": "Makes your message as sticker quote.",
        "usage": "{tr}q [reply to message]",
    },
)
async def sticker_chat(message: Message):
    "Makes your message as sticker quote"
    reply_ = message.reply_to_message
    if not reply_:
        return await message.edit(
            "`Reply to a message to quote...`", del_in=5
        )
    fetchmsg = reply_.text
    repliedreply = None
    mediatype = msg_type(reply_)
    if mediatype and mediatype in ["photo", "video", "gif"]:
        return await message.edit("`Replied message is not supported...`", del_in=5)
    msg_ = await message.edit("`Making quote...`")
    user_ = (
        await userge.get_user(reply_.forward_from.from_user.id)
        if reply_.forward_from
        else reply_.from_user.id
    )
    res, catmsg = await process(fetchmsg, user, catquotes.client, reply, repliedreply)
    if not res:
        return
    outfi = os.path.join("./temp", "sticker.png")
    catmsg.save(outfi)
    endfi = convert_tosticker(outfi)
    await catquotes.client.send_file(catquotes.chat_id, endfi, reply_to=reply)
    await catevent.delete()
    os.remove(endfi)