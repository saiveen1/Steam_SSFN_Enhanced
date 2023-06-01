import sqlite3
import json

from SteamInfo.DBManager import DBManager

# 连接到数据库文件
conn = sqlite3.connect('../accounts.db')

# 创建一个游标对象来执行 SQL 语句
cursor = conn.cursor

db_manager = DBManager(r'../accounts.db')
db_manager.connect()
db_manager.create_table()

# 解析 JSON 数据
data = '''
{
    "remark": "\u6c38\u4e45",
    "username": "725mcyy397",
    "password": "k901wul99",
    "ssfn": "ssfn6238892867035664127",
    "steamid": "76561199255377825",
    "sale_info": "",
    "CommunityBanned": false,
    "VACBanned": false,
    "NumberOfVACBans": 0,
    "NumberOfGameBans": 1,
    "EconomyBan": "none",
    "LastBanTime": "2022-12-06",
    "game_count": 1,
    "games": [{
            "appid": 578080,
            "name": "PUBG: BATTLEGROUNDS",
            "playtime_forever": 507,
            "img_icon_url": "609f27278aa70697c13bf99f32c5a0248c381f9d",
            "has_community_visible_stats": true,
            "playtime_windows_forever": 507,
            "playtime_mac_forever": 0,
            "playtime_linux_forever": 0,
            "rtime_last_played": 1683480716,
            "has_workshop": false,
            "has_market": true,
            "has_dlc": true,
            "content_descriptorids": [2, 5]
        }],
    "cs_total": 3,
    "cs_2week": 0,
    "pubg_total": 4,
    "pubg_2week": 0
}
'''

data = json.loads(data)

db_manager.insert_data("accounts", data)

# 提交更改并关闭连接
conn.commit()
conn.close()
