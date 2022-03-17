
from userge import userge, Message, Config, get_collection


TSUDO_LIST = get_collection("TSUDO_LIST")


async def _init() -> None:
    async for one in TSUDO_LIST.find():
        Config.TSUDO.add(one['_id'])



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
        Config.TSUDO.remove(user_)
        await TSUDO_LIST.delete_one({"_id": user_})
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
        Config.TSUDO.add(user_)
        await TSUDO_LIST.insert_one({"_id": user_})
    else:
        return await message.edit("`TSUDO for you is already enabled.`", del_in=5)