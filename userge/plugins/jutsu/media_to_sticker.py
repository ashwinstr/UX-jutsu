# ported from oub-remix to USERGE-X by @Kakashi_HTK/@ashwinstr

import os

from userge import Config, Message, userge
from userge.helpers import Media_Info
from userge.utils import runcmd


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
    info_ = Media_Info.data(down_)
    width = info_["pixel_sizes"][0]
    height = info_["pixel_sizes"][1]
    if width == height:
        w, h = 512, 512
    elif width > height:
        w, h = 512, -1
    elif width < height:
        w, h = -1, 512
    if "-f" in message.flags:
        dure_ = int(info_["duration_in_ms"]) / 1000
        if dure_ > 3:
            fract_ = 3 / dure_
            ff_f = round(fract_, 2)
            set_pts_ = ff_f - 0.01 if ff_f > fract_ else ff_f
            cmd_f = f"-filter:v 'setpts={set_pts_}*PTS',scale={w}:{h}"
        else:
            cmd_f = f"-filter:v scale={w}:{h}"
    else:
        cmd_f = f"-ss 00:00:00 -to 00:00:03 -filter:v scale={w}:{h}"
    fps_ = float(info_["frame_rate"])
    fps_cmd = "-r 30 " if fps_ > 30 else ""
    resized_video = f"{down_}.webm"
    cmd = f"ffmpeg -i {down_} {cmd_f} -an {fps_cmd}-fs 256K {resized_video}"
    await runcmd(cmd)
    await reply.reply_sticker(resized_video)
    os.remove(down_)
    os.remove(resized_video)
