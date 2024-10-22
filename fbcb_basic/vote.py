import time
import json

from mcdreforged.api.types import ServerInterface, PluginServerInterface, Info, CommandSource
from mcdreforged.api.rtext import RTextBase, RText, RTextList, RColor, RAction
from mcdreforged.api.command import Literal, Integer, QuotableText, Boolean, Text

from fbcb_basic.config import VoteConfig
from fbcb_basic.utils import get_reply, generate_help


class Vote:
    MODULE_NAME = "vote"
    CONFIG_FILENAME = "vote.json"
    COMMAND_PREFIX = "vote"
    ROOT_ACTION = "查看服务器投票主页"
    ROOT_HELP = "显示投票帮助"

    def __init__(self, server: PluginServerInterface, prev=None):
        self.server = server
        self.config = VoteConfig()
        self.config.init(server, Vote.CONFIG_FILENAME)
        self.config.load()
        self._get_ongoings()
        self.voteMap = {}
        for item in self.config.content:
            self.voteMap[item["id"]] = item

    def _get_format_time(self, timestr):
        year = timestr[:4]
        mounth = timestr[4:6]
        day = timestr[6:8]
        hour = timestr[8:10]
        minute = timestr[10:12]
        return f"{year}年{mounth}月{day}日{hour}时{minute}分"
    
    def _verify_time(self, timestr):
        try:
            time.strftime("%Y%m%d%H%M", time.strptime(str(timestr), "%Y%m%d%H%M"))
        except ValueError:
            return False
        return True
        

    def _verify_id(self, id):
        if id in self.voteMap:
            return True
        return False


    def _check_status(self, target=None):
        """ :param target: a single vote or None for check all """
        if target is None:
            target = self.config.content
        else:
            target = [target]
        now = time.strftime("%Y%m%d%H%M")
        for item in target:
            if now > item["info"]["finishAt"]:
                item["status"] = "Finished"
            elif now < item["info"]["startAt"]:
                item["status"] = "NotStart"
            else:
                item["status"] = "InProgress"

    def _get_ongoings(self):
        """ 维护一个正在进行的列表 """
        self.ongoings = []
        self.prepare_ongoings = []
        self._check_status()
        for item in self.config.content:
            if item["status"] == "InProgress":
                self.ongoings.append(item)
            elif item["status"] == "NotStart":
                self.prepare_ongoings.append(item)

    def _update_ongoings(self):
        now = time.strftime("%Y%m%d%H%M")
        for item in self.ongoings:
            if now > item["info"]["finishAt"]:
                item["status"] = "Finished"
                self.ongoings.remove(item)
        for item in self.prepare_ongoings:
            if now > item["info"]["startAt"]:
                item["status"] = "InProgress"
                self.prepare_ongoings.remove(item)
                self.ongoings.append(item)

    def register_command(self, commandRoot):
        reload_Node = Literal("reload").runs(lambda: self.__init__(self.server))
        list_Node = Literal("list").runs(self._list_cmd)
        show_Node = Literal("show").then(Integer("id").runs(self._show_cmd))
        add_Node = Literal("add").then(
            QuotableText("title").then(
            QuotableText("description").then(
            Integer("startAt").then(
            Integer("finishAt").runs(self._add_cmd).then(
                Boolean("share").runs(self._add_cmd)
            )))))
        del_Node = Literal("del").then(Integer("id").runs(self._del_cmd))
        agree_Node = Literal("agree").then(Integer("id").runs(self._agree_cmd))
        disagree_Node = Literal("disagree").then(Integer("id").runs(self._disagree_cmd))
        finish_Node = Literal("finish").then(Integer("id").runs(self._finish_cmd))
        ban_Node = Literal("ban").then(Text("player").runs(self._ban_cmd))
        deban_Node = Literal("deban").then(Text("player").runs(self._deban_cmd))
        banlist_Node = Literal("banlist").runs(self._banlist_cmd)

        vote_node = (
            Literal("vote")
            .runs(self.display)
            .then(reload_Node)
            .then(list_Node)
            .then(show_Node)
            .then(add_Node)
            .then(del_Node)
            .then(agree_Node)
            .then(disagree_Node)
            .then(finish_Node)
            .then(ban_Node)
            .then(deban_Node)
            .then(banlist_Node)
        )
        self.register_help(vote_node)
        commandRoot.then(vote_node)

    def register_help(self, commandRoot):
        help = generate_help(f"!!fbcb {Vote.COMMAND_PREFIX}", [
            ["", "查看服务器投票主页"],
            ["help", "显示投票帮助"],
            ["reload", "重载投票系统"],
            ["list", "列出所有投票"],
            ["show <id>", "显示某一投票id的详细信息"],
            ["add <title> <description> <startAt> <finishAt> [share=True]", "作为发起人发起一次投票"],
            ["del <id>", "删除某一投票"],
            ["agree <id>", "投赞成票"],
            ["disagree <id>", "投反对票"],
            ["finish <id>", "强制提前结束某一投票"],
            ["ban <player>", "禁止该玩家发起投票"],
            ["deban <player>", "重新允许该玩家发起投票"],
            ["banlist", "查看投票黑名单"]
        ])
        self.helpNode = Literal("help").runs(lambda src: src.reply(help))
        commandRoot.then(self.helpNode)


    def on_player_joined(self, server: ServerInterface, player, info: Info):
        self._update_ongoings()
        if len(self.ongoings) == 0:
            return
        server.tell(player, f"当前服务器有{len(self.ongoings)}个正在进行中的投票，输入§6!!fbcb vote§r查看")


    def display(self, player):
        self._update_ongoings()
        reply, src = get_reply(self.server, player)
        if len(self.ongoings) == 0:
            reply("没有正在进行的投票")
            return
        reply("§7-------§r 服务器投票列表§b[正在进行]§r §7-------§r")
        for i in range(len(self.ongoings)):
            content = self.ongoings[i]
            proposer = content["info"]["proposer"] if content["info"]["share"] else "匿名玩家"
            reply(RTextList(
                RText(f"§b[ID: {content["id"]}]§r §6{content["title"]}§r 由§b{proposer}§r发起").set_click_event(RAction.run_command, f"!!fbcb {Vote.COMMAND_PREFIX} show {content["id"]}").set_hover_text("§e查看详情§r"),
                " ",
                RText("[赞成]").set_click_event(RAction.run_command, f"!!fbcb {Vote.COMMAND_PREFIX} agree {content["id"]}").set_hover_text("§a点击赞成§r").set_color(RColor.green), " ",
                RText("[反对]").set_click_event(RAction.run_command, f"!!fbcb {Vote.COMMAND_PREFIX} disagree {content["id"]}").set_hover_text("§c点击反对§r").set_color(RColor.red)
            ))


    def _list_cmd(self, player):
        self._update_ongoings()
        reply, src = get_reply(self.server, player)
        if len(self.config.content) == 0:
            reply("投票列表为空")
            return
        reply("§7-------§r 服务器投票列表§b[所有投票]§r §7-------§r")
        for item in self.config.content:
            proposer = item["info"]["proposer"] if item["info"]["share"] or item["info"]["proposer"] == src else "匿名玩家"
            reply(RTextList(
                RText(f"[ID: {item["id"]}]").set_color(RColor.aqua),
                "§b[正在进行]§r" if item["status"] == "InProgress" else "§7[尚未开始]§r" if item["status"] == "NotStart" else "§c[已经结束]§r", " ",
                RText(item["title"]).set_color(RColor.gold), " ",
                "由", RText(proposer).set_color(RColor.aqua), "发起"
            ).set_click_event(RAction.run_command, f"!!fbcb {Vote.COMMAND_PREFIX} show {item["id"]}").set_hover_text("§e查看详情§r"))

    def _show_cmd(self, src: CommandSource, cxt: CommandSource):
        self._update_ongoings()
        if not self._verify_id(cxt["id"]):
            src.reply("投票不存在")
            return
        item = self.voteMap[cxt["id"]]
        if hasattr(src, "player"):
            if item["info"]["share"] or src.player == item["info"]["proposer"] or src.get_permission_level() >= self.config.permission["show"]:
                proposer = item["info"]["proposer"]
                is_show = True
            else:
                proposer = "匿名玩家"
                is_show = False
        else:
            proposer = item["info"]["proposer"]
            is_show = True
        response = RTextList(
            f"§7-->§r 由§b{proposer}§r发起的ID为§6[{item["id"]}]§r的投票：§a{item["title"]}§r §7<--§r\n",
            f"§b§l=>§r {item["description"]}\n",
            f"开始于§e§n§o{self._get_format_time(item["info"]["startAt"])}§r，结束于§e§n§o{self._get_format_time(item["info"]["finishAt"])}§r\n",
            "当前状态：", "§b[正在进行]§r" if item["status"] == "InProgress" else "§7[尚未开始]§r" if item["status"] == "NotStart" else "§c[已经结束]§r", "\n",
        )
        if not is_show:
            response.append(f"发起人设置详细信息不可见")
        else:
            with open("./server/whitelist.json") as file:
                players = [name["name"] for name in json.load(file)]
            with open("./server/ops.json") as file:
                players.extend([name["name"] for name in json.load(file)])
            players = sorted(list(set(players)))
            for i in [*item["agrees"], *item["disagrees"]]:
                if i in players:
                    players.remove(i)
            response.append(
                RText("[赞成]").set_click_event(RAction.run_command, f"!!fbcb {Vote.COMMAND_PREFIX} agree {item["id"]}").set_hover_text("§a点击赞成§r").set_color(RColor.green),
                f"{len(item["agrees"])}人：", ", ".join(item["agrees"]), "\n",
                RText("[反对]").set_click_event(RAction.run_command, f"!!fbcb {Vote.COMMAND_PREFIX} disagree {item["id"]}").set_hover_text("§c点击反对§r").set_color(RColor.red),
                f"{len(item["disagrees"])}人：", ", ".join(item["disagrees"]), "\n",
                f"未投票{len(players)}人：", ", ".join(players)
            )
        src.reply(response)


    def _add_cmd(self, src: CommandSource, cxt: CommandSource):
        if not hasattr(src, "player"):
            src.reply("只能由玩家发起投票")
            return
        if "share" in cxt:
            share = cxt["share"]
        else:
            share = True
        if hasattr(src, "player") and src.player in self.config.blacklist:
            src.reply("你处于黑名单内，无法发起投票")
            return
        if src.get_permission_level() < self.config.permission["add"]:
            src.reply("你无权发起投票")
        for i in [cxt["startAt"], cxt["finishAt"]]:
            if not self._verify_time(i):
                src.reply("非法的时间格式")
                return
        
        if len(self.config.content) == 0:
            voteid = 1
        else:
            voteid = self.config.content[-1]["id"] + 1
        vote = {
            "id": voteid,
            "title": cxt["title"],
            "description": cxt["description"],
            "agrees": [],
            "disagrees": [],
            "status": "NotStart",
            "info": {
                "startAt": str(cxt["startAt"]),
                "finishAt": str(cxt["finishAt"]),
                "proposer": src.player,
                "share": share
            }
        }
        self.config.content.append(vote)
        self.voteMap[vote["id"]] = vote
        self.prepare_ongoings.append(vote)
        self._update_ongoings()
        self.config.save()
        src.reply(f"§6添加成功，ID§b[{vote["id"]}]§r")


    def _del_cmd(self, src: CommandSource, cxt: CommandSource):
        if not self._verify_id(cxt["id"]):
            src.reply("无效的投票id")
            return
        if src.get_permission_level() < self.config.permission["del"]:
            src.reply("你无权删除此投票")
            return
        if self.voteMap[cxt["id"]] in self.ongoings:
            self.ongoings.remove(self.voteMap[cxt["id"]])
        self.config.content.remove(self.voteMap[cxt["id"]])
        self.voteMap.pop(cxt["id"])
        self.config.save()
        src.reply("删除成功")

    def _agree_cmd(self, src: CommandSource, cxt: CommandSource):
        self._update_ongoings()
        if not hasattr(src, "player"):
            src.reply("只能由玩家投票")
            return
        if not self._verify_id(cxt["id"]):
            src.reply("无效的投票id")
            return
        item = self.voteMap[cxt["id"]]
        if item in self.ongoings:
            if src.player in item["agrees"] or src.player in item["disagrees"]:
                src.reply("你已经投过票了")
            else:
                item["agrees"].append(src.player)
                src.reply("投票成功")
        self.config.save()

    def _disagree_cmd(self, src: CommandSource, cxt: CommandSource):
        self._update_ongoings()
        if not hasattr(src, "player"):
            src.reply("只能由玩家投票")
            return
        if not self._verify_id(cxt["id"]):
            src.reply("无效的投票id")
            return
        item = self.voteMap[cxt["id"]]
        if item in self.ongoings:
            if src.player in item["agrees"] or src.player in item["disagrees"]:
                src.reply("你已经投过票了")
            else:
                item["disagrees"].append(src.player)
                src.reply("投票成功")
        self.config.save()

    def _finish_cmd(self, src: CommandSource, cxt: CommandSource):
        if not self._verify_id(cxt["id"]):
            src.reply("无效的投票id")
            return
        item = self.voteMap[cxt["id"]]
        if item["status"] == "NotStart":
            src.reply("投票未开始")
            return
        elif item["status"] == "Finished":
            src.reply("投票已结束")
            return
        item["info"]["finishAt"] = time.strftime("%Y%m%d%H%M")
        item["status"] = "Finished"
        self.ongoings.remove(item)
        src.reply(f"强制终止投票§bID[{item["id"]}]§r")
        self.config.save()


    def _ban_cmd(self, src: CommandSource, cxt: CommandSource):
        self.config.blacklist.append(cxt["player"])
        self.config.save()
        src.reply(f"禁止玩家{cxt["player"]}发起投票")

    
    def _deban_cmd(self, src: CommandSource, cxt: CommandSource):
        if cxt["player"] not in self.config.blacklist:
            src.reply("玩家不在黑名单内")
            return
        self.config.blacklist.remove(cxt["player"])
        self.config.save()
        src.reply(f"重新允许玩家{cxt["player"]}发起投票")


    def _banlist_cmd(self, src: CommandSource, cxt: CommandSource):
        if len(self.config.blacklist) == 0:
            src.reply("黑名单内无玩家")
            return
        src.reply("禁止以下玩家发起投票：")
        src.reply("，".join(sorted(self.config.blacklist)))
