# ported from oub-remix to USERGE-X by AshSTR/ashwinstr

import os

import lyricsgenius

from userge import Message, userge
from userge.helpers import capitaled
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
            "-no_p": "Disable preview",
            "-t": "With telegra.ph link...",
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
            s_list.append(f'• <code>{hits[number]["result"]["full_title"]}</code>')
            number += 1
        s_list = "\n".join(s_list)
        await message.edit(f"Songs matching [<b>{song}</b>]:\n\n" f"{s_list}")
        return
    artist = ""
    if " - " in song:
        artist, song = song.split("-", 1)
        artist = artist.strip()
        artist = capitaled(artist)
    song = song.strip()
    song = capitaled(song)
    if artist == "":
        title = song
    else:
        title = f"{artist} - {song}"
    await message.edit(f"Searching lyrics for **{title}** on Genius...`")
    dis_pre = False
    try:
        lyr = genius.search_song(song, artist)
    except Exception:
        await message.edit(f"Couldn't find <code>{title}</code> on genius...", del_in=5)
        return
    if lyr is None:
        await message.edit(f"Couldn't find `{title}` on Genius...")
        return
    lyric = lyr.lyrics
    lyrics = f"\n{lyric}</i>"
    lyrics += f"\n\n<b>Source:</b> <code>genius.com</code>"
    lyrics = (
        lyrics.replace("[", "</i><b>[")
        .replace("]", "]</b><i>")
        .replace("EmbedShare", "")
        .replace("URLCopyEmbedCopy", "")
    )
    lyr_msg = f"Lyrics for <b>{title}</b>...\n\n<i>{lyrics}"
    if len(lyr_msg) <= 4096 and "-t" not in flag and "-pre" not in flag:
        await message.edit(f"{lyr_msg}")
    else:
        if "-no_p" in flag:
            dis_pre = True
        lyrics = lyrics.replace("\n", "<br>")
        link = post_to_telegraph(f"Lyrics for {title}...", f"<i>{lyrics}")
        await message.edit(
            f"Lyrics for [<b>{title}</b>]({link}) by genius.com...",
            disable_web_page_preview=dis_pre,
        )
