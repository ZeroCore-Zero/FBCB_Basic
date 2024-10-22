# FBCB Basic

为服务器添加一些基础功能的MCDR插件

## 使用帮助

- `!!fbcb` 显示总菜单
- `!!fbcb help` 查看帮助总览

1. Motd
    1. `!!fbcb motd` 查看服务器motd
    2. `!!fbcb motd help` 查看motd帮助
    3. `!!fbcb motd reload` 重载motd
2. Announcement
    1. `!!fbcb announcement` 查看服务器公告
    2. `!!fbcb announcement help` 查看公告帮助
    3. `!!fbcb announcement reload` 重载公告
    4. `!!fbcb announcement add <content>` 添加公告
        > `<content>`匹配从`add(空格)`后的所有内容，支持Mincecraft格式化代码，使用`/`替换`§`即可
    5. `!!fbcb announcement del <all|index>` 删除全部/指定公告
        > 匹配字符串`all`或公告序号`index`
3. TodoList
    1. `!!fbcb todolist` 查看服务器todolist
    2. `!!fbcb todolist help` 查看todolist帮助
    3. `!!fbcb todolist reload` 重载todolist
    4. `!!fbcb todolist add <title> <content>` 添加待办事项
        > `<title>`, `content>`如有空格可用双引号`""`包裹，支持Mincecraft格式化代码，使用`/`替换`§`即可
    5. `!!fbcb todolist del <all|index>` 删除全部/指定待办事项
        > 匹配字符串`all`或公告序号`index`
    6. `!!fbcb todolist move <from> <behind>` 移动指定待办事项
        > 将序号为`<from>`的待办事项移动到序号为`<behind>`的待办事项之后
4. Vote
    1. `!!fbcb votd` 查看服务器投票主页
    2. `!!fbcb votd help` 显示投票帮助
    3. `!!fbcb votd reload` 重载投票系统
    4. `!!fbcb votd list` 列出所有投票
    5. `!!fbcb votd show <id>` 显示某一投票id的详细信息
    6. `!!fbcb votd add <title> <description> [share=True]` 作为发起人发起一次投票
    7. `!!fbcb votd del <id>` 删除某一投票
    8. `!!fbcb votd agree <id>` 投赞成票
    9. `!!fbcb votd disagree <id>` 投反对票
    10. `!!fbcb votd finish <id>` 强制提前结束某一投票
