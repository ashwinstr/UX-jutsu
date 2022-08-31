### By Ryuk ###


import glob
import os
import shutil
import mutagen
from pathlib import Path
from subprocess import call
from time import time

from userge import Config, Message, userge


@userge.on_cmd(
    "song",
    about={
        "header": "Download Songs from Youtube.",
        "usage": "{tr}song alone\n{tr}song youtube link",
    },
)
async def song_dl(message: Message):
    query = message.input_str
    if not query:
        return await message.edit("Give a song name or link to download.", del_in=5)
    await message.edit("Searching....")
    starttime = time()
    dl_path = os.path.join(Config.DOWN_PATH, str(starttime))
    yt_dl = f"yt-dlp -o {dl_path}/'%(title)s.%(ext)s' --write-thumbnail --extract-audio --audio-format opus --audio-quality 320K --embed-thumbnail 'ytsearch:{query}'"
    call(yt_dl, shell=True)
    s_path = ""
    t_path = ""
    for file_ in glob.glob(os.path.join(dl_path, "*")):
        if file_.lower().endswith(".opus"):
            s_path = file_
            duration = mutagen.File(s_path).info.length
        if file_.lower().endswith((".jpg", ".webp", ".png")):
            t_path = file_
    if not s_path:
        return await message.edit("Not found")
    await message.edit("Uploading....",del_in=3)
    await message.reply_audio(audio=s_path, duration = int(duration), thumb = t_path )
    if os.path.exists(str(dl_path)):
        shutil.rmtree(dl_path)
