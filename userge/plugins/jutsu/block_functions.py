from userge import Message, get_collection

BLOCKED = get_collection("BLOCKED")


async def text_(_, __, message: Message) -> bool:
    found = await BLOCKED.find_one({"chat_id": message.chat.id})
    if found:
        return any(one in message.text for one in found['blocked']['text'])


async def audio_(_, __, message: Message) -> bool:
    found = await BLOCKED.find_one({"chat_id": message.chat.id})
    if found:
        return found["blocked"]["audio"]


async def video_(_, __, message: Message) -> bool:
    found = await BLOCKED.find_one({"chat_id": message.chat.id})
    if found:
        return found["blocked"]["video"]


async def photo_(_, __, message: Message) -> bool:
    found = await BLOCKED.find_one({"chat_id": message.chat.id})
    if found:
        return found["blocked"]["photo"]


async def document_(_, __, message: Message) -> bool:
    found = await BLOCKED.find_one({"chat_id": message.chat.id})
    if found:
        return found["blocked"]["document"]


async def animation_(_, __, message: Message) -> bool:
    found = await BLOCKED.find_one({"chat_id": message.chat.id})
    if found:
        return found["blocked"]["animation"]


async def sticker_(_, __, message: Message) -> bool:
    found = await BLOCKED.find_one({"chat_id": message.chat.id})
    if found:
        return found["blocked"]["sticker"]


async def voice_(_, __, message: Message) -> bool:
    found = await BLOCKED.find_one({"chat_id": message.chat.id})
    if found:
        return found["blocked"]["voice"]


async def video_note_(_, __, message: Message) -> bool:
    found = await BLOCKED.find_one({"chat_id": message.chat.id})
    if found:
        return found["blocked"]["video_note"]


async def media_(_, __, message: Message) -> bool:
    found = await BLOCKED.find_one({"chat_id": message.chat.id})
    if found:
        return found["blocked"]["media"]
