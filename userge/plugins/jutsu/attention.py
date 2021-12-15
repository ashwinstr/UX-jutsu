import os
import traceback

import ujson
from pyrogram import filters
from pyrogram.errors import MessageNotModified
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from userge import Config, get_collection, userge

SEEN_BY = get_collection("SEEN_BY")


async def _init() -> None:
    attention = os.path.join(Config.CACHE_PATH, "notice.json")
    found = await SEEN_BY.find_one({"_id": "ATTENTION"})
    if found:
        notice_data = {
            found["_id"]: {
                "sender": found["sender"],
                "notice": found["notice"],
                "seen": found["seen"],
                "user_first_names": found["user_first_names"],
            }
        }
    else:
        return
    with open(attention, "w") as r:
        ujson.dump(notice_data, r, indent=4)


@userge.bot.on_callback_query(filters.regex(pattern=r"^notice.*"))
async def notice_(_, c_q: CallbackQuery):
    try:
        query_ = c_q.data
        split_ = query_.split("_", 1)
        id_ = split_[-1]
        notice_path = "userge/xcache/notice.json"
        if not os.path.exists(notice_path):
            await c_q.answer("This message doesn't exist anymore", show_alert=True)
            return
        with open(notice_path) as f:
            n_data = ujson.load(f)
            view_data = n_data.get(id_)
        user_ = c_q.from_user.id
        found = await SEEN_BY.find_one({"_id": id_})
        if "seen" not in c_q.data:
            try:
                users_ = found["seen"]
                seen_by = found["user_first_names"]
            except BaseException:
                users_ = []
                seen_by = []
            if user_ in users_:
                pass
            else:
                users_.append(user_)
                seen_by.append((await userge.get_users(user_)).first_name)
            await SEEN_BY.update_one(
                {"_id": id_}, {"$set": {"seen": users_}}, upsert=True
            )
            await SEEN_BY.update_one(
                {"_id": id_}, {"$set": {"user_first_names": seen_by}}, upsert=True
            )
            await c_q.answer(view_data["notice"], show_alert=True)
            btn_ = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="What is it!!?", callback_data=f"notice_{id_}"
                        ),
                        InlineKeyboardButton(
                            text="Seen by.", callback_data=f"noticeseen_{id_}"
                        ),
                    ],
                ]
            )
            try:
                await c_q.edit_message_text(
                    f"**Attention everyone!!!**\n👁‍🗨 **Seen by:** {len(users_)} people.",
                    reply_markup=btn_,
                )
            except MessageNotModified:
                pass
        else:
            if user_ not in Config.OWNER_ID and user_ not in Config.TRUSTED_SUDO_USERS:
                await c_q.answer(
                    "Only owner or trusted sudo users can see this list.",
                    show_alert=True,
                )
            else:
                users_ = found["seen"]
                seen_by = found["user_first_names"]
                list_ = f"Notice seen by: [{len(users_)}]\n\n"
                for one in seen_by:
                    list_ += f"• {one}\n"
                await c_q.answer(list_, show_alert=True)
    except BaseException:
        tb = traceback.format_exc()
        await userge.send_message(Config.LOG_CHANNEL_ID, f"#ATTENTION\n\n```{tb}```")
