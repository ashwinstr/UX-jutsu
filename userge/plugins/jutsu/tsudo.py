
from userge import userge, Message, Config, get_collection


TSUDO_LIST = get_collection("TSUDO_LIST")


async def _init() -> None:
    found = False
    async for one in TSUDO_LIST.find():
        Config.TSUDO = one['users']
        found = True
    if not found:
        for one in Config.TRUSTED_SUDO_USERS:
            Config.TSUDO.add(one)


@userge.on_cmd(
    "distsudo",
    about={
        "header": "disable tsudo temporarily",
        "usage": "{tr}distsudo",
    },
)
async def dis_tsudo(message: Message):
    " disable tsudo temporarily "
    user_ = message.from_user.id
    if user_ in Config.OWNER_ID:
        return
    if user_  in Config.TSUDO:
        found = await TSUDO_LIST.find_one({"_id": "TSUDO_USERS"})
        if found:
            users = found['users']
            users.remove(user_)
            await TSUDO_LIST.update_one(
                {"_id": "TSUDO_USERS"},
                {"$set": {"users": users}},
                upsert=True
            )
            Config.TSUDO.remove(user_)
    else:
        return await message.edit("`TSUDO for you is already disabled temporarily.`", del_in=5)


@userge.on_cmd(
    "entsudo",
    about={
        "header": "enable tsudo",
        "usage": "{tr}entsudo",
    },
)
async def dis_tsudo(message: Message):
    " disable tsudo temporarily "
    user_ = message.from_user.id
    if user_ in Config.OWNER_ID:
        return
    if user_  not in Config.TSUDO:
        found = await TSUDO_LIST.find_one({"_id": "TSUDO_USERS"})
        if found:
            users = found['users']
            users.append(user_)
            await TSUDO_LIST.update_one(
                {"_id": "TSUDO_USERS"},
                {"$set": {"users": users}},
                upsert=True
            )
            Config.TSUDO.append(user_)
    else:
        return await message.edit("`TSUDO for you is already enabled.`", del_in=5)