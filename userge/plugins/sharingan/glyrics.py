# ported from oub-remix to USERGE-X by AshSTR/ashwinstr

import json
import os

import aiohttp
import lyricsgenius
import requests
from bs4 import BeautifulSoup
from googlesearch import search

from userge import Message, userge
from userge.utils import post_to_telegraph

GENIUS = os.environ.get("GENIUS")

CHANNEL = userge.getCLogger(__name__)

if GENIUS is not None:
    genius = lyricsgenius.Genius(GENIUS)


@userge.on_cmd(
    "glyrics",
    about={
        "header": "Lyrics using Genius API",
        "description": "Song lyrics from Genius.com",
        "flags": {
            "-t": "With telegra.ph link...",
            "-pre": "telegr.ph link with preview",
            "-s": "Search song names...",
        },
        "usage": "{tr}glyrics [Artist name] - [Song name]",
        "examples": "{tr}glyrics Eminem - Higher",
    },
)
async def lyrics(message: Message):
    """Lyrics from genius.com"""
    song = message.filtered_input_str or message.reply_to_message.text
    flag = message.flags
    if not song:
        await message.err("Search song lyrics without song name?", del_in=5)
        return
    if GENIUS is None:
        await message.err(
            "Provide 'Genius access token' as `GENIUS` to config vars...\nGet it from docs.genius.com...",
            del_in=5,
        )
        return
    if len(flag) > 1:
        await message.edit("Only one flag at a time please...", del_in=5)
        return
    if "-s" in flag:
        songs = genius.search_songs(song)
        await message.edit(f"Searching songs matching <b>{song}</b>...")
        number = 0
        s_list = []
        hits = songs["hits"]
        for one in hits:
            s_list.append(f'◾️ <code>{hits[number]["result"]["full_title"]}</code>')
            number += 1
        s_list = "\n".join(s_list)
        await message.edit(f"Songs matching [<b>{song}</b>]:\n\n" f"{s_list}")
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
        artist = " ".join(artist_a)
    song = song.strip()
    name_s = song.split()
    song_s = []
    for s in name_s:
        s = s.capitalize()
        song_s.append(s)
    song = " ".join(song_s)
    if artist == "":
        title = song
    else:
        title = f"{artist} - {song}"
    await message.edit(f"Searching lyrics for **{title}** on Genius...`")
    dis_pre = True
    try:
        lyr = genius.search_song(song, artist)
    except Exception:
        name = f"{song} {artist}"
        data = {"searchTerm": name}
        async with aiohttp.request(
            "POST",
            "http://www.glyrics.xyz/search",
            headers={
                "content-type": "application/json",
            },
            data=json.dumps(data),
        ) as result:
            lyric = await result.text()
        lyr = json.loads(lyric)
        lyr = lyr["lyrics"]
        if not lyr:
            await message.edit(
                f"Sorry, couldn't find lyrics for <code>{title}</code>...", del_in=5
            )
            return
        lyrics = f"\n{lyr}"
        lyrics += f"\n\n<b>Written by:</b> <code>{writers}</code>"
        lyrics += f"\n<b>Source:</b> <code>genius.com</code>"
        lyrics = lyrics.replace("[", "<b>[").replace("]", "]</b>")
        full_lyr = f"Lyrics for **{title}** by Genius.com...\n\n{lyrics}"
        if len(full_lyr) <= 4096 and "-t" not in flag and "-pre" not in flag:
            await message.edit(full_lyr)
        else:
            if "-pre" in flag:
                dis_pre = False
            lyrics = lyrics.replace("\n", "<br>")
            link = post_to_telegraph(f"Lyrics for {title}...", lyrics)
            await message.edit(
                f"Lyrics for [<b>{title}</b>]({link}) by genius.com...",
                disable_web_page_preview=dis_pre,
            )
        return
    if lyr is None:
        await message.edit(f"Couldn't find `{title}` on Genius...")
        return
    lyric = lyr.lyrics
    lyrics = f"\n{lyric}"
    lyrics += f"\n\n<b>Written by:</b> <code>{writers}</code>"
    lyrics += f"\n<b>Source:</b> <code>genius.com</code>"
    lyrics = lyrics.replace("[", "<b>[")
    lyrics = lyrics.replace("]", "]</b>")
    lyr_msg = f"Lyrics for <b>{title}</b>...\n\n{lyrics}"
    if len(lyr_msg) <= 4096 and "-t" not in flag and "-pre" not in flag:
        await message.edit(f"{lyr_msg}")
    else:
        if "-pre" in flag:
            dis_pre = False
        lyrics = lyrics.replace("\n", "<br>")
        link = post_to_telegraph(f"Lyrics for {title}...", lyrics)
        await message.edit(
            f"Lyrics for [<b>{title}</b>]({link}) by genius.com...",
            disable_web_page_preview=dis_pre,
        )
