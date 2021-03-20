# testing by @Kakashi_HTK/@ashwinstr


import aiofiles
import ujson

from userge import userge


async def swim():
    async with aiofiles.open("userge/xcache/get_me.json", "w+") as fn:
        json_data = await userge.get_me()
        await fn.write(json_data)


await swim()
