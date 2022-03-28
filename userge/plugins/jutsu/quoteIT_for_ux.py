import asyncio
import json
import os

from pyrogram import filters

from userge import Message, userge
from userge.config import Config


@userge.on_cmd(
    "twit",
    about={
        "header": "make replied message a fake tweet",
        "flags": {
            "-f": "add fake text in the fake tweet",
            "-b": "black background",
        },
        "usage": "{tr}twit [reply to message]",
    },
)
async def make_tweet(message: Message):
    try:
        await userge.get_chat_member(-1001331162912, message.from_user.id)
    except BaseException:
        if message.from_user.id not in Config.TRUSTED_SUDO_USERS:
            return await message.edit(
                "First join **@UX_xplugin_support** and get approved by Kakashi."
            )
    reply_ = message.replied
    if not reply_:
        return await message.edit("`Reply to message...`", del_in=5)
    name_ = reply_.from_user.first_name
    username_ = "@" + reply_.from_user.username
    pfp_ = reply_.from_user.photo.big_file_id if reply_.from_user.photo else None
    text_ = (
        reply_.text
        if reply_.text and "-f" not in message.flags
        else message.filtered_input_str
    )
    fake_ = True if "-f" in message.flags else False
    bg_ = (26, 43, 60) if "-b" not in message.flags else (0, 0, 0)
    if not text_:
        return await message.edit("`Text not found...`", del_in=5)
    await message.edit("`Making tweet...`")
    bot_ = "QuoteIT_thebot"
    form_ = {
        "cmd": "TWEET_IT",
        "name": name_,
        "username": username_,
        "text": text_,
        "background": bg_,
        "fake": fake_,
    }
    json_ = json.dumps(form_, indent=4)
    if pfp_:
        down_ = await userge.download_media(pfp_)
        await userge.send_photo(bot_, down_, caption=json_)
        os.remove(down_)
    else:
        await userge.send_message(bot_, json_)
    try:
        async with userge.conversation(bot_, timeout=20) as conv:
            response = await conv.get_response(mark_read=True, filters=(filters.bot))
    except TimeoutError:
        return await message.edit("`Bot didn't respond...`", del_in=5)
    resp = response.text
    if resp != "Sticker done.":
        return await message.edit(resp, del_in=5)
    result = await userge.get_inline_bot_results(
        bot_, f"tweetIT {message.from_user.id} -done"
    )
    await asyncio.gather(
        userge.send_inline_bot_result(
            chat_id=message.chat.id,
            query_id=result.query_id,
            result_id=result.results[0].id,
            reply_to_message_id=reply_.message_id,
        ),
        message.delete(),
    )


@userge.on_cmd(
    "qit",
    about={
        "header": "make replied message a telegram quote",
        "flags": {
            "-r": "add the replied message of quote message",
            "-f": "add fake text",
        },
        "usage": "{tr}qit [reply to message]",
    },
)
async def make_quote(message: Message):
    try:
        await userge.get_chat_member(-1001331162912, message.from_user.id)
    except BaseException:
        if message.from_user.id not in Config.TRUSTED_SUDO_USERS:
            return await message.edit(
                "First join **@UX_xplugin_support** and get approved by Kakashi."
            )
    reply_ = message.replied
    if not reply_:
        return await message.edit("`Reply to message...`", del_in=5)
    name_ = reply_.from_user.first_name
    pfp_ = reply_.from_user.photo.big_file_id if reply_.from_user.photo else None
    text_ = reply_.text if "-f" not in message.flags else message.filtered_input_str
    fake_ = True if "-f" in message.flags else False
    if not text_:
        return await message.edit("`Text not found...`", del_in=5)
    await message.edit("`Making quote...`")
    if "-r" in message.flags:
        reply_msg = await userge.get_messages(message.chat.id, reply_.message_id)
        reply_name = reply_msg.reply_to_message.from_user.first_name
        reply_text = (reply_msg.reply_to_message.text).splitlines()[0]
    else:
        reply_name = None
        reply_text = None
    bot_ = "QuoteIT_thebot"
    form_ = {
        "cmd": "QUOTE_IT",
        "name": name_,
        "text": text_,
        "reply_name": reply_name,
        "reply_text": reply_text,
        "fake": fake_,
    }
    json_ = json.dumps(form_, indent=4)
    if pfp_:
        down_ = await userge.download_media(pfp_)
        await userge.send_photo(bot_, down_, caption=json_)
        os.remove(down_)
    else:
        await userge.send_message(bot_, json_)
    try:
        async with userge.conversation(bot_, timeout=20) as conv:
            response = await conv.get_response(mark_read=True, filters=(filters.bot))
    except TimeoutError:
        return await message.edit("`Bot didn't respond...`", del_in=5)
    resp = response.text
    if resp != "Sticker done.":
        return await message.edit(resp, del_in=5)
    result = await userge.get_inline_bot_results(
        bot_, f"quoteIT {message.from_user.id} -done"
    )
    await asyncio.gather(
        userge.send_inline_bot_result(
            chat_id=message.chat.id,
            query_id=result.query_id,
            result_id=result.results[0].id,
            reply_to_message_id=reply_.message_id,
        ),
        message.delete(),
    )
