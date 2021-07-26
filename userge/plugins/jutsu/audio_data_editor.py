# made for USERGE-X by @Kakashi_HTK(tg)/@ashwinstr(gh)

import os

from userge import Message, userge


@userge.on_cmd(
    "alb",
    about={
        "header": "Audio name editor",
        "description": "Change audio name, singer name, album art.",
        "flags": {
            "-a": "album art",
            "-p": "performer",
            "-t": "title",
        },
        "usage": "{tr}alb [flag] [name or album art file location]\n"
        "enter input w.r.t. order of flags shown in help",
    },
)
async def album_edt(message: Message):
    """Audio name editor"""
    reply_ = message.reply_to_message
    if not reply_ or not reply_.audio:
        await message.edit("Reply to an audio file...")
        return
    chat_ = message.chat.id
    file_ = await userge.download_media(reply_)
    flag = message.flags
    input_ = message.filtered_input_str
    if not input_:
        await message.err("No input found...", del_in=5)
        return
    flag_list = list(flag)
    split_input_ = input_.split(";")
    list_input_ = list(split_input_)
    await message.reply(len(list_input_))
    if len(split_input_) > 2 or len(flag_list) > 2:
        await message.err("Don't enter more then two '<b>;</b>' or flags...", del_in=5)
        return
    elif len(split_input_) == 2 and len(flag_list) == 2:
        if ("-a" and "-p") in flag_list:
            album_art, performer = split_input_
            try:
                await userge.send_audio(
                    chat_, file_, thumb=album_art, performer=performer
                )
            except BaseException:
                await message.err(
                    f"Album art file location <code>{album_art}</code> might be invalid, check again...",
                    del_in=5,
                )
                return
        elif ("-a" and "-t") in flag_list:
            album_art, title = split_input_
            try:
                await userge.send_audio(chat_, file_, thumb=album_art, title=title)
            except BaseException:
                await message.err(
                    f"Album art file location <code>{album_art}</code> might be invalid, check again...",
                    del_in=5,
                )
                return
        elif ("-p" and "-t") in flag_list:
            performer, title = split_flag_
            try:
                await userge.send_audio(chat_, file_, performer=performer, title=title)
            except BaseException:
                await message.err(
                    f"Something unexpected happened, try again...", del_in=5
                )
                return
        else:
            await message.err(
                "Invalid flags, check help of command <code>alb</code>...", del_in=5
            )
            return
    elif len(split_input_) == 1 and len(flag_list) == 1:
        if "-a" in sort_flag:
            album_art = split_input_[0]
            try:
                await userge.send_audio(chat_, file_, thumb=album_art)
            except BaseException:
                await message.err(
                    f"Album art file location <code>{album_art}</code> might be invalid, check again...",
                    del_in=5,
                )
                return
        elif "-t" in flag_list:
            title = split_input_[0]
            try:
                await userge.send_audio(chat_, file_, title=title)
            except BaseException:
                await message.err(
                    f"Something unexpected happened, try again...", del_in=5
                )
                return
        elif "-p" in flag_list:
            performer = split_flag_[0]
            try:
                await userge.send_audio(chat_, file, performer=performer)
            except BaseException:
                await message.err(
                    f"Something unexpected happened, try again...", del_in=5
                )
                return
        else:
            await message.err(
                "Invalid flag, check help of command <code>alb</code>...", del_in=5
            )
            return
    elif len(flag_list) == 0:
        await message.err(
            "This command requires a proper flag to be passed...", del_in=5
        )
        return
    else:
        await message.err("Number of flags and inputs didn't match...", del_in=5)
        return
    await message.delete()
    os.remove(file_)
