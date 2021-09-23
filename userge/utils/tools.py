# pylint: disable=missing-module-docstring
#
# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

import asyncio
import os
import re
import shlex
from os.path import basename
from typing import List, Optional, Tuple

from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from telegraph import Telegraph
from ujson import loads

import userge

tele_ = Telegraph()
_LOG = userge.logging.getLogger(__name__)

_BTN_URL_REGEX = re.compile(r"(\[([^\[]+?)]\[buttonurl:(?:/{0,2})(.+?)(:same)?])")


def get_file_id(
    message: "userge.Message",
) -> Optional[str]:
    """get file_id"""
    if message is None:
        return
    file_ = (
        message.audio
        or message.animation
        or message.photo
        or message.sticker
        or message.voice
        or message.video_note
        or message.video
        or message.document
    )
    return file_.file_id if file_ else None


def humanbytes(size: float) -> str:
    """humanize size"""
    if not size:
        return ""
    power = 1024
    t_n = 0
    power_dict = {0: " ", 1: "Ki", 2: "Mi", 3: "Gi", 4: "Ti"}
    while size > power:
        size /= power
        t_n += 1
    return "{:.2f} {}B".format(size, power_dict[t_n])


def time_formatter(seconds: float) -> str:
    """humanize time"""
    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = (
        ((str(days) + "d, ") if days else "")
        + ((str(hours) + "h, ") if hours else "")
        + ((str(minutes) + "m, ") if minutes else "")
        + ((str(seconds) + "s, ") if seconds else "")
    )
    return tmp[:-2]


def time_date(year: int, month: int, date: int, hour: int, minute: int, diff: str):
    """time and date changer as per time-zone difference"""
    differ = diff.split(":")
    if int(differ[0]) >= 12 or int(differ[0]) <= -12 or int(differ[1]) >= 60:
        return await message.edit(
            "`Format of the difference given is wrong, check and try again...`"
        )
    try:
        hour_diff = differ[0]
        hour_diff = int(hour_diff)
        min_diff = differ[1]
        min_diff = int(min_diff)

        if hour_diff < 0:
            minute -= min_diff
            if minute < 0:
                minute += 60
                hour -= 1
            hour -= hour_diff
            if hour < 0:
                date -= 1
                hour += 12
            elif hour > 12 and hour < 24:
                hour -= 12
            elif hour == 12:
                pass
            else:
                pass
            if date < 1:
                month -= 1
                if month < 1:
                    month = 12
                    year -= 1
                if month == (12 or 10 or 8 or 7 or 5 or 3 or 1):
                    date = 31
                elif month == (11 or 9 or 6 or 4):
                    date = 30
                else:
                    if year % 4 == 0:
                        date = 29
                    else:
                        date = 28
        else:
            minute += min_diff
            if minute >= 60:
                hour += 1
                if hour > 12 and hour < 24:
                    hour -= 12
                elif hour == 12:
                    pass
                elif hour >= 24:
                    hour -= 24
                    date += 1
                    if date > 30 and (month == (4 or 6 or 9 or 11)):
                        month += 1
                    elif date > 28 and month == 2 and year % 4 != 0:
                        month += 1
                    elif date > 29 and month == 2 and year % 4 == 0:
                        month += 1
                    elif date > 31 and (month == (1 or 3 or 5 or 7 or 8 or 10 or 12)):
                        month += 1
                        if month > 12:
                            year += 1
        hour = f"{hour:02}"
        minute = f"{minute:02}"
        date = f"{date:02}"
        month = f"{month:02}"
        json_ = {
            "min": minute,
            "hour": hour,
            "date": date,
            "month": month,
            "year": year,
        }
        return json_
    except Exception as e:
        return await message.err(e, del_in=5)


# https://github.com/UsergeTeam/Userge-Plugins/blob/master/plugins/anilist.py
def post_to_telegraph(a_title: str, content: str) -> str:
    """Create a Telegram Post using HTML Content"""
    auth_name = tele_.create_account("Kakashi")
    resp = tele_.create_page(
        title=a_title,
        author_name=auth_name,
        author_url="https://t.me/xplugin",
        html_content=content,
    )
    link_ = "https://telegra.ph/" + resp["path"]
    return link_


async def runcmd(cmd: str) -> Tuple[str, str, int, int]:
    """run command in terminal"""
    args = shlex.split(cmd)
    process = await asyncio.create_subprocess_exec(
        *args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    return (
        stdout.decode("utf-8", "replace").strip(),
        stderr.decode("utf-8", "replace").strip(),
        process.returncode,
        process.pid,
    )


async def take_screen_shot(
    video_file: str, duration: int, path: str = ""
) -> Optional[str]:
    """take a screenshot"""
    _LOG.info(
        "[[[Extracting a frame from %s ||| Video duration => %s]]]",
        video_file,
        duration,
    )
    ttl = duration // 2
    thumb_image_path = path or os.path.join(
        userge.Config.DOWN_PATH, f"{basename(video_file)}.jpg"
    )
    command = f'''ffmpeg -ss {ttl} -i "{video_file}" -vframes 1 "{thumb_image_path}"'''
    err = (await runcmd(command))[1]
    if err:
        _LOG.error(err)
    return thumb_image_path if os.path.exists(thumb_image_path) else None


def parse_buttons(markdown_note: str) -> Tuple[str, Optional[InlineKeyboardMarkup]]:
    """markdown_note to string and buttons"""
    prev = 0
    note_data = ""
    buttons: List[Tuple[str, str, str]] = []
    for match in _BTN_URL_REGEX.finditer(markdown_note):
        n_escapes = 0
        to_check = match.start(1) - 1
        while to_check > 0 and markdown_note[to_check] == "\\":
            n_escapes += 1
            to_check -= 1
        if n_escapes % 2 == 0:
            buttons.append((match.group(2), match.group(3), bool(match.group(4))))
            note_data += markdown_note[prev : match.start(1)]
            prev = match.end(1)
        else:
            note_data += markdown_note[prev:to_check]
            prev = match.start(1) - 1
    note_data += markdown_note[prev:]
    keyb: List[List[InlineKeyboardButton]] = []
    for btn in buttons:
        if btn[2] and keyb:
            keyb[-1].append(InlineKeyboardButton(btn[0], url=btn[1]))
        else:
            keyb.append([InlineKeyboardButton(btn[0], url=btn[1])])
    return note_data.strip(), InlineKeyboardMarkup(keyb) if keyb else None


# https://www.tutorialspoint.com/How-do-you-split-a-list-into-evenly-sized-chunks-in-Python
def sublists(input_list: list, width: int = 3):
    return [input_list[x : x + width] for x in range(0, len(input_list), width)]


# Solves ValueError: No closing quotation by removing ' or " in file name
def safe_filename(path_):
    if path_ is None:
        return
    safename = path_.replace("'", "").replace('"', "")
    if safename != path_:
        os.rename(path_, safename)
    return safename


def clean_obj(obj, convert: bool = False):
    if convert:
        # Pyrogram object to python Dict
        obj = loads(str(obj))
    if isinstance(obj, (list, tuple)):
        return [clean_obj(item) for item in obj]
    if isinstance(obj, dict):
        return {key: clean_obj(value) for key, value in obj.items() if key != "_"}
    return obj
