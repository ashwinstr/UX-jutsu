from userge import message


def name_():
    u = message.from_user
    user = " ".join([u.first_name, u.last_name or ""])
    return user
