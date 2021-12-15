import time

from userge import get_collection, userge
from userge.utils import time_formatter

CHANNEL = userge.getCLogger(__name__)

UPDATE = get_collection("UPDATE_MSG")


async def _init() -> None:
    found = await UPDATE.find_one({"_id": "UPDATE_MSG"})
    if found:
        try:
            af_update = time.time()
            be_update = found['time']
            proc = found['process']
            took_time = af_update - be_update
            took_time = time_formatter(took_time)
            msg_ = found["message"]
            chat_id = msg_.split("/")[0]
            msg_id = msg_.split("/")[1]
            await userge.edit_message_text(
                chat_id=int(chat_id),
                message_id=int(msg_id),
                text=f"### <b>UX-jutsu {proc} successfully.</b> ###\nProcess time - <b>{took_time}</b>"
            )
            await CHANNEL.log(f"Update/restart time - <b>{took_time}</b>")
        except:
            await CHANNEL.log(f"`### UX-jutsu updated/restarted successfully. ###`")
        await UPDATE.drop()
    else:
        await CHANNEL.log("`### UX-jutsu started successfully. ###`")
