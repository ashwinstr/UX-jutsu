# tools for jutsu plugins by @Kakashi_HTK(tg)/@ashwinstr(gh)


from pyrogram.raw.functions.account import ReportPeer
from pyrogram.raw.types import (
    InputPeerUserFromMessage,
    InputReportReasonPornography,
    InputReportReasonSpam,
)


# capitalise
def capitaled(query: str):
    query_split = query.split()
    cap_text = []
    for word_ in query_split:
        word_cap = word_.capitalize()
        cap_text.append(word_cap)
    cap_query = " ".join(cap_text)
    return cap_query


# to report for spam or pornographic content
def report_user(chat: int, user_id: int, msg: dict, msg_id: int, reason: str):
    if ("nsfw" or "porn") in reason:
        reason_ = InputReportReasonPornography()
        for_ = "<b>pornographic</b> message"
    else:
        reason_ = InputReportReasonSpam()
        for_ = "<b>spam</b> message"
    peer_ = (
        InputPeerUserFromMessage(
            peer=chat,
            msg_id=msg_id,
            user_id=user_id,
        ),
    )
    ReportPeer(
        peer=peer_,
        reason=reason_,
        message=msg,
    )
    return for_
