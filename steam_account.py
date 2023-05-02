import datetime
import re
import threading

import requests
from steam.webapi import WebAPI


class SteamAccount:
    api = None
    thread = None
    initialized = False

    @staticmethod
    def get_webAPI():
        if not SteamAccount.initialized:
            thread = threading.Thread(target=SteamAccount.thread_webapi, args=())
            thread.start()
            thread.join()
            SteamAccount.initialized = True

    @staticmethod
    def thread_webapi():
        SteamAccount.api = WebAPI(key='0F6C12E262EE5101755F668842217EE7')

    def __init__(self, account_str):
        self.account_str = account_str
        self.steam_id = None

    # 会占用线程时间, 单启动一个线程获取

    def parse_login_info(self) -> dict[str:str]:
        pattern = r'(\S+?)----(\S+?)----(ssfn\d+)----(\d+)?'  # 匹配17位数字的正则表达式
        result = re.findall(pattern, self.account_str)
        if result:
            self.steam_id = result[0][3] if result[0][3] else ''  # 判断是否存在17位数字
            extra, sale = self.account_str.split('----'.join([i for i in result[0] if i]))
            return {"username": result[0][0], "password": result[0][1],
                    "ssfn": result[0][2], "steamid": self.steam_id,
                    "extra_info": extra.rstrip(),
                    "sale_info": sale.lstrip('----')
                    }
        else:
            return None

    def get_games_ban(self) -> dict[str:str]:
        if SteamAccount.api is None:
            self.thread.join()
        data = SteamAccount.api.ISteamUser.GetPlayerBans(format='json', steamids=self.steam_id)
        # api判断的不准确，各种情况，还是要直接通过cookie 获取封禁具体
        days_since_last_ban = data['players'][0].pop('DaysSinceLastBan')
        last_ban_time = ''
        if days_since_last_ban != 0:
            last_ban_time = datetime.datetime.now() - datetime.timedelta(days=days_since_last_ban)
            last_ban_time = last_ban_time.replace(second=0, microsecond=0).strftime('%Y-%m-%d')
        data['players'][0]['LastBanTime'] = last_ban_time

        return data['players'][0]

    def get_game_info(self) -> dict[str:list]:
        data = SteamAccount.api.IPlayerService.GetOwnedGames(format='json', steamid=self.steam_id,
                                                             include_appinfo=True,
                                                             include_played_free_games=False,
                                                             appids_filter=0,
                                                             include_free_sub=False,
                                                             language='	it',
                                                             include_extended_appinfo=True
                                                             )
        return data['response']

    def get_account_info(self, api_check=False) -> dict[str:str]:
        # 这里可以优化以下，不过懒得弄了
        login_info = self.parse_login_info()
        if login_info is None:
            return None
        if login_info['steamid'] == '' or api_check is False:
            return login_info
        bans_info = None
        game_info = None
        try:
            if SteamAccount.api is None:
                SteamAccount.get_webAPI()
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
