# plugin made for USERGE-X by @Kakashi_HTK(TG)/@ashwinstr(GH)


import asyncio
import os

from userge import Config, Message, get_collection, userge

FROZEN = get_collection("FROZEN")

CHANNEL = userge.getCLogger(__name__)


@userge.on_cmd(
    "freeze",
    about={
        "header": "disable plugin temporarily",
        "usage": "{tr}freeze [plugin name or command name]",
    },
)
async def freezer_(message: Message):
    """disable plugin temporarily"""
    cmd_name = message.input_str
    if not cmd_name:
        await message.edit(
            "`Provide a plugin name or command name to disable...`", del_in=5
        )
        return
    try:
        cmd_ = f"{Config.CMD_TRIGGER}{cmd_name}"
        plugin_name = userge.manager.commands[cmd_].plugin_name
    except BaseException:
        plugin_name = message.input_str
    try:
        plugin_parent = userge.manager.plugins[plugin_name].parent
        loc_ = f"userge/plugins/{plugin_parent}/{plugin_name}.py"
        old_ = loc_
        new_ = loc_.replace(".py", "")
    except Exception as e:
        await message.edit(f"Provide correct plugin name...\n\n<b>ERROR:</b> {e}")
        return
    found = await FROZEN.find_one({"plug_name": plugin_name})
    if found:
        await message.edit(
            f"The plugin <b>[{plugin_name}]</b> is already frozen.", del_in=5
        )
        return
    if os.path.exists(old_):
        os.rename(old_, new_)
        await FROZEN.insert_one({"plug_name": plugin_name, "plug_loc": new_})
        await message.edit(
            f"Plugin <b>{plugin_name}</b> got frozen temporarily.\n<b>Bot restarting...</b>"
        )
        await CHANNEL.log(
            f"Plugin <b>{plugin_name}</b> got frozen temporarily.\n<b>Bot restarting...</b>"
        )
        asyncio.get_event_loop().create_task(userge.restart())
    else:
        await message.edit(
            f"`The given plugin {plugin_name} doesn't exist...`", del_in=5
        )


@userge.on_cmd(
    "defreeze",
    about={
        "header": "re-enable frozen plugin",
        "flags": {
            "-all": "re-enable all frozen plugins",
        },
        "usage": "{tr}defreeze [plugin name]",
    },
)
async def defreezer_(message: Message):
    """re-enable frozen plugin"""
    if "-all" in message.flags:
        async for plug in FROZEN.find():
            old_ = plug["plug_loc"]
            new_ = f"{old_}.py"
            os.rename(old_, new_)
        await FROZEN.drop()
        await message.edit("All frozen plugins are <b>re-enabled</b> now...")
        await CHANNEL.log("All frozen plugins are <b>re-enabled</b>.")
        asyncio.get_event_loop().create_task(userge.restart())
        return
    plugin_name = message.input_str
    if not plugin_name:
        await message.edit("`Provide a plugin name to re-enable...`", del_in=5)
        return
    found = await FROZEN.find_one({"plug_name": plugin_name})
    if found:
        old_ = found["plug_loc"]
        new_ = f"{old_}.py"
        try:
            os.rename(old_, new_)
        except BaseException:
            await message.edit(
                f"The plugin <b>{plugin_name}</b> is already re-enabled.", del_in=5
            )
            return
        await FROZEN.delete_one(found)
        await message.edit(
            f"Plugin <b>{plugin_name}</b> got defrozen.\n<b>Bot restarting...</b>"
        )
        await CHANNEL.log(
            f"Plugin <b>{plugin_name}</b> got defrozen.\n<b>Bot restarting...</b>"
        )
        asyncio.get_event_loop().create_task(userge.restart())
    else:
        await message.edit(f"`The plugin {plugin_name} is not frozen...`", del_in=5)


@userge.on_cmd(
    "frozen",
    about={
        "header": "list frozen plugins",
        "usage": "{tr}frozen",
    },
)
async def frozen_(message: Message):
    """list frozen plugins"""
    list_ = "The list of <b>frozen</b> plugins: [{}]\n\n"
    total = 0
    async for plug in FROZEN.find():
        total += 1
        plugin = plug["plug_name"]
        list_ += f"• [{total}] `{plugin}`\n"
    if total == 0:
        await message.edit("`No plugin is frozen at the moment.`", del_in=5)
        return
    list_ = list_.format(total)
    await message.edit(list_)
