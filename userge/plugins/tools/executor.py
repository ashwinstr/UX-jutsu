""" run shell or python command(s) """

# Copyright (C) 2020-2021 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved.

import asyncio
import io
import keyword
import sys
import traceback
from getpass import getuser
from os import geteuid

from userge import Config, Message, userge
from userge.utils import runcmd

CHANNEL = userge.getCLogger()


@userge.on_cmd(
    "eval",
    about={
        "header": "run python code line | lines",
        "flags": {"-s": "silent mode (hide STDIN)"},
        "usage": "{tr}eval [flag] [code lines]",
        "examples": [
            "{tr}eval print('USERGE-X')",
            "{tr}eval -s print('USERGE-X')",
            "{tr}eval 5 + 6",
            "{tr}eval -s 5 + 6",
        ],
    },
    allow_channels=False,
)
async def eval_(message: Message):
    """run python code"""
    cmd = await init_func(message)
    if cmd is None:
        return
    silent_mode = False
    if cmd.startswith("-s"):
        silent_mode = True
        cmd = cmd[2:].strip()
    if not cmd:
        await message.err("Unable to Parse Input!")
        return
    await message.edit("`Executing eval ...`", parse_mode="md")
    old_stderr = sys.stderr
    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()
    redirected_error = sys.stderr = io.StringIO()
    ret_val, stdout, stderr, exc = None, None, None, None

    async def aexec(code):
        head = "async def __aexec(userge, message):\n "
        if "\n" in code:
            rest_code = "\n ".join(iter(code.split("\n")))
        elif (
            any(
                True
                for k_ in keyword.kwlist
                if k_ not in ("True", "False", "None") and code.startswith(f"{k_} ")
            )
            or "=" in code
        ):
            rest_code = f"\n {code}"
        else:
            rest_code = f"\n return {code}"
        exec(head + rest_code)  # nosec pylint: disable=W0122
        return await locals()["__aexec"](userge, message)

    try:
        ret_val = await aexec(cmd)
    except Exception:  # pylint: disable=broad-except
        exc = traceback.format_exc().strip()
    stdout = redirected_output.getvalue().strip()
    stderr = redirected_error.getvalue().strip()
    sys.stdout = old_stdout
    sys.stderr = old_stderr
    evaluation = exc or stderr or stdout or ret_val
    output = ""
    if not silent_mode:
        output += f"**>** ```{cmd}```\n\n"
    if evaluation is not None:
        output += f"**>>** ```{evaluation}```"
    if (exc or stderr) and message.chat.type in ("group", "supergroup", "channel"):
        msg_id = await CHANNEL.log(output)
        await message.edit(f"**Logs**: {CHANNEL.get_link(msg_id)}")
    elif output:
        await message.edit_or_send_as_file(
            text=output, parse_mode="md", filename="eval.txt", caption=cmd
        )
    else:
        await message.delete()


@userge.on_cmd(
    "exec",
    about={
        "header": "run commands in exec",
        "usage": "{tr}exec [commands]",
        "examples": '{tr}exec echo "USERGE-X"',
    },
    allow_channels=False,
)
async def exec_(message: Message):
    """run commands in exec"""
    cmd = await init_func(message)
    if cmd is None:
        return
    await message.edit("`Executing exec ...`")
    try:
        out, err, ret, pid = await runcmd(cmd)
    except Exception as t_e:  # pylint: disable=broad-except
        await message.err(str(t_e))
        return
    out = out or "no output"
    err = err or "no error"
    out = "\n".join(out.split("\n"))
    output = f"**EXEC**:\n\n\
__Command:__\n`{cmd}`\n__PID:__\n`{pid}`\n__RETURN:__\n`{ret}`\n\n\
**stderr:**\n`{err}`\n\n**stdout:**\n``{out}`` "
    await message.edit_or_send_as_file(
        text=output, parse_mode="md", filename="exec.txt", caption=cmd
    )


@userge.on_cmd(
    "term",
    about={
        "header": "run commands in shell (terminal)",
        "usage": "{tr}term [commands]",
        "examples": '{tr}term echo "USERGE-X"',
    },
    allow_channels=False,
)
async def term_(message: Message):
    """run commands in shell (terminal with live update)"""
    cmd = await init_func(message)
    if cmd is None:
        return
    await message.edit("`Executing terminal ...`")
    try:
        t_obj = await Term.execute(cmd)  # type: Term
    except Exception as t_e:  # pylint: disable=broad-except
        await message.err(str(t_e))
        return
    curruser = getuser()
    try:
        uid = geteuid()
    except ImportError:
        uid = 1
    output = f"{curruser}:~# {cmd}\n" if uid == 0 else f"{curruser}:~$ {cmd}\n"
    sleep_for = 1
    _stdout = ""
    async for stdout in t_obj.get_output():
        if message.process_is_canceled:
            t_obj.cancel()
            return await message.reply("`process canceled!`")
        if _stdout != stdout:
            if len(stdout) <= 4096:
                await message.edit(
                        f"<code>{stdout}</code>",
                        disable_web_page_preview=True,
                        parse_mode="html",
                )
            _stdout = stdout
        if sleep_for >= 6:
            sleep_for = 1
        sleep_for += 1
        await asyncio.sleep(sleep_for)
    out_data = f"<pre>{output}{t_obj.full_std}</pre>"
    await message.edit_or_send_as_file(
        out_data, parse_mode="html", filename="term.txt", caption=cmd
    )

async def init_func(message: Message):
    cmd = message.input_str
    if not cmd:
        await message.err("No Command Found!")
        return None
    #    if "config.env" in cmd:
    #        await message.err("That's a dangerous operation! Not Permitted!")
    #        return None
    return cmd


class Term:
    " Live Term By Ryuk "
    def __init__(self, process):
        self.process = process
        self.full_std = ""
        self.is_done = False

    async def read_output(self):
        while True:
            line = (await self.process.stdout.readline()).decode("utf-8")
            if not line:
                break
            self.full_std += line
        self.is_done = True
        await self.process.wait()

    async def get_output(self):
        while not self.is_done:
            yield self.full_std

    def cancel(self):
        if not self.is_done:
            self.process.kill()
            self._task.cancel()

    @classmethod
    async def execute(cls, cmd):
        sub_process = cls(
            process=await asyncio.create_subprocess_shell(
                cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT
            )
        )
        sub_process._task = asyncio.create_task(
            sub_process.read_output(), name="AsyncShell"
        )
        await asyncio.sleep(0.5)
        return sub_process