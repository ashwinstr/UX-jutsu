# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

from userge import Config, Message, userge


@userge.on_cmd(
    "repo",
    about={
        "header": "get repo link and details",
        "flags": {
            "-d": " Disables Link preview ",
            "-g": "MyGpack",
        },
    },
)
async def see_repo(message: Message):
    """see repo"""
    repo_ = "[GPACK](https://github.com/ashwinstr/MyGpack)" if "-g" in message.flags else f"[UX-JUTSU]({Config.UPSTREAM_REPO})"
    output = f"• **repo** : {repo_}"
    if "-d" in message.flags:
        await message.edit(output, disable_web_page_preview=True)
    else:
        await message.edit(output)
