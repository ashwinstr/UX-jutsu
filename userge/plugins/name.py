async def user(message: Message):
    message.from_user


def name_(u):
    user = " ".join([u.first_name, u.last_name or ""])
    return user
