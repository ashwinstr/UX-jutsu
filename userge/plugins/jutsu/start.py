

from userge import userge

CHANNEL = userge.getCLogger(__name__)


async def _init() -> None:
    await CHANNEL.log("`### BOT restarted successfully ###`")