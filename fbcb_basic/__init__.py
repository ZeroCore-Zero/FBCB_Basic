from typing import Any

from mcdreforged.api.types import PluginServerInterface, ServerInterface, Info, CommandSource
from mcdreforged.api.command import Literal, GreedyText, CommandContext, Integer
from mcdreforged.api.rtext import RTextBase, RText, RTextList, RColor

from fbcb_basic.utils import generate_help
from fbcb_basic.config import Config
from fbcb_basic.motd import Motd
from fbcb_basic.announcement import Announcement
from fbcb_basic.todolist import TodoList
from fbcb_basic.vote import Vote


PREFIX = '!!fbcb'
config = Config()
modules = {}
commandRoot = Literal(PREFIX)


def resiger_command():
    global commandRoot, modules
    # command root messages
    rootMsg = [
        ["", "显示此列表"],
        ["help", "查看帮助总览"]
    ]
    rootMsg.extend([[module.COMMAND_PREFIX, module.ROOT_ACTION] for module in modules.values()])
    commandHelp = generate_help(f"{PREFIX}", rootMsg)
    commandRoot.runs(lambda src: src.reply(commandHelp))
    # register command for modules
    for module in modules.values():
        module.register_command(commandRoot)

    # help messages
    helpMsg = [
        ["", "显示此列表"]
    ]
    helpMsg.extend([[module.COMMAND_PREFIX, module.ROOT_HELP] for module in modules.values()])
    HelpList = generate_help(f"{PREFIX} help", helpMsg)
    help_commands = Literal("help").runs(lambda src: src.reply(HelpList))
    for module in modules.values():
        help_commands.then(Literal(module.COMMAND_PREFIX).redirects(module.helpNode))
    commandRoot.then(help_commands)


def on_load(server: PluginServerInterface, prev_module: Any):
    global config, modules
    # init config
    config.init(server, "config.json")
    config.load()
    # init modules
    modules[Motd.MODULE_NAME] = Motd(server, prev_module)
    modules[Announcement.MODULE_NAME] = Announcement(server, prev_module)
    modules[TodoList.MODULE_NAME] = TodoList(server, prev_module)
    modules[Vote.MODULE_NAME] = Vote(server, prev_module)
    # register commands
    server.register_help_message(PREFIX, 'FBCB基础插件')
    resiger_command()
    commandRoot.then(Literal("config").then(Literal("reload").runs(config.load)))
    server.register_command(commandRoot)

def on_unload(server: PluginServerInterface):
    global config, modules
    for module in modules:
        if getattr(config, module) and hasattr(modules[module], "on_unload"):
            modules[module].on_unload(server)


def on_player_joined(server: ServerInterface, player, info: Info):
    global config, modules
    for module in modules:
        if getattr(config, module):
            modules[module].on_player_joined(server, player ,info)
