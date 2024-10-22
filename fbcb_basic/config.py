from typing import Union

from mcdreforged.api.utils import Serializable
from mcdreforged.api.types import PluginServerInterface


class baseConfig(Serializable):
    def init(self, server, file_name):
        self._server = server
        self._file_name = file_name

    def load(self, server: PluginServerInterface = None):
        if isinstance(server, PluginServerInterface):
            self._server = server
        self.merge_from(self._server.load_config_simple(file_name=self._file_name, target_class=self.__class__))

    def save(self):
        self._server.save_config_simple(config=self, file_name=self._file_name)


class Config(baseConfig):
    motd: bool = True
    announcement: bool = False
    todolist: bool = False
    vote: bool = False

    def init(self, server, file_name):
        super().init(server=server, file_name=file_name)


class MotdConfig(baseConfig):
    serverName: str = 'FBCB边境第一建设局'
    message: dict[str, str] = {
        "welcome": '§7=======§r §6{}§r，欢迎回到 §b§l{}§r！ §7=======§r',
        "daycount": '今天是§e{}§r，开服的第§e{}§r天'
    }

    def init(self, server, file_name):
        super().init(server, file_name)


class AnnouncementConfig(baseConfig):
    title: str =  "§7-------§r 服务器公告 §7-------§r"
    content: list[str] =  [
        "默认公告1",
        "默认公告2"
    ]

    def init(self, server, file_name):
        super().init(server, file_name)

class TodoListConfig(baseConfig):
    title: str =  "§7-------§r 服务器待办清单 §7-------§r"
    content: list[dict[str, Union[str, int]]] = [
        {
            "title": "示例事项标题",
            "content": "示例事项内容"
        }
    ]

    def init(self, server, file_name):
        super().init(server, file_name)

class VoteConfig(baseConfig):
    permission: dict[str, int] = {
        "show": 2,
        "add": 1,
        "del": 2
    }
    blacklist: list[str] = []
    content: list[dict[str, Union[int, str, list[str], dict[str, Union[str, bool]]]]] = [
        {
            "id": 1,
            "title": "示例投票标题",
            "description": "示例投票描述",
            "agrees": [
                "player1"
            ],
            "disagrees": [
                "player2"
            ],
            "status": "InProgress",
            "info": {
                "startAt": "202406061200",
                "finishAt": "202406072200",
                "proposer": "发起玩家",
                "share": True
            }
        }
    ]
    
    def init(self, server, file_name):
        super().init(server, file_name)
