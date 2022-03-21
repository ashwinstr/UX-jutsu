import time
import re

from userge import Message, get_collection, userge, Config
from userge.utils import time_formatter

CHANNEL = userge.getCLogger(__name__)

UPDATE = get_collection("UPDATE_MSG")
RESTART_MESSAGE = get_collection("RESTART_MESSAGE")
FROZEN = get_collection("FROZEN")


async def _init() -> None:
    found = await UPDATE.find_one({"_id": "UPDATE_MSG"})
    restart = await RESTART_MESSAGE.find_one({"_id": "RESTART_MSG"})
    af_time = time.time()
    if found:
        try:
            be_update = found["time"]
            proc = found["process"]
            took_time = af_time - be_update
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
        await FROZEN.drop()
        await UPDATE.drop()
    elif restart:
        try:
            chat_ = restart["chat_id"]
            msg_ = restart["message_id"]
            text_ = restart["text"]
            text_ = text_ + f"\n<b>Time took:</b> `{af_time - st_time}`"
            cmd_ = restart["command"]
            st_time = restart["start"]
            await userge.edit_message_text(chat_id=chat_, message_id=msg_, text=text_)
        except BaseException:
            pass
        await CHANNEL.log(f"`### UX-jutsu restarted successfully. ###`\n<b>Time took:<b> `{af_time - st_time}`")
        hard_ = bool(re.search(fr"^\{Config.CMD_TRIGGER}|\{Config.SUDO_TRIGGER}restart \-h", cmd_))
        if hard_:
            await FROZEN.drop()
        await RESTART_MESSAGE.drop()
    else:
        await CHANNEL.log("`### UX-jutsu started successfully. ###`")


class Start:
    async def save_msg(message: Message, text: str) -> None:
        cmd_ = (message.text).replace(message.filtered_input_str, "").strip()
        start_time_ = time.time()
        await RESTART_MESSAGE.insert_one(
            {
                "_id": "RESTART_MSG",
                "chat_id": message.chat.id,
                "message_id": message.message_id,
                "command": cmd_,
                "text": text,
                "start": start_time_
            }
        )