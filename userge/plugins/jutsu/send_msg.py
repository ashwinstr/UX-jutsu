
from userge import userge, Message

CHANNEL = userge.getCLogger(__name__)


@userge.on_cmd(
    "reply",
    about={
        "header": "send message with sudo",
        "usage": "{tr}reply text",
    },
)
async def send_message_and_reply(message: Message):
    """send message with sudo"""
    text_ = message.input_str
    reply_ = message.reply_to_message
    if reply_:
        reply_to = reply_.message_id
    else:
        reply_to = None
    try:
        await userge.send_message(message.chat.id, text_, reply_to_message_id=reply_to, disable_web_page_preview=True)
    except Exception as e:
        await CHANNEL.log(f"<b>ERROR:</b> {e}")