# this plugin is made for USERGE-X by @Kakashi_HTK(tg)/@ashwinstr(gh)


import re

from userge import Config

regex_stop = r"(addsudo)|(delsudo)|(addscmd).*"


def forbidden_sudo(msg, cmd: str) -> bool:
    if msg.from_user.id not in Config.SUDO_USERS:
        return False
    return bool(
        re.search(
            fr"^(\{Config.CMD_TRIGGER})|(\{Config.SUDO_TRIGGER})\{regex_stop}", cmd
        )
    )
