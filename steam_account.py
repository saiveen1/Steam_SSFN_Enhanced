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
        try:
            SteamAccount.api = WebAPI(key='0F6C12E262EE5101755F668842217EE7')
        # except requests.exceptions as exp:
        except requests.exceptions.SSLError:
            SteamAccount.api = 'Net Error'

    def __init__(self, account_str):
        self.is_danger = None
        self.str_acc = account_str
        self.steam_id = None
        self.d_acc_info = None
        self.get_account_info(api_check=False)
    # 会占用线程时间, 单启动一个线程获取

    def parse_login_info(self) -> dict[str:str]:
        if self.d_acc_info is None:
            pattern = r'(\S+?)----(\S+?)----(ssfn\d+)----(\d+)?'  # 匹配17位数字的正则表达式
            result = re.findall(pattern, self.str_acc)

            # 可以加一个括号，匹配出来的会多一个----
            if len(result) == 0:
                pattern = r'(\S+?)----(\S+?)----(ssfn\d+)'
                result = re.findall(pattern, self.str_acc)
            if result:
                self.steam_id = '' if len(result[0]) == 3 else result[0][3] if result[0][3] else ''  # 判断是否存在17位数字
                remark, sale = self.str_acc.split('----'.join([i for i in result[0] if i]))
                self.d_acc_info = {"remark": remark.rstrip(),
                                   "username": result[0][0], "password": result[0][1],
                                   "ssfn": result[0][2], "steamid": self.steam_id,
                                   "sale_info": sale.lstrip('----')
                                   }
                return self.d_acc_info
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
        d_login_info = self.parse_login_info()
        if d_login_info is None:
            return None
        if d_login_info['steamid'] == '' or api_check is False:
            return d_login_info
        bans_info = None
        game_info = None
        try:
            if SteamAccount.api is None:
                SteamAccount.get_webAPI()
            if SteamAccount.api == 'Net Error':
                return -3, SteamAccount.api
            bans_info = self.get_games_ban()
            game_info = self.get_game_info()
        except Exception as exp:
            return -1, exp
        except requests.exceptions.SSLError:
            bans_info['GameBans'] = 'Net error'
        except requests.exceptions.RequestException as exp:
            return -2, exp

        if bans_info['NumberOfGameBans'] > 0:
            self.is_danger = True
            if d_login_info['remark'] != '':
                self.str_acc = self.str_acc.replace(d_login_info['remark'], '永久', 1)
            else:
                self.str_acc = '永久 ' + self.str_acc
            d_login_info['remark'] = '永久'

        self.d_acc_info = {**d_login_info, **bans_info, **game_info}
        return self.d_acc_info

    def get_owned_games(self):
        # ...
        pass
