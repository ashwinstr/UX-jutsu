""" setup AFK mode """

import asyncio
import time
from random import choice, randint

from userge import Config, Message, filters, get_collection, userge
from userge.utils import time_formatter

CHANNEL = userge.getCLogger(__name__)
SAVED_SETTINGS = get_collection("CONFIGS")
AFK_COLLECTION = get_collection("AFK")

IS_AFK = False
IS_AFK_FILTER = filters.create(lambda _, __, ___: bool(IS_AFK))
REASON = ""
TIME = 0.0
USERS = {}


async def _init() -> None:
    global IS_AFK, REASON, TIME  # pylint: disable=global-statement
    data = await SAVED_SETTINGS.find_one({"_id": "AFK"})
    if data:
        IS_AFK = data["on"]
        REASON = data["data"]
        TIME = data["time"] if "time" in data else 0
    async for _user in AFK_COLLECTION.find():
        USERS.update({_user["_id"]: [_user["pcount"], _user["gcount"], _user["men"]]})


@userge.on_cmd(
    "afk",
    about={
        "header": "Set to AFK mode",
        "description": "Sets your status as AFK. Responds to anyone who tags/PM's.\n"
        "you telling you are AFK. Switches off AFK when you type back anything.",
        "usage": "{tr}afk or {tr}afk [reason]",
    },
    allow_channels=False,
)
async def active_afk(message: Message) -> None:
    """ turn on or off afk mode """
    global REASON, IS_AFK, TIME  # pylint: disable=global-statement
    IS_AFK = True
    TIME = time.time()
    REASON = message.input_str
    await asyncio.gather(
        CHANNEL.log(f"You went AFK! : `{REASON}`"),
        message.edit("`You went AFK!`", del_in=1),
        AFK_COLLECTION.drop(),
        SAVED_SETTINGS.update_one(
            {"_id": "AFK"},
            {"$set": {"on": True, "data": REASON, "time": TIME}},
            upsert=True,
        ),
    )


@userge.on_filters(
    IS_AFK_FILTER
    & ~filters.me
    & ~filters.bot
    & ~filters.user(Config.TG_IDS)
    & ~filters.edited
    & (
        filters.mentioned
        | (
            filters.private
            & ~filters.service
            & (
                filters.create(lambda _, __, ___: Config.ALLOW_ALL_PMS)
                | Config.ALLOWED_CHATS
            )
        )
    ),
    allow_via_bot=False,
)
async def handle_afk_incomming(message: Message) -> None:
    """ handle incomming messages when you afk """
    if not message.from_user:
        return
    user_id = message.from_user.id
    chat = message.chat
    user_dict = await message.client.get_user_dict(user_id)
    afk_time = time_formatter(round(time.time() - TIME))
    coro_list = []
    if user_id in USERS:
        if not (USERS[user_id][0] + USERS[user_id][1]) % randint(2, 4):
            if REASON:
                out_str = (
                    f"I'm still **AFK**.\nReason: <code>{REASON}</code>\n"
                    f"Last Seen: `{afk_time} ago`"
                )
            else:
                out_str = choice(AFK_REASONS)
            coro_list.append(message.reply(out_str))
        if chat.type == "private":
            USERS[user_id][0] += 1
        else:
            USERS[user_id][1] += 1
    else:
        if REASON:
            out_str = (
                f"I'm **AFK** right now.\nReason: <code>{REASON}</code>\n"
                f"Last Seen: `{afk_time} ago`"
            )
        else:
            out_str = choice(AFK_REASONS)
        coro_list.append(message.reply(out_str))
        if chat.type == "private":
            USERS[user_id] = [1, 0, user_dict["mention"]]
        else:
            USERS[user_id] = [0, 1, user_dict["mention"]]
    if chat.type == "private":
        coro_list.append(
            CHANNEL.log(
                f"#PRIVATE\n{user_dict['mention']} send you\n\n" f"{message.text}"
            )
        )
    else:
        coro_list.append(
            CHANNEL.log(
                "#GROUP\n"
                f"{user_dict['mention']} tagged you in [{chat.title}](http://t.me/{chat.username})\n\n"
                f"{message.text}\n\n"
                f"[goto_msg](https://t.me/c/{str(chat.id)[4:]}/{message.message_id})"
            )
        )
    coro_list.append(
        AFK_COLLECTION.update_one(
            {"_id": user_id},
            {
                "$set": {
                    "pcount": USERS[user_id][0],
                    "gcount": USERS[user_id][1],
                    "men": USERS[user_id][2],
                }
            },
            upsert=True,
        )
    )
    await asyncio.gather(*coro_list)


@userge.on_filters(IS_AFK_FILTER & filters.outgoing, group=-1, allow_via_bot=False)
async def handle_afk_outgoing(message: Message) -> None:
    """ handle outgoing messages when you afk """
    global IS_AFK  # pylint: disable=global-statement
    IS_AFK = False
    afk_time = time_formatter(round(time.time() - TIME))
    replied: Message = await message.reply("`I'm no longer AFK!`", log=__name__)
    coro_list = []
    if USERS:
        p_msg = ""
        g_msg = ""
        p_count = 0
        g_count = 0
        for pcount, gcount, men in USERS.values():
            if pcount:
                p_msg += f"👤 {men} ✉️ **{pcount}**\n"
                p_count += pcount
            if gcount:
                g_msg += f"👥 {men} ✉️ **{gcount}**\n"
                g_count += gcount
        coro_list.append(
            replied.edit(
                f"`You recieved {p_count + g_count} messages while you were away. "
                f"Check log for more details.`\n\n**AFK time** : __{afk_time}__",
                del_in=3,
            )
        )
        out_str = (
            f"You've recieved **{p_count + g_count}** messages "
            + f"from **{len(USERS)}** users while you were away!\n\n**AFK time** : __{afk_time}__\n"
        )
        if p_count:
            out_str += f"\n**{p_count} Private Messages:**\n\n{p_msg}"
        if g_count:
            out_str += f"\n**{g_count} Group Messages:**\n\n{g_msg}"
        coro_list.append(CHANNEL.log(out_str))
        USERS.clear()
    else:
        await asyncio.sleep(3)
        coro_list.append(replied.delete())
    coro_list.append(
        asyncio.gather(
            AFK_COLLECTION.drop(),
            SAVED_SETTINGS.update_one(
                {"_id": "AFK"}, {"$set": {"on": False}}, upsert=True
            ),
        )
    )
    await asyncio.gather(*coro_list)


AFK_REASONS = (
    "I'm Busy Right Now. Please Talk In A Fuckin' Bag And When I Come Back You Can Just Give Me The Bag!",
    "I'm Away Right Now. If You Need Anything, Leave A Message After The Beep: \
`BeeeeeeeeeeeeeeeeFuuuuuckkkkkkeeeeeeeeeeeeeeeeep!`",
    "You Missed Me, Next Time Aim Fuckin Better.",
    "I'll Be Back In A Few Minutes And If I'm Not...,\nWait Longer Or Die Bish! BEZZ+.",
    "I'm Not Here Fuckin Right Now, So I'm Probably Somewhere Else In A Hell!.",
    "Roses Are Red,\nViolets Are Blue,\nLeave Me A Fuckin' Message,\nand I'll Get Back To You!.",
    "Sometimes The Best Fuckin Things In Life Are Worth Waiting For…\nI'll Be Fucking Right Back!.",
    "I'll Be Right Back,:\nBut If I'm Not Fuckin Right Back,\nI'll Be Back Whenever The Fuck I Want! 😎.",
    "If You Haven't Figured It Out Already,\nI'm Not Here.",
    "I'm Away Over 7 Seas And 7 Countries,\n7 Waters And 7 Continents,\n7 Mountains And 7 Hill's,\
7 Plains And 7 Mounds,\n7 Pools And 7 Lakes,\n7 Springs And 7 Meadows,\
7 Cities And 7 Neighborhoods,\n7 Blocks And 7 Houses...\
    Where Not Even Your Fuckin Messages Can Reach Me!",
    "I'm Fucking Away From The Fuckin Keyboard At The Fucking Moment, But If You'll Fucking screammmmm LoudASF! Enough At Your Fuckin Shieety Screen,\
    I Might Just Fuckin' Hear You!.",
    "I Went That Fuckin' Way\n>>>>>",
    "I Went This Fuckin' Way\n<<<<<",
    "Please Leave A Fuckin'Sheeity Message And Make Me Feel Even More Important Than I Already Fuckin'EM!.",
    "If I Were Here,\nI'd Tell You Where I Am.\n\nBut I'm Not,\nSo Ask Me When I Fuckin' Returned...",
    "I Am Away!\nI Don't Know when I'll Be Back!\nHopefully A few Minutes From Now!",
    "I'm Not Available Fuckin' Right Now So Please Leave Your Fuckin' Name, Number, \
    And Address And I Will Stalk You Later. :P",
    "Sorry, I'm Not Here Right Now.\nFeel Free To Talk To My HyperUserge-UX As Long As You Like.\
I'll Get Back To You Later.",
    "I Bet You Were Expecting An Fuckin'Shieeety Away Message!",
    "Life Is So Short, There Are So Many Things To Do...\nI'm Away Doing One Of Them..",
    "I Am Not Here Fuckin' Right Now...\nBut If I Was...\n\nWouldn't That Be Awesome?",
)
