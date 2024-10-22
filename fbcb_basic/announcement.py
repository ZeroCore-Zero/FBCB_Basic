import re

from mcdreforged.api.types import ServerInterface, CommandSource, Info
from mcdreforged.api.command import CommandContext, Literal, Integer, GreedyText
from mcdreforged.api.rtext import RText, RTextList, RColor

from fbcb_basic.config import AnnouncementConfig
from fbcb_basic.utils import get_reply, generate_help, format_str


class Announcement:
    MODULE_NAME = "announcement"
    CONFIG_FILENAME = "announcement.json"
    COMMAND_PREFIX = "announcement"
    ROOT_ACTION = "查看服务器公告"
    ROOT_HELP = "显示公告帮助"

    def __init__(self, server, prev):
        self.server = server
        self.config = AnnouncementConfig()
        self.config.init(server, Announcement.CONFIG_FILENAME)
        self.config.load()

    def register_command(self, commandRoot):
        add_anouncement = (
            Literal("add")
            .then(
                GreedyText("content")
                .runs(self.add)
            )
        )

        del_announcement = (
            Literal("del")
            .then(
                Integer("index")
                .runs(self.delete)
            )
            .then(
                Literal("all")
                .runs(self.delete))
        )

        reload_announcement = (
            Literal("reload")
            .runs(self.config.load)
        )
        
        announcement = (
            Literal(Announcement.COMMAND_PREFIX)
            .runs(self.display)
            .then(reload_announcement)
            .then(add_anouncement)
            .then(del_announcement)
        )
        self.register_help(announcement)
        commandRoot.then(announcement)

    def register_help(self, commandRoot):
        help = generate_help(f"!!fbcb {Announcement.COMMAND_PREFIX}", [
            ["", "查看服务器公告"],
            ["help", "查看帮助"],
            ["reload", "重载公告"],
            ["add <content>", "添加公告"],
            ["del <all|index>", "删除全部/指定公告"],
        ])
        self.helpNode = Literal("help").runs(lambda src: src.reply(help))
        commandRoot.then(self.helpNode)

    def add(self, src: CommandSource, cxt: CommandContext):
        self.config.content.append(format_str(cxt["content"]))
        self.config.save()
        src.reply("公告添加成功")


    def delete(self, src: CommandSource, cxt:CommandContext):
        if "all" in cxt:
            self.config.content.clear(),
            self.config.save(),
            src.reply("删除成功")
            return
        
        try:
            self.config.content.pop(cxt["index"] - 1)
            self.config.save()
        except IndexError:
            src.reply("公告不存在")
        else:
            src.reply("删除成功")

    def display(self, player):
        reply, src = get_reply(self.server, player)
        if src != "console" and len(self.config.content) == 0:
            return

        if len(self.config.content) == 0:
            reply("没有公告")
            return
        reply(self.config.title)
        for i in range(len(self.config.content)):
            reply(RTextList(
                RText(f"[{i + 1}] ").set_color(RColor.aqua),
                self.config.content[i]
            ))

    def on_player_joined(self, server: ServerInterface, player, info: Info):
        self.display(player)
