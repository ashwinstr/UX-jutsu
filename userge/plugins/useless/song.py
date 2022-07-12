### By Ryuk ###


import glob
import os
import shutil
from pathlib import Path
from subprocess import call
from time import time

from userge import Config, Message, userge
from userge.plugins.misc.uploads import upload


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
    await message.edit("Downloading...")
    starttime = time()
    dl_path = os.path.join(Config.DOWN_PATH, str(starttime))
    yt_dl = f"yt-dlp -o {dl_path}/'%(title)s.%(ext)s' --write-thumbnail --extract-audio --audio-format opus --audio-quality 320K --embed-thumbnail 'ytsearch:{query}'"
    call(yt_dl, shell=True)
    s_path = ""
    for song in glob.glob(os.path.join(dl_path, "*")):
        if song.lower().endswith(".opus"):
            s_path = song
            await upload(message, Path(s_path))
    if os.path.exists(str(dl_path)):
        shutil.rmtree(dl_path)
