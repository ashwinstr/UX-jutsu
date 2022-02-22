import os

from pymediainfo import MediaInfo

from userge import Message, userge


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
    media_info = MediaInfo.parse(down_)
    out_ = "`Nothing found...`"
    for track in media_info.tracks:
        if track.track_type == "Video":
            try:
                size_ = track.other_stream_size[3]
            except BaseException:
                size_ = track.stream_size
            out_ = f"""
<b><u>Media Info of the replied media.</u></b>

• <b>Type:</b> {track.track_type}
• <b>Format:</b> {track.format}
• <b>Duration:</b> {track.other_duration[0]} - ({track.other_duration[3]})
• <b>Width:</b> {track.width} pixels
• <b>Height:</b> {track.height} pixels
• <b>Aspect ratio:</b> {track.other_display_aspect_ratio[0]}
• <b>Frame rate:</b> {track.frame_rate} FPS
• <b>Frame count:</b> {track.frame_count}
• <b>Size:</b> {size_}
"""
    await message.edit(out_)
    os.remove(down_)


async def duration(message: Message):
    reply_ = message.replied
    if not reply_:
        return await message.edit("`Reply to media...`", del_in=5)
    down_ = await reply_.download()
    media_info = MediaInfo.parse(down_)
    for track in media_info.tracks:
        if track.track_type == "Video":
            time_ = float(str(track.other_duration[3]).split(":")[-1])
            return time_
    os.remove(down_)
    return "`Nothing found...`"
