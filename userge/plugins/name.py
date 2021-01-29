from userge import userge


class user:
    @staticmethod
    async def name_():
        u = await userge.get_me()
        return u.first_name
