
from pyrogram.raw.types import UpdatePeerBlocked

from userge import userge

CHANNEL = userge.getCLogger(__name__)


@userge.on_raw_update()
async def checking_status(_, peer_block: UpdatePeerBlocked):
    await CHANNEL.log(peer_block)
