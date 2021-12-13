

from userge import get_collection, userge

CHANNEL = userge.getCLogger(__name__)

UPDATE = get_collection("UPDATE_MSG")


async def _init() -> None:
    found = await UPDATE.find_one({"_id": "UPDATE_MSG"})
    if found:
        msg_ = found['message']
        chat_id = msg_.split("/")[0]
        msg_id = msg_.split("/")[1]
        await userge.edit_message_text(
            chat_id=int(chat_id),
            message_id=int(msg_id),
            text="### <b>UX-jutsu updated successfully.</b> ###"
        )
        await UPDATE.drop()
    else:
        await CHANNEL.log("`### UX-jutsu started successfully. ###`")