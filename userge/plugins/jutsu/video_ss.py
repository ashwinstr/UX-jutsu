# ported from oub-remix to USERGE-X by @Kakashi_HTK(tg)/@ashwinstr(gh)


import asyncio
import os
import time
import vcsi

from userge import Message, userge
from userge.utils import progress


@userge.on_cmd(
    "ssvid",
    about={
        "header": "take screenshot of video",
        "flags": {
            "-d": "send as document",
        },
        "usage": "{tr}ssvid [reply to video]",
    },
)
async def ss_video(message: Message):
    reply_ = message.reply_to_message
    if not reply_:
        return await message.edit("`Reply to video...`", del_in=5)
    if not reply_.video:
        return await message.edit("`Reply to a video...`", del_in=5)
    try:
        frame = int(message.filtered_input_str)
        if not frame:
            frame = 4
        if frame > 10:
            return await message.edit("`Limit is 10 frames...`", del_in=5)
    except BaseException:
        return await message.edit("`Please input number of frames...`", del_in=5)
    c_time = time.time()
    await message.edit("`Downloading media...`")
    ss = await userge.download_media(
        reply_,
        "ss.mp4",
        progress_args=lambda d, t: asyncio.get_event_loop().create_task(
            progress(d, t, reply_, c_time, "[DOWNLOAD]")
        ),
    )
    try:
        await message.edit("`Proccessing...`")
        command = f"vcsi -g {frame}x{frame} {ss} -o ss.png "
        os.system(command)
        if "-d" in message.flags:
            await userge.send_document(
                message.chat.id,
                "ss.png",
                reply_to_message_id=reply_.message_id,
            )
        else:
            await userge.send_photo(
                message.chat.id,
                "ss.png",
                reply_to_message_id=reply_.message_id,
            )
        await message.delete()
    except BaseException as e:
        await message.edit(f"<b>Error:</b> `{e}`", del_in=5)
    os.remove(ss)
    os.system("rm -rf ss.png")
