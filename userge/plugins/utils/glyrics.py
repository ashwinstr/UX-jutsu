# ported from oub-remix to USERGE-X by AshSTR/ashwinstr

import lyricsgenius
import requests

from bs4 import BeautifulSoup
from googlesearch import search
from userge import Message, userge, Config
from userge.utils import post_to_telegraph

if Config.GENIUS is not None:
    genius = lyricsgenius.Genius(Config.GENIUS)


@userge.on_cmd(
    "glyrics",
    about={
        "header": "Lyrics using Genius API",
        "description": "Song lyrics from Genius.com",
        "usage": "{tr}glyrics [Artist name] - [Song name]",
        "examples": "{tr}glyrics Eminem - Higher",
    },
)
async def lyrics(message: Message):
    song = message.input_str or message.reply_to_message.text
    if not song:
        await message.err("Search song lyrics without song name?")
        return
    if Config.GENIUS is None:
        await message.err("Provide 'Genius access token' as `GENIUS` to config vars...\nGet it from docs.genius.com")
        return
    
    to_search = song + "genius lyrics"
    gen_surl = list(search(to_search, num=1, stop=1))[0]
    gen_page = requests.get(gen_surl)
    scp = BeautifulSoup(gen_page.text, "html.parser")
    writers_box = [
        writer
        for writer in scp.find_all("span", {"class": "metadata_unit-label"})
        if writer.text == "Written By"
    ]
    if writers_box:
        target_node = writers_box[0].find_next_sibling(
            "span", {"class": "metadata_unit-info"}
        )
        writers = target_node.text.strip()
    else:
        writers = "Couldn't find writers..."

    artist = ""
    if " - " in song:
        artist, song = song.split("-", 1)
        artist = artist.strip()
        name_a = artist.split()
        artist_a = []
        for a in name_a:
            a = a.capitalize()
            artist_a.append(a)
        artist = " ".join(map(str, artist_a))
    song = song.strip()
    name_s = song.split()
    song_s = []
    for s in name_s:
        s = s.capitalize()
        song_s.append(s)
    song = " ".join(map(str, song_s)) 
    title = f"{artist} - {song}"
    if artist == "":
        title = title.replace(" - ", "")
    await message.edit(f"Searching lyrics for **{title}** on Genius...`")
    lyr = genius.search_song(song, artist)
    if lyr is None:
        await message.edit(f"Couldn't find `{title}` on Genius...")
        return
    lyric = lyr.lyrics
    lyrics = f"\n{lyric}"
    lyrics += f"\n\n<b>Written by: </b><code>{writers}</code>"
    lyrics += f"\n<b>Source: </b><code>genius.com</code>"
    lyrics = lyrics.replace("[", "<b>[")
    lyrics = lyrics.replace("]", "]</b>")
    lyr_msg = f"Lyrics for <b>{title}</b>...\n\n{lyrics}"
    if len(lyr_msg) <= 4096:
        await message.edit(f"{lyr_msg}")
    else:
        lyrics = lyrics.replace("\n", "<br>") 
        link = post_to_telegraph(f"Lyrics for {title}...", lyrics)
        await message.edit(f"Lyrics for **{title}** by Genius.com...\n[Link]({link})")
