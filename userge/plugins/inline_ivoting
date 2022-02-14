
import re

from pyrogram.types import (
    InlineQuery,
    InlineQueryResultPhoto,
    InlineQueryResultArticle,
    InputTextMessageContent,
)

from userge import userge, Config
from .jutsu.ivotings import vote_buttons

@userge.bot.on_inline_query()
async def alive_inline_q(_, inline_query: InlineQuery):
    results = []
    i_q = inline_query.query
    str_y = i_q.split(" ", 1)
    iq_user_id = inline_query.from_user.id
    if (
        (iq_user_id in Config.OWNER_ID)
        or (
            iq_user_id in Config.SUDO_USERS
            or iq_user_id in Config.TRUSTED_SUDO_USERS
        )
        and Config.SUDO_ENABLED
    ):
        if str_y[0] == "voting" and len(str_y) == 2:
            id_ = userge.rnd_id()
            up = 0
            down = 0
            anon = False
            tele_ = bool(
                re.search(
                    r"http[s]?\:\/\/telegra\.ph\/file\/.*\.(gif|jpg|png|jpeg)$",
                    str_y[1],
                )
            )
            if tele_:
                results.append(
                    InlineQueryResultPhoto(
                        photo_url=str_y[1],
                        title="Vote.",
                        description="Vote your opinion.",
                        caption="Vote your opinion.",
                        reply_markup=vote_buttons(up, down, anon, id_),
                    )
                )
            else:
                results.append(
                    InlineQueryResultArticle(
                        title="Vote.",
                        input_message_content=InputTextMessageContent(str_y[1]),
                        description="Vote your opinion.",
                        reply_markup=vote_buttons(up, down, anon, id_),
                    )
                )

        if str_y[0] == "anon_vote" and len(str_y) == 2:
            id_ = userge.rnd_id()
            up = 0
            down = 0
            anon = True
            tele_ = bool(
                re.search(
                    r"http[s]?\:\/\/telegra\.ph\/file\/.*\.(gif|jpg|png|jpeg)$",
                    str_y[1],
                )
            )
            if tele_:
                results.append(
                    InlineQueryResultPhoto(
                        photo_url=str_y[1],
                        title="Vote.",
                        description="Vote your opinion.",
                        caption="Vote your opinion.",
                        reply_markup=vote_buttons(up, down, anon, id_),
                    )
                )
            else:
                results.append(
                    InlineQueryResultArticle(
                        title="Vote.",
                        input_message_content=InputTextMessageContent(str_y[1]),
                        description="Vote your opinion.",
                        reply_markup=vote_buttons(up, down, anon, id_),
                    )
                )
