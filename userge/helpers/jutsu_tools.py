# tools for jutsu plugins by @Kakashi_HTK(tg)/@ashwinstr(gh)

import asyncio
from typing import Union
from pyrogram.errors import UserNotParticipant
from pyrogram.raw.functions.account import ReportPeer
from pyrogram.raw.types import (
    InputPeerUserFromMessage,
    InputReportReasonPornography,
    InputReportReasonSpam,
)
from userge import userge


# capitalise
def capitaled(query: str):
    query_split = query.split()
    cap_text = []
    for word_ in query_split:
        word_cap = word_.capitalize()
        cap_text.append(word_cap)
    cap_query = " ".join(cap_text)
    return cap_query


# to report for spam or pornographic content
def report_user(chat: int, user_id: int, msg: dict, msg_id: int, reason: str):
    if ("nsfw" or "NSFW" or "porn") in reason:
        reason_ = InputReportReasonPornography()
        for_ = "pornographic message"
    else:
        reason_ = InputReportReasonSpam()
        for_ = "spam message"
    peer_ = (
        InputPeerUserFromMessage(
            peer=chat,
            msg_id=msg_id,
            user_id=user_id,
        ),
    )
    ReportPeer(
        peer=peer_,
        reason=reason_,
        message=msg,
    )
    return for_


# return time and date after applying time difference
def time_date_diff(year: int, month: int, date: int, hour: int, minute: int, diff: str):
    """time and date changer as per time-zone difference"""
    differ = diff.split(":")
    if int(differ[0]) >= 12 or int(differ[0]) <= -12 or int(differ[1]) >= 60:
        return "`Format of the difference given is wrong, check and try again...`"
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
                ts = "PM"
            elif hour > 12 and hour < 24:
                hour -= 12
                ts = "PM"
            elif hour == 12:
                ts = "PM"
            else:
                ts = "AM"
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
                minute -= 60
            hour += hour_diff
            if hour > 12 and hour < 24:
                hour -= 12
                ts = "PM"
            elif hour == 12:
                ts = "PM"
            elif hour >= 24:
                hour -= 24
                date += 1
                ts = "AM"
            if date > 30 and (month == 4 or month == 6 or month == 9 or month == 11):
                month += 1
                date -= 30
            elif date > 28 and month == 2 and year % 4 != 0:
                month += 1
                date -= 28
            elif date > 29 and month == 2 and year % 4 == 0:
                month += 1
                date -= 29
            elif date > 31 and (
                month == 1
                or month == 3
                or month == 5
                or month == 7
                or month == 8
                or month == 10
                or month == 12
            ):
                month += 1
                date -= 31
                if month > 12:
                    month -= 12
                    year += 1
        hour = f"{hour:02}"
        minute = f"{minute:02}"
        date = f"{date:02}"
        month = f"{month:02}"
        json_ = {
            "hour": hour,
            "min": minute,
            "stamp": ts,
            "date": date,
            "month": month,
            "year": year,
        }
        return json_
    except Exception as e:
        return e

    
async def admin_or_creator(chat_id: int, user_id: int) -> dict:
    check_status = await userge.get_chat_member(chat_id, user_id)
    admin_ = True if check_status.status == "administrator" else False
    creator_ = True if check_status.status == "creator" else False
    json_ = {"is_admin": admin_, "is_creator": creator_}
    return json_


async def admin_chats(user_id: int) -> dict:
    list_ = []
    try:
        user_ = await userge.get_users(user_id)
    except:
        raise
        return
    async for dialog in userge.iter_dialogs():
        if dialog.chat.type in ["group", "supergroup", "channel"]:
            try:
                check = await admin_or_creator(dialog.chat.id, user_.id)
                is_admin = check['is_admin']
                is_creator = check['is_creator']
            except UserNotParticipant:
                is_admin = False
                is_creator = False
            chat_ = dialog.chat
            if is_admin or is_creator:
                list_.append(
                    {
                        "chat_name": chat_.title,
                        "chat_id": chat_.id,
                        "chat_username": chat_.username,
                        "admin": is_admin,
                        "creator": is_creator,
                    }
                )
    return list_


async def get_response(msg, filter_user: Union[int, str] = 0, timeout: int = 5, mark_read: bool = False):
    await asyncio.sleep(timeout)
    if filter_user:
        try:
            user_ = await userge.get_users(filter_user)
        except:
            raise "Invalid user."
    for msg_ in range(1, 6):
        msg_id = msg.message_id + msg_
        try:
            response = await userge.get_messages(msg.chat.id, msg_id)
        except:
            raise "No response found."
        if response.reply_to_message.message_id == msg.message_id:
            if filter_user:
                if response.from_user.id == user_.id:
                    if mark_read:
                        await userge.send_read_acknowledge(msg.chat.id, response)
                    return response
            else:
                if mark_read:
                    await userge.send_read_acknowledge(msg.chat.id, response)
                return response
        
    raise "No response found in time limit."


#async def get_response(msg, filter_user: Union[int, str] = 0, timeout: int = 5, mark_read: bool = False):
#    try:
#       _response = await asyncio.wait_for(response(msg, filter_user, mark_read), timeout=timeout)
#    except:
#        raise
#    return _response


def full_name(user: dict):
    try:
        f_name = " ".join([user.first_name, user.last_name or ""])
    except:
        raise
    return f_name


def msg_type(message):
    type_ = "text"
    if message.audio:
        type_ = "audio"
    elif message.animation:
        type_ = "gif"
    elif message.document:
        type_ = "file"
    elif message.photo:
        type_ = "photo"
    elif message.sticker:
        type_ = "sticker"
    elif message.video:
        type_ = "video"
    return type_
