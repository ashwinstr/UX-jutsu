""" system commands """
# Copyright (C) 2020-2021 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved.

# additions by @Kakashi_HTK(TG)/@ashwinstr(GH)


import asyncio
import os
import shutil
import time

from dotenv import get_key, load_dotenv, set_key, unset_key
from pyrogram.types import User

from userge import Config, Message, get_collection, userge
from userge.core.ext import RawClient
from userge.utils import runcmd, terminate

SAVED_SETTINGS = get_collection("CONFIGS")
DISABLED_CHATS = get_collection("DISABLED_CHATS")
FROZEN = get_collection("FROZEN")

MAX_IDLE_TIME = 300
LOG = userge.getLogger(__name__)
CHANNEL = userge.getCLogger(__name__)


async def _init() -> None:
    global MAX_IDLE_TIME  # pylint: disable=global-statement
    d_s = await SAVED_SETTINGS.find_one({"_id": "DYNO_SAVER"})
    if d_s:
        Config.RUN_DYNO_SAVER = bool(d_s["on"])
        MAX_IDLE_TIME = int(d_s["timeout"])
    disabled_all = await SAVED_SETTINGS.find_one({"_id": "DISABLE_ALL_CHATS"})
    if disabled_all:
        Config.DISABLED_ALL = bool(disabled_all["on"])
    else:
        async for i in DISABLED_CHATS.find():
            if i["_id"] == Config.LOG_CHANNEL_ID:
                continue
            Config.DISABLED_CHATS.add(i["_id"])


@userge.on_cmd(
    "restart",
    about={
        "header": "Restarts the bot and reload all plugins",
        "flags": {
            "-h": "restart hard",
            "-log": "reload userge-plugins repo (if 'restart -h' doesn't update custom plugins)",
            "-t": "clean temp loaded plugins",
            "-d": "clean working folder",
        },
        "usage": "{tr}restart [flag | flags]",
        "examples": "{tr}restart -t -d",
    },
    del_pre=True,
    allow_channels=False,
)
async def restart_(message: Message):
    """restart USERGE-X"""
    await message.edit("`Restarting USERGE-X Services`", log=__name__)
    LOG.info("USERGE-X Services - Restart initiated")
    if "t" in message.flags:
        shutil.rmtree(Config.TMP_PATH, ignore_errors=True)
    if "log" in message.flags:
        await message.edit("Restarting <b>logs</b>...", del_in=5)
        await runcmd("bash run")
        asyncio.get_event_loop().create_task(userge.restart())
        return
    if "d" in message.flags:
        shutil.rmtree(Config.DOWN_PATH, ignore_errors=True)
    if "h" in message.flags:
        if Config.HEROKU_APP:
            await message.edit(
                "`Heroku app found, trying to restart dyno...\nthis will take upto 30 sec`",
                del_in=3,
            )
            await FROZEN.drop()
            Config.HEROKU_APP.restart()
            time.sleep(30)
        else:
            await message.edit("`Restarting [HARD] ...`", del_in=1)
            await FROZEN.drop()
            asyncio.get_event_loop().create_task(userge.restart(hard=True))
    else:
        await message.edit("`Restarting [SOFT] ...`", del_in=1)
        asyncio.get_event_loop().create_task(userge.restart())


@userge.on_cmd(
    "shutdown", about={"header": "shutdown USERGE-X :)"}, allow_channels=False
)
async def shutdown_(message: Message) -> None:
    """shutdown USERGE-X"""
    await message.edit("`shutting down ...`")
    if Config.HEROKU_APP:
        try:
            Config.HEROKU_APP.process_formation()["worker"].scale(0)
        except Exception as h_e:  # pylint: disable=broad-except
            await message.edit(f"**heroku error** : `{h_e}`")
            await asyncio.sleep(3)
    else:
        await asyncio.sleep(1)
    await message.delete()
    terminate()


@userge.on_cmd(
    "setvar",
    about={
        "header": "set var",
        "usage": "{tr}setvar [var_name] [var_data]",
        "examples": "{tr}setvar WORKERS 4",
    },
)
async def setvar_(message: Message) -> None:
    """set var"""
    heroku = True
    if not Config.HEROKU_APP:
        heroku = False
        if os.path.exists("config.env"):
            pass
        else:
            await message.err("`Heroku app and config.env both not detected...`")
            return
    if not message.input_str:
        await message.err("`Input not found...`")
        return
    var_key, var_value = message.input_str.split(maxsplit=1)
    if not var_value:
        await message.err("`Var value not found...`")
        return
    var_key = var_key.strip()
    var_value = var_value.strip()
    if heroku:
        heroku_vars = Config.HEROKU_APP.config()
        if var_key in heroku_vars:
            await CHANNEL.log(
                f"#HEROKU_VAR #SET #UPDATED\n\n`{var_key}` = `{var_value}`"
            )
            await message.edit(
                f"`Var {var_key} updated and forwarded to log channel...`", del_in=3
            )
        else:
            await CHANNEL.log(f"#HEROKU_VAR #SET #ADDED\n\n`{var_key}` = `{var_value}`")
            await message.edit(
                f"`Var {var_key} added and forwarded to log channel...`", del_in=3
            )
        heroku_vars[var_key] = var_value
    else:
        file = "config.env"
        get = get_key(file, var_key)
        if get is not None:
            await message.edit(
                f"Var {var_key} updated and forwarded to log channel...", del_in=3
            )
            await CHANNEL.log(f"#CONFIG_VAR #UPDATED\n\n`{var_key} = {var_value}`")
        else:
            await message.edit(
                f"Var {var_key} added and forwarded to log channel...", del_in=3
            )
            await CHANNEL.log(f"#CONFIG_VAR #ADDED\n\n`{var_key} = {var_value}`")
        set_key(file, var_key, var_value)
        load_dotenv(file, override=True)


@userge.on_cmd(
    "delvar",
    about={
        "header": "del var",
        "usage": "{tr}delvar [var_name]",
        "examples": "{tr}delvar WORKERS",
    },
)
async def delvar_(message: Message) -> None:
    """del var"""
    heroku = True
    if not Config.HEROKU_APP:
        heroku = False
        if os.path.exists("config.env"):
            pass
        else:
            await message.err("`Heroku app and config.env both not detected...`")
            return
    if not message.input_str:
        await message.err("`Input not found...`")
        return
    var_key = message.input_str
    var_key = var_key.strip()
    if heroku:
        heroku_vars = Config.HEROKU_APP.config()
        if var_key in heroku_vars:
            await CHANNEL.log(f"#HEROKU_VAR #DELETED\n\n`{var_key}`")
            await message.edit(
                f"`Var {var_key} deleted and forwarded to log channel...`", del_in=3
            )
        else:
            await message.edit(f"`Var {var_key} doesn't exist...`", del_in=3)
            return
        del heroku_vars[var_key]
    else:
        file = "config.env"
        get = get_key(file, var_key)
        if get is not None:
            await message.edit(
                f"Var {var_key} deleted and forwarded to log channel...", del_in=3
            )
            await CHANNEL.log(f"#CONFIG_VAR #DELETED\n\n`{var_key}`")
        else:
            await message.edit(f"`Var {var_key} doesn't exist...`", del_in=3)
            return
        unset_key(file, var_key)
        load_dotenv(file, override=True)


@userge.on_cmd(
    "getvar",
    about={
        "header": "get var",
        "usage": "{tr}getvar [var_name]",
        "examples": "{tr}getvar WORKERS",
    },
)
async def getvar_(message: Message) -> None:
    """get var"""
    heroku = True
    if not Config.HEROKU_APP:
        heroku = False
        if os.path.exists("config.env"):
            pass
        else:
            await message.err("`Heroku app and config.env both not detected...`")
            return
    if not message.input_str:
        await message.err("`Input not found...`")
        return
    var_key = message.input_str
    var_key = var_key.strip()
    if heroku:
        heroku_vars = Config.HEROKU_APP.config()
        if var_key in heroku_vars:
            await CHANNEL.log(
                f"#HEROKU_VAR #GET\n\n`{var_key}` = `{heroku_vars[var_name]}`"
            )
            await message.edit(f"`Var {var_key} forwarded to log channel...`", del_in=3)
        else:
            await message.edit(f"`Var {var_key} doesn't exist...`", del_in=3)
            return
    else:
        file = "config.env"
        get = get_key(file, var_key)
        if get is not None:
            await message.edit(
                f"Var {var_key} value forwarded to log channel...", del_in=3
            )
            await CHANNEL.log(f"#CONFIG_VAR #GET\n\n`{var_key} = {get}`")
        else:
            await message.edit(f"`Var {var_key} doesn't exist...`", del_in=3)
            return


@userge.on_cmd(
    "enhere",
    about={
        "header": "enable userbot in disabled chat.",
        "flags": {"-all": "Enable Userbot in all chats."},
        "usage": "{tr}enhere [chat_id | username]\n{tr}enhere -all",
    },
)
async def enable_userbot(message: Message):
    if message.flags:
        if "-all" in message.flags:
            Config.DISABLED_ALL = False
            Config.DISABLED_CHATS.clear()
            await asyncio.gather(
                DISABLED_CHATS.drop(),
                SAVED_SETTINGS.update_one(
                    {"_id": "DISABLE_ALL_CHATS"}, {"$set": {"on": False}}, upsert=True
                ),
                message.edit("**Enabled** all chats!", del_in=5),
            )
        else:
            await message.err("invalid flag!")
    elif message.input_str:
        try:
            chat = await message.client.get_chat(message.input_str)
        except Exception as err:
            await message.err(str(err))
            return
        if chat.id not in Config.DISABLED_CHATS:
            await message.edit("This chat is already enabled!")
        else:
            Config.DISABLED_CHATS.remove(chat.id)
            if chat.type == "private":
                c_name = " ".join([chat.first_name, chat.last_name or ""])
            else:
                c_name = chat.title
            await asyncio.gather(
                DISABLED_CHATS.delete_one({"_id": chat.id}),
                message.edit(
                    f"CHAT : `{c_name}` removed from **DISABLED_CHATS**!\n`Bot might restart, wait for some time...`",
                    del_in=5,
                    log=__name__,
                ),
            )
    else:
        await message.err("chat_id not found!")


@userge.on_cmd(
    "dishere",
    about={
        "header": "disable userbot in current chat.",
        "flags": {"-all": "disable Userbot in all chats."},
        "usage": "{tr}dishere\n{tr}dishere [chat_id | username]\n{tr}dishere -all",
    },
)
async def disable_userbot(message: Message):
    if message.flags:
        if "-all" in message.flags:
            Config.DISABLED_ALL = True
            await asyncio.gather(
                SAVED_SETTINGS.update_one(
                    {"_id": "DISABLE_ALL_CHATS"}, {"$set": {"on": True}}, upsert=True
                ),
                message.edit("**Disabled** all chats!", del_in=5),
            )
        else:
            await message.err("Invalid flag!")
    else:
        chat = message.chat
        if message.input_str:
            try:
                chat = await message.client.get_chat(message.input_str)
            except Exception as err:
                await message.err(str(err))
                return
        if chat.id in Config.DISABLED_CHATS:
            await message.edit("This chat is already disabled!")
        elif chat.id == Config.LOG_CHANNEL_ID:
            await message.err("Can't disabled log channel")
        else:
            if chat.type == "private":
                c_name = " ".join([chat.first_name, chat.last_name or ""])
            else:
                c_name = chat.title
            Config.DISABLED_CHATS.add(chat.id)
            await asyncio.gather(
                DISABLED_CHATS.insert_one({"_id": chat.id, "title": chat.title}),
                message.edit(
                    f"CHAT : `{c_name}` added to **DISABLED_CHATS**!\n`Bot might restart, wait for some time...`",
                    del_in=5,
                    log=__name__,
                ),
            )


@userge.on_cmd("listdisabled", about={"header": "List all disabled chats."})
async def view_disabled_chats_(message: Message):
    if Config.DISABLED_ALL:
        # bot will not print this, but dont worry except log channel
        await message.edit("All chats are disabled!", del_in=5)
    elif not Config.DISABLED_CHATS:
        await message.edit("**DISABLED_CHATS** not found!", del_in=5)
    else:
        out_str = "🚷 **DISABLED_CHATS** 🚷\n\n"
        async for chat in DISABLED_CHATS.find():
            out_str += f" 👥 {chat['title']} 🆔 `{chat['_id']}`\n"
        await message.edit(out_str, del_in=0)


@userge.on_cmd(
    "sleep (\\d+)",
    about={"header": "sleep USERGE-X :P", "usage": "{tr}sleep [timeout in seconds]"},
    allow_channels=False,
)
async def sleep_(message: Message) -> None:
    """sleep USERGE-X"""
    seconds = int(message.matches[0].group(1))
    await message.edit(f"`sleeping {seconds} seconds...`")
    asyncio.get_event_loop().create_task(_slp_wrkr(seconds))


async def _slp_wrkr(seconds: int) -> None:
    await userge.stop()
    await asyncio.sleep(seconds)
    await userge.reload_plugins()
    await userge.start()


@userge.on_user_status()
async def _user_status(_, user: User) -> None:
    Config.STATUS = user.status


@userge.add_task
async def _dyno_saver_worker() -> None:
    count = 0
    check_delay = 5
    offline_start_time = time.time()
    while Config.RUN_DYNO_SAVER:
        if not count % check_delay and (
            Config.STATUS is None or Config.STATUS != "online"
        ):
            if Config.STATUS is None:
                LOG.info("< bot client found ! >")
            else:
                LOG.info("< state changed to offline ! >")
                offline_start_time = time.time()
            warned = False
            while Config.RUN_DYNO_SAVER and (
                Config.STATUS is None or Config.STATUS != "online"
            ):
                if not count % check_delay:
                    if Config.STATUS is None:
                        offline_start_time = RawClient.LAST_OUTGOING_TIME
                    current_idle_time = int((time.time() - offline_start_time))
                    if current_idle_time < 5:
                        warned = False
                    if current_idle_time >= MAX_IDLE_TIME:
                        try:
                            Config.HEROKU_APP.process_formation()["worker"].scale(0)
                        except Exception as h_e:  # pylint: disable=broad-except
                            LOG.error(f"heroku app error : {h_e}")
                            offline_start_time += 20
                            await asyncio.sleep(10)
                            continue
                        LOG.info("< successfully killed heroku dyno ! >")
                        await CHANNEL.log("heroku dyno killed !")
                        terminate()
                        return
                    prog = round(current_idle_time * 100 / MAX_IDLE_TIME, 2)
                    mins = int(MAX_IDLE_TIME / 60)
                    if prog >= 75 and not warned:
                        rem = int((100 - prog) * MAX_IDLE_TIME / 100)
                        await CHANNEL.log(
                            f"#WARNING\n\ndyno kill worker `{prog}%` completed !"
                            f"\n`{rem}`s remaining !"
                        )
                        warned = True
                    LOG.info(f"< dyno kill worker ... ({prog}%)({mins}) >")
                await asyncio.sleep(1)
                count += 1
            LOG.info("< state changed to online ! >")
        await asyncio.sleep(1)
        count += 1
    if count:
        LOG.info("< auto heroku dyno off worker has been stopped! >")
