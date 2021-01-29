u = await userge.get_me()


def name_(u):
    user = " ".join([u.first_name, u.last_name or ""])
    return user
