from userge import userge


class username:
    @staticmethod
    async def name_():
        u = await userge.get_me()
        user = " ".join([u.first_name, u.last_name or ""])
        return user
