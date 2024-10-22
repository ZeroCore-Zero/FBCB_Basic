import re

from mcdreforged.api.types import CommandSource
from mcdreforged.api.rtext import RTextBase


def get_reply(server, src):
    # 控制台
    if isinstance(src, CommandSource):
        reply = src.reply
        name = "console"
    # 玩家
    else:
        def reply(message: str|RTextBase, **kwargs):
            server.tell(src, message, **kwargs)
        name = src
    return reply, name

def generate_help(helpRoot, helpList):
    help = "\n".join([
        "§6{}{}§r §7{}".format(
            helpRoot,
            " " + helpCommand if len(helpCommand) != 0 else "",
            helpContent
        )
        for helpCommand, helpContent in helpList
    ])
    return help

def format_str(src):
    return re.sub(r'/(?=[^/\s])', '§', src)