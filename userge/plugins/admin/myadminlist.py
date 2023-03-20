"""Get Your Admin Groups and Channels"""

# For USERGE-X
# Idea : https://github.com/kantek/.../kantek/plugins/private/stats.py
# Module By: github/code-rgb [TG - @DeletedUser420]
# Modded to Admin only By: Ryuk (anonymousx97)

import asyncio

from pyrogram.errors import FloodWait, UserNotParticipant

from userge import Message, userge
from userge.utils import post_to_telegraph as pt


@userge.on_cmd(
    "myadminlist",
    about={"header": "List your Admin groups/channels.", "usage": "{tr}myadminlist"},
)
async def get_your_admin_list(message: Message):
    """get info about your Admin group/channels"""

    await message.edit(
        "💁‍♂️ `Collecting your Telegram Stats ...`\n"
        "<b>Please wait it will take some time</b>"
    )
    owner = await userge.get_me()
    groups_admin = []
    groups_creator = []
    channels_admin = []
    channels_creator = []
    try:
        async for dialog in userge.iter_dialogs():
            chat_type = dialog.chat.type
            if chat_type not in ["bot", "private"]:
                try:
                    is_admin = await admin_check(dialog.chat.id, owner.id)
                    is_creator = dialog.chat.is_creator
                except UserNotParticipant:
                    is_admin = False
                    is_creator = False
                if chat_type in ["group", "supergroup"]:
                    if is_admin:
                        groups_admin.append(dialog.chat.title)
                    if is_creator:
                        groups_creator.append(dialog.chat.title)
                else:  # Channel
                    if is_admin:
                        channels_admin.append(dialog.chat.title)
                    if is_creator:
                        channels_creator.append(dialog.chat.title)
    except FloodWait as e:
        await asyncio.sleep(e.x + 5)
    template = f"""Admin Groups/Channels of {owner.first_name}"""
    text_ = ""
    if channels_creator or groups_creator:
        if groups_creator:
            text_ += f"""\n<h3>Owner of Groups:</h3>\n• """ + "\n• ".join(
                sorted(groups_creator)
            )
        if channels_creator:
            text_ += f"""\n\n\n<h3>Owner of Channels:</h3>\n• """ + "\n• ".join(
                sorted(channels_creator)
            )
    if groups_admin:
        text_ += f"""\n\n\n<h3>Admin in Groups:</h3>\n• """ + "\n• ".join(
            sorted(groups_admin)
        )
    if channels_admin:
        text_ += f"""\n\n\n<h3>Admin in Channels:</h3>\n• """ + "\n• ".join(
            sorted(channels_admin)
        )
    telegraph = pt(template.replace("\n", "<br>"), text_.replace("\n", "<br>"))
    await message.edit(
        f"{template} : \n[📜 TELEGRAPH]({telegraph})", disable_web_page_preview=True
    )


#  https://git.colinshark.de/PyroBot/PyroBot/src/branch
#  /master/pyrobot/modules/admin.py#L69
async def admin_check(chat_id: int, user_id: int) -> bool:
    check_status = await userge.get_chat_member(chat_id, user_id)
    admin_strings = ["creator", "administrator"]
    return check_status.status in admin_strings
