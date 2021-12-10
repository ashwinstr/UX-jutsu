import traceback

from pyrogram import filters
from pyrogram.types import CallbackQuery

from userge import userge, get_collection, Config

SEEN_BY = get_collection("SEEN_BY")


@userge.on_callback_query(
    filters.regex(r"^attention.*")
)
async def notice_(_, c_q: CallbackQuery):
    try:
        query_ = c_q.data
        split_ = query_.split("_", 2)
        id_ = split_[-2]
        notice = split_[-1]
        found = await SEEN_BY.find_one({"_id": id_})
        user_ = c_q.from_user.id
        if not found:
            await SEEN_BY.insert_one(
                {
                    "_id": id_,
                    "seen": [],
                    "notice": notice,
                    "user_first_names": [],
                }
            )
        found = await SEEN_BY.find_one({"_id": id_})
        if "seen" not in c_q.data:
            users_ = found['seen']
            seen_by = found['user_first_names']
            if user_ in users_:
                pass
            else:
                users_.append(user_)
                seen_by.append((await userge.get_users(user_)).first_name)
            await c_q.answer(notice, show_alert=True)
        else:
            if user_ not in Config.OWNER_ID and user_ not in Config.TRUSTED_SUDO_USERS:
                await c_q.answer("Only owner or trusted sudo users can see this list.", show_alert=True)
            else:
                users_ = found['seen']
                seen_by = found['user_first_names']
                list_ = f"Notice seen by: [{len(users_)}]\n\n"
                for one in seen_by:
                    list_ += f"• {one}\n"
                await c_q.answer(list_, show_alert=True)
    except:
        tb = traceback.format_exc()
        await userge.send_message(Config.LOG_CHANNEL_ID, f"#ATTENTION\n\n```{tb}```")