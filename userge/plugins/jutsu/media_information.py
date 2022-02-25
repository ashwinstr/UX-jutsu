import os

from userge import userge, Message
from userge.helpers import Media_Info


@userge.on_cmd(
    "media_in",
    about={
        "header": "get mediainfo",
        "usage": "{tr}media_in [reply to media]",
    },
)
async def media_info_(message: Message):
    reply_ = message.replied
    if not reply_.media:
        return await message.edit("`Reply to media...`", del_in=5)
    down_ = await reply_.download()
    info_ = Media_Info.data(down_)
    if info_:
        fps_ = f"{info_['frame_rate']} FPS" if info_["frame_rate"] else None
        out_ = f"""
<b><u>Media Info of the replied media.</u></b>

• <b>Type:</b> {info_["media_type"]}
• <b>Format:</b> {info_["format"]}
• <b>Duration:</b> {info_["duration"]}
• <b>Width:</b> {info_["pixel_sizes"][0]} pixels
• <b>Height:</b> {info_["pixel_sizes"][1]} pixels
• <b>Aspect ratio:</b> {info_["aspect_ratio"]}
• <b>Frame rate:</b> {fps_}
• <b>Frame count:</b> {info_["frame_count"]}
• <b>Size:</b> {info_["file_size"]}
"""
        del_ = -1
    else:
        out_ = "`Couldn't find media information...`"
        del_ = 5
    await message.edit(out_, del_in=del_)
    os.remove(down_)