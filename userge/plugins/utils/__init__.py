# testing by @Kakashi_HTK/@ashwinstr


import aiofiles
import ujson
from userge import userge

def __init__() -> None:
  json_data = await userge.get_me()
  async with aiofiles.open("userge/xcache/get_me.json", "w+") as fn:
    fn.write(json_data)
