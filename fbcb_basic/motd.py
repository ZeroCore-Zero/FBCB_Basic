import time

from mcdreforged.api.types import ServerInterface, PluginServerInterface, Info
from mcdreforged.api.command import Literal

from fbcb_basic.config import MotdConfig
from fbcb_basic.utils import get_reply, generate_help


class Motd:
    MODULE_NAME = "motd"
    CONFIG_FILENAME = "motd.json"
    COMMAND_PREFIX = "motd"
    ROOT_ACTION = "查看服务器motd"
    ROOT_HELP = "显示motd帮助"

    def __init__(self, server: PluginServerInterface, prev):
        self.server = server
        self.config = MotdConfig()
        self.config.init(server, Motd.CONFIG_FILENAME)
        self.config.load()

    def register_command(self, commandRoot):
        motd = (
            Literal(Motd.COMMAND_PREFIX)
            .runs(self.display)
            .then(
                Literal("reload")
                .runs(self.config.load)
            )
        )
        self.register_help(motd)
        commandRoot.then(motd)

    def register_help(self, commandRoot):
        help = generate_help(f"!!fbcb {Motd.COMMAND_PREFIX}", [
            ["", "查看服务器motd"],
            ["help", "查看帮助"],
            ["reload", "重载motd"]
        ])
        self.helpNode = Literal("help").runs(lambda src: src.reply(help))
        commandRoot.then(self.helpNode)

    def display(self, player):
        reply, player = get_reply(self.server, player)
        if player == "console":
            player = "Welcome"
        
        daycount = self.server.get_plugin_instance("daycount_nbt")
        reply(self.config.message["welcome"].format(player, self.config.serverName))
        reply(self.config.message["daycount"].format(time.strftime("%Y-%m-%d"), daycount.getday()))

    def on_player_joined(self, server: ServerInterface, player, info: Info):
        self.display(player)
