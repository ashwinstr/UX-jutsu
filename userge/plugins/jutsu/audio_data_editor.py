# plugin made for USERGE-X by @Kakashi_HTK(TG)/@ashwinstr(GH)
# before porting please ask to Kakashi
# v3.1.5

import os

from userge import Message, userge


@userge.on_cmd(
    "alb",
    about={
        "header": "Audio name editor",
        "description": "Change audio name, singer name, album art.",
        "flags": {
            "-t": "title",
        },
        "usage": "{tr}alb [title and/or album art file location]\n",
    },
)
async def album_edt(message: Message):
    """Audio name editor"""
    reply_ = message.reply_to_message
    if not reply_ or not reply_.audio:
        await message.edit("`Reply to an audio file...`")
        return
    album_thumb = reply_.audio.thumbs
    if album_thumb is not None:
        album_art_id = album_thumb[0].file_id
        album_art = await userge.download_media(album_art_id)
    else:
        album_art = None
    performer = reply_.audio.performer
    title = reply_.audio.title
    chat_ = message.chat.id
    file_ = await userge.download_media(reply_)
    flag_ = message.flags
    input_ = message.filtered_input_str
    if not input_:
        await message.err("`No input found...`", del_in=5)
        return
    await message.edit("`Editing meta-data...`")
    if ";" in input_:
        split_input_ = input_.split(";")
        if len(split_input_) > 2:
            await message.edit("`Please give no more than two inputs...`", del_in=5)
            return
        for single_input_ in split_input_:
            if "/" in single_input_:
                album_art = single_input_
            else:
                performer = single_input_
        try:
            await userge.send_audio(chat_, file_, thumb=album_art, performer=performer)
        except BaseException:
            await message.err(
                f"Album art file location <code>{album_art}</code> might be invalid, check again...",
                del_in=5,
            )
        await message.delete()
        os.remove(file_)
        return
    if "-t" in flag_:
        title = input_
    else:
        if "/" in input_:
            album_art = input_
        else:
            performer = input_
    try:
        await userge.send_audio(
            chat_, file_, thumb=album_art, performer=performer, title=title
        )
    except BaseException as e:
        await message.edit(
            f"`Something unexpected happened.`\n<b>ERROR:</b> `{e}`", del_in=5
        )
        return
    await message.delete()
    os.remove(album_art)
    os.remove(file_)
