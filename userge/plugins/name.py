from userge import Message


async def user(message: Message):
    u = message.from_user


def name_(u):
    user = " ".join([u.first_name, u.last_name or ""])
    return user
