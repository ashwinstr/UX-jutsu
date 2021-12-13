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
            be_update = found["time"]
            took_time = af_update - be_update
            took_time = time_formatter(took_time)
            msg_ = found["message"]
            chat_id = msg_.split("/")[0]
            msg_id = msg_.split("/")[1]
            await userge.edit_message_text(
                chat_id=int(chat_id),
                message_id=int(msg_id),
                text=f"### <b>UX-jutsu updated successfully.</b> ###\nUpdate time - <b>{took_time}</b>",
            )
            await CHANNEL.log(f"Update time - <b>{took_time}</b>")
        except BaseException:
            await CHANNEL.log("`### UX-jutsu started successfully. ###`")
        await UPDATE.drop()
    else:
        await CHANNEL.log("`### UX-jutsu started successfully. ###`")
