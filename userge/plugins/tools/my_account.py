# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

from userge import Message, userge


@userge.on_cmd(
    "ac",
    about={
        "header": "displays which account you're using right now.",
        "usage": "{tr}ac",
    },
)
async def accunt(message: Message):
    msg = message.from_user
    name = " ".join([msg.first_name, msg.last_name or ""])
    out_str = f"👤 **Account** : `{name}`\n"
    out_str += f"#⃣ **Account ID** : `{msg.id}`\n"
    await message.edit(out_str, del_in=5)
