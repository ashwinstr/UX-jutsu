### Made by Ryuk ###

import os

from userge import Config, Message, get_collection, userge

SAVED_SETTINGS = get_collection("CONFIGS")


async def _init() -> None:
    found = await SAVED_SETTINGS.find_one({"_id": "REVEAL_VAR"})
    if found:
        Config.REVEAL_VAR = found["switch"]
    else:
        Config.REVEAL_VAR = False


@userge.on_cmd(
    "reveal_vars",
    about={
        "header": "enable fetching secured vars",
        "flags": {
            "-c": "check",
        },
        "usage": "{tr}reveal_vars",
    },
)
async def reveal_var(message: Message):
    if "-c" in message.flags:
        out_ = "ON" if Config.REVEAL_VAR else "OFF"
        return await message.edit(f"`Secure Vars : {out_}.`", del_in=5)
    if Config.REVEAL_VAR:
        Config.REVEAL_VAR = False
        await SAVED_SETTINGS.update_one(
            {"_id": "REVEAL_VAR"}, {"$set": {"switch": False}}, upsert=True
        )
    else:
        Config.REVEAL_VAR = True
        await SAVED_SETTINGS.update_one(
            {"_id": "REVEAL_VAR"}, {"$set": {"switch": True}}, upsert=True
        )
    out_ = "ON" if Config.REVEAL_VAR else "OFF"
    await message.edit(f"`Secured Vars : {out_}.`")


@userge.on_cmd(
    "rvar",
    about={
        "header": "view vars",
        "usage": "{tr}rvar OWNER_ID ",
    },
)
async def view_var(message: Message):
    vname = message.input_str
    if not vname:
        await message.edit("Give a var name to vview", del_in=5)
        return
    input_name = (vname.strip()).upper()
    var = os.environ.get(input_name)
    await message.edit(var)
