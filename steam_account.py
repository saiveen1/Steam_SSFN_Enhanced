import datetime
import re
import threading

import requests
from steam.webapi import WebAPI


class SteamAccount:

    def __init__(self, account_str):
        self.account_str = account_str
        self.steam_id = None
        self.api = None
        self.thread = None
        self.thread = threading.Thread(target=self.thread_webapi, args=())
        self.thread.start()

    # 会占用线程时间, 单启动一个线程获取
    def thread_webapi(self):
        self.api = WebAPI(key='0F6C12E262EE5101755F668842217EE7')

    def parse_login_info(self) -> dict[str:str]:
        pattern = r'(\S+?)----(\S+?)----(ssfn\d+)(----(\d+))?'  # 匹配7位数字的正则表达式
        result = re.findall(pattern, self.account_str)
        if result:
            self.steam_id = result[0][4] if result[0][4] else ''  # 判断是否存在7位数字
            return {"username": result[0][0], "password": result[0][1], "ssfn": result[0][2], "steamid": self.steam_id}
        else:
            return None

    def get_games_ban(self) -> dict[str:str]:
        if self.api is None:
            self.thread.join()
        data = self.api.ISteamUser.GetPlayerBans(format='json', steamids=self.steam_id)
        # api判断的不准确，各种情况，还是要直接通过cookie 获取封禁具体
        days_since_last_ban = data['players'][0].pop('DaysSinceLastBan')
        last_ban_time = ''
        if days_since_last_ban != 0:
            last_ban_time = datetime.datetime.now() - datetime.timedelta(days=days_since_last_ban)
            last_ban_time = last_ban_time.replace(second=0, microsecond=0).strftime('%Y-%m-%d')
        data['players'][0]['LastBanTime'] = last_ban_time
        # <class 'dict'> {'players':
        # [{'SteamId': '76561198425601856', 'CommunityBanned': False,
        # 'VACBanned': False, 'NumberOfVACBans': 0, 'NumberOfGameBans': 1,
        # 'EconomyBan': 'none', 'LastBanTime': '2023-04-13'}]}

        return data['players'][0]

    def get_game_info(self) -> dict[str:list]:
        data = self.api.IPlayerService.GetOwnedGames(format='json', steamid='76561199248569212',
                                                     include_appinfo=True,
                                                     include_played_free_games=False,
                                                     appids_filter=0,
                                                     include_free_sub=False,
                                                     language='	it',
                                                     include_extended_appinfo=True
                                                     )
        return data['response']

    def get_account_info(self, api_check=False) -> dict[str:str]:
        login_info = self.parse_login_info()
        if login_info is None:
            return None
        if login_info['steamid'] == '' or api_check is False:
            return login_info
        bans_info = None
        game_info = None
        try:
            bans_info = self.get_games_ban()
            game_info = self.get_game_info()
        except Exception as exp:
            return -1, exp
        except requests.exceptions.SSLError:
            bans_info['GameBans'] = 'Net error'
        except requests.exceptions.RequestException as exp:
            return -2, exp

        return {**login_info, **bans_info, **game_info}

    def get_owned_games(self):
        # ...
        pass
