from cgitb import text
import time

from userge import get_collection, userge, Message
from userge.utils import time_formatter

CHANNEL = userge.getCLogger(__name__)

UPDATE = get_collection("UPDATE_MSG")
RESTART_MESSAGE = get_collection("RESTART_MESSAGE")


async def _init() -> None:
    found = await UPDATE.find_one({"_id": "UPDATE_MSG"})
    restart = await RESTART_MESSAGE.find_one({"_id": "RESTART_MSG"})
    if found:
        try:
            af_update = time.time()
            be_update = found["time"]
            proc = found["process"]
            took_time = af_update - be_update
            took_time = time_formatter(took_time)
            msg_ = found["message"]
            chat_id = msg_.split("/")[0]
            msg_id = msg_.split("/")[1]
            await userge.edit_message_text(
                chat_id=int(chat_id),
                message_id=int(msg_id),
                text=f"### <b>UX-jutsu {proc} successfully.</b> ###\nProcess time - <b>{took_time}</b>",
            )
            await CHANNEL.log(f"Update/restart time - <b>{took_time}</b>")
        except BaseException:
            await CHANNEL.log(f"`### UX-jutsu updated/restarted successfully. ###`")
        await UPDATE.drop()
    elif restart:
        try:
            chat_ = restart['chat_id']
            msg_ = restart['message_id']
            text_ = restart['text']
            await userge.edit_message_text(
                chat_id=chat_,
                message_id=msg_,
                text=text_
            )
        except:
            pass
        await CHANNEL.log("`### UX-jutsu restarted successfully. ###`")
        await RESTART_MESSAGE.drop()
    else:
        await CHANNEL.log("`### UX-jutsu started successfully. ###`")



class Start:
    async def save_msg(message: Message, text: str) -> None:
        await RESTART_MESSAGE.insert_one(
            {
                "_id": "RESTART_MSG",
                "chat_id": message.chat.id,
                "message_id": message.message_id,
                "text": text
            }
        )

