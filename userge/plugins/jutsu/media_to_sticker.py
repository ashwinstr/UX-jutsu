# ported from oub-remix to USERGE-X by @Kakashi_HTK/@ashwinstr

import os

from userge import Config, Message, userge
from userge.utils import runcmd

from .media_information import duration


@userge.on_cmd(
    "stick",
    about={
        "header": "Image to sticker",
        "description": "Convert any image to sticker w/o sticker bot",
        "flags": {
            "-f": "fast-forward [video/gif sticker]",
        },
        "usage": "{tr}stick [reply to image]",
    },
)
async def stik_(message: Message):
    reply = message.replied
    vid_ = False
    anim_ = False
    if not reply:
        return await message.edit("`Reply to image to convert...`", del_in=5)
    await message.edit("`Converting...`")
    if reply.photo:
        name_ = "sticker.webp"
        path_ = os.path.join(Config.DOWN_PATH, name_)
        if os.path.isfile(path_):
            os.remove(path_)
        down_ = await reply.download(path_)
        await reply.reply_sticker(down_)
        os.remove(down_)
        await message.delete()
        return
    elif reply.animation:
        anim_ = True
    elif reply.video:
        vid_ = True
    if not vid_ and not anim_:
        return await message.edit("`Unsupported file.`", del_in=5)
    down_ = await reply.download()
    media = reply.animation if anim_ else reply.video
    width = media.width
    height = media.height
    if width == height:
        w, h = 512, 512
    elif width > height:
        w, h = 512, -1
    elif width < height:
        w, h = -1, 512
    if "-f" in message.flags:
        dure_ = await duration(message)
        trim_ = 3 / float(dure_ + 0.01) - 0.01
        cmd_ = f"-filter:v 'setpts={trim_}*PTS',scale={w}:{h}"
    else:
        cmd_ = f"-ss 00:00:00 -to 00:00:03 -filter:v scale={w}:{h}"
    resized_video = f"{down_}.webm"
    cmd = f"ffmpeg -i {down_} {cmd_} -an -r 30 -fs 256K {resized_video}"
    await runcmd(cmd)
    await reply.reply_sticker(resized_video)
    os.remove(down_)
    os.remove(resized_video)
