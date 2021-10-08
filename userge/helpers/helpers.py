from userge import userge 


async def admin_or_creator(chat_id: int, user_id: int) -> bool:
    check_status = await userge.get_chat_member(chat_id, user_id)
    admin_ = True if check_status.status == "administrator" else False
    creator_ = True if check_status.status == "creator" else False
    json_ = {is_admin: admin_, is_creator: creator_}
    return json_
