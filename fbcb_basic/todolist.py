from mcdreforged.api.types import ServerInterface, PluginServerInterface, CommandSource, Info
from mcdreforged.api.rtext import RText, RTextList, RColor
from mcdreforged.api.command import Literal, QuotableText, Integer

from fbcb_basic.config import TodoListConfig
from fbcb_basic.utils import get_reply, generate_help, format_str


class TodoList:
    MODULE_NAME = "todolist"
    CONFIG_FILENAME = "todolist.json"
    COMMAND_PREFIX = "todolist"
    ROOT_ACTION = "查看服务器待办清单"
    ROOT_HELP = "显示待办清单帮助"

    def __init__(self, server: PluginServerInterface, prev):
        self.server = server
        self.config = TodoListConfig()
        self.config.init(server, TodoList.CONFIG_FILENAME)
        self.config.load()

    def register_command(self, commandRoot):
        add_todolist = (
            Literal("add")
            .then(
                QuotableText("title")
                .then(
                    QuotableText("content")
                    .runs(self.add)
                )
            )
        )

        del_todolist = (
            Literal("del")
            .then(
                Integer("index")
                .runs(self.delete)
            )
            .then(
                Literal("all")
                .runs(self.delete))
        )

        move_todolist = (
            Literal("move")
            .then(
                Integer("from")
                .then(
                    Integer("behind")
                    .runs(self.move)
                )
            )
        )

        reload_todolist = (
            Literal("reload")
            .runs(self.config.load)
        )

        todolist = (
            Literal(TodoList.COMMAND_PREFIX)
            .runs(self.display)
            .then(reload_todolist)
            .then(add_todolist)
            .then(del_todolist)
            .then(move_todolist)
        )
        self.register_help(todolist)
        commandRoot.then(todolist)

    def register_help(self, commandRoot):
        help = generate_help(f"!!fbcb {TodoList.COMMAND_PREFIX}", [
            ["", "查看服务器todolist"],
            ["help", "查看帮助"],
            ["reload", "重载todolist"],
            ["add <title> <content>", "添加待办事项"],
            ["del <all|index>", "删除全部/指定待办事项"],
            ["move <from> <behind>", "移动指定待办事项"]
        ])
        self.helpNode = Literal("help").runs(lambda src: src.reply(help))
        commandRoot.then(self.helpNode)

    def add(self, src: CommandSource, cxt: CommandSource):
        self.config.content.append({
            "title": format_str(cxt["title"]),
            "content": format_str(cxt["content"])
        })
        self.config.save()
        src.reply("添加成功")

    def delete(self, src: CommandSource, cxt: CommandSource):
        if "all" in cxt:
            self.config.content.clear(),
            self.config.save(),
            src.reply("删除成功")
            return
        
        try:
            self.config.content.pop(cxt["index"] - 1)
            self.config.save()
        except IndexError:
            src.reply("待办事项不存在")
        else:
            src.reply("删除成功")

    def move(self, src: CommandSource, cxt: CommandSource):
        self.config.content.insert(cxt["behind"], self.config.content.pop(cxt["from"] - 1))
        self.config.save()
        src.reply("移动成功")


    def display(self, player):
        reply, src = get_reply(self.server, player)
        if src != "console" and len(self.config.content) == 0:
            return

        if len(self.config.content) == 0:
            reply("没有待办事项")
            return
        reply(self.config.title)
        for i in range(len(self.config.content)):
            content = self.config.content[i]
            reply(RTextList(
                RText(f"[{i + 1}] ").set_color(RColor.aqua),
                RText(content["title"]).set_color(RColor.gold), " §7->§r ",
                RText(content["content"]).set_color(RColor.green)
            ))

    def on_player_joined(self, server: ServerInterface, player, info: Info):
        if len(self.config.content) == 0:
            return
        server.tell(player, f"当前服务器有{len(self.config.content)}个待办事项，输入§6!!fbcb {TodoList.COMMAND_PREFIX}§r查看")
