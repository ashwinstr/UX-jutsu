### By Ryuk ###


import glob
import os
import shutil
from subprocess import call
from time import time

import music_tag

from userge import Message, userge


@userge.on_cmd(
    "song",
    about={
        "header": "Download Songs from Youtube.",
        "usage": "{tr}song alone\n{tr}song youtube link\n{tr}song -m alone",
        "flags": {"-m": "To get mp3."},
    },
)
async def song_dl(message: Message):
    reply_query = None
    audio_path = None
    thumb_path = None
    artist = None
    reply = message.reply_to_message
    if reply:
        for link in reply.text.split():
            if link.startswith(("http://www.youtube.com", "https://www.youtube.com")):
                reply_query = link
                break
    query = reply_query if reply_query else message.filtered_input_str
    if not query:
        return await message.edit("Give a song name or link to download.", del_in=5)
    await message.edit("Searching....")
    starttime = time()
    dl_path = f"downloads/{starttime}"
    if "-m" in message.flags:
        quality = f"--audio-format mp3 --audio-quality 320K"
    else:
        quality = "--audio-format opus"
    yt_dl = f"yt-dlp -o {dl_path}/'%(title)s.%(ext)s' --write-thumbnail --extract-audio --embed-thumbnail {quality} --add-metadata 'ytsearch:{query}'"
    call(yt_dl, shell=True)
    for file_ in glob.glob(dl_path + "/*"):
        if file_.lower().endswith((".opus", ".mp3")):
            audio_path = file_
            audio_info = music_tag.load_file(audio_path)
            duration = audio_info["#length"]
            artist = audio_info["artist"]
        if file_.lower().endswith((".jpg", ".webp", ".png")):
            thumb_path = file_
    if not audio_path:
        return await message.edit("Not found")
    await message.edit("Uploading....")
    await message.reply_audio(
        audio=audio_path,
        duration=int(duration),
        performer=str(artist),
        thumb=thumb_path,
    )
    await message.delete()
    if os.path.exists(str(dl_path)):
        shutil.rmtree(dl_path)
