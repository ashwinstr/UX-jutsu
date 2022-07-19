import asyncio
from subprocess import call

from userge import Config, Message, userge


@userge.on_cmd(
    "uc",
    about={
        "header": "Update your config.env.",
        "description": "Upload and reply to your new config.env file to update it for currently deployed container.",
        "usage": "{tr}uc [reply to config.env file.]",
    },
)
async def config_replace(message: Message):
    reply = message.reply_to_message
    await message.edit("`Checking file...`")
    if Config.HEROKU_APP:
        await message.edit("Use `.setvar` to update Vars in Heroku app.")
    if reply and reply.document and reply.document.file_name == "config.env":
        call("rm -rf config.env", shell=True)
        await reply.download()
        await message.edit(
            "`Config.env downloaded...`,\n**Restarting to change Vars.**"
        )
        call("mv downloads/config.env .", shell=True)
        asyncio.get_event_loop().create_task(userge.restart(hard=True))
    else:
        await message.edit("`Reply to config.env -_-`", del_in=10)
