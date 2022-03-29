# new tsudo control for TRUSTED SUDO USERS

import asyncio

from pyrogram import filters

from userge import Config, Message, get_collection, userge

DISABLED_TSUDO = get_collection("DISABLED_TSUDO")
TRUSTED_SUDO_USERS = get_collection("TRUSTED_SUDO_USERS")


async def _init() -> None:
    async for one in DISABLED_TSUDO.find():
        Config.DISABLED_TSUDO.add(one["_id"])



@userge.on_cmd(
    "tsudo",
    about={"header": "check tsudo status", "usage": "{tr}tsudo"},
)
async def tsudo_check(message: Message):
    user_ = message.from_user.id
    if user_ in Config.DISABLED_TSUDO:
        await message.edit("`Your TSUDO is OFF.`", del_in=5)
    else:
        await message.edit("`Your TSUDO is ON.`", del_in=5)


@userge.on_cmd(
    "distsudo",
    about={
        "header": "disable tsudo temporarily",
        "usage": "{tr}distsudo",
    },
)
async def dis_tsudo(message: Message):
    "disable tsudo temporarily"
    user_ = message.from_user.id
    if user_ in Config.OWNER_ID:
        return
    user = await userge.get_user(user_)
    if user_ in Config.TRUSTED_SUDO_USERS and user_ not in Config.DISABLED_TSUDO:
        Config.TRUSTED_SUDO_USERS.remove(user_)
        Config.DISABLED_TSUDO.add(user_)
        await asyncio.gather(
            TRUSTED_SUDO_USERS.delete_one({"_id": user_}),
            DISABLED_TSUDO.insert_one({"_id": user_, "men": user.mention}),
            message.edit("`TSUDO disabled for you...`", del_in=5)
        )
    elif user_ not in Config.TRUSTED_SUDO_USERS and user_ in Config.DISABLED_TSUDO:
        await message.edit("`TSUDO for you is already DISABLED temporarily.`", del_in=5)
    else:
        await message.edit("`You're not eligible for this command.`", del_in=5)


@userge.on_message(
    filters.command("ensudo", prefixes=Config.SUDO_TRIGGER)
    & Config.DISABLED_TSUDO
    & ~filters.bot,
    group=-1
)
async def en_tsudo(message: Message):
    "enable tsudo"
    user_ = message.from_user.id
    if user_ in Config.OWNER_ID:
        return
    if user_ in Config.DISABLED_TSUDO and user_ not in Config.TRUSTED_SUDO_USERS:
        Config.DISABLED_TSUDO.remove(user_)
        Config.TRUSTED_SUDO_USERS.add(user_)
        await asyncio.gather(
            DISABLED_TSUDO.delete_one({"_id": user_}),
            TRUSTED_SUDO_USERS.insert_one({"_id": user_}),
            message.edit("`TSUDO enabled for you...`")
        )
    elif user_ not in Config.DISABLED_TSUDO and user_ in Config.TRUSTED_SUDO_USERS:
        await message.edit("`TSUDO for you is already ENABLED.`", del_in=5)
    else:
        await message.edit("`You're not eligible for this command.`", del_in=5)