import datetime
import re
import threading

import requests
from steam.webapi import WebAPI

import vals


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
            SteamAccount.api = vals.STATUS.ApiERROR.API_NET_ERROR

    def __init__(self, account_str, api_check=False):
        self.is_danger = None
        self.str_acc = account_str
        self.steam_id = None
        self.d_acc_info = None
        self.get_account_info(api_check=api_check)
        self.api_check = api_check
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
                self.steam_id = '' if len(result[0]) == 3 else result[0][3] if result[0][3] is not None else ''
                # 判断是否存在17位数字
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

    def get_multi_info(self, api_check=True) -> str:
        self.api_check = api_check
        self.get_account_info(api_check=True)
        if self.steam_id == vals.STATUS.ApiERROR.STEAMID_NOT_FOUND:
            return "未找到玩家，请确认steamid是否正确"
        elif self.api_check is False:
            return 'api查询已关闭'
        elif self.d_acc_info is None or self.steam_id == '':
            return '未获取到steamid'
        elif SteamAccount.api == vals.STATUS.ApiERROR.API_NET_ERROR:
            return "API网络连接错误！"
        num_game_bans = self.d_acc_info['NumberOfGameBans']
        last_ban = '' if num_game_bans == 0 else '上次封禁时间: '
        line = '' if num_game_bans == 0 else '\n'
        vac_ban = '是' if self.d_acc_info['VACBanned'] is True else '否'
        number_vac_bans = '' if vac_ban == '否' else self.d_acc_info['NumberOfVACBans']

        games_summary = "玩家资料已隐藏"
        if 'games' in self.d_acc_info:
            for d in self.d_acc_info['games']:
                if d['appid'] == 578080:
                    d['pubg_total'] = int(d['playtime_forever'] / 60)
                    d['pubg_2week'] = int(d['playtime_2weeks'] / 60) if 'playtime_2weeks' in d else 0
                if d['appid'] == 730:
                    d['cs_total'] = int(d['playtime_forever'] / 60)
                    d['cs_2week'] = int(d['playtime_2weeks'] / 60) if 'playtime_2weeks' in d else 0
            # d['pubg_total'] = [d['playtime_forever'] for d in data if d['appid'] == 578080][0]
            csgo = '' if d['cs_total'] is None or d['cs_total'] == 0 else f"CSGO总时长: {d['cs_total']}小时\n" \
                                                                f"CSGO最近两周时长: {d['cs_2week']}小时\n"
            games_summary = f"共{self.d_acc_info['game_count']}个游戏\n" \
                            f"吃鸡总时长: {d['pubg_total']}小时\n" \
                            f"吃鸡最近两周时长: {d['pubg_2week']}小时\n" \
                            f"{csgo}" \
                            f"额外信息: {self.d_acc_info['remark']}\n" \
                            f"购买信息：{self.d_acc_info['sale_info']}"

        multi_info = f"游戏封禁：{num_game_bans}   " \
                     f"{last_ban}{self.d_acc_info['LastBanTime']}{line}" \
                     f"Vac封禁: {vac_ban}      " \
                     f"{'' if vac_ban == '否' else 'Vac封禁个数: '}{number_vac_bans}\n" \
                     + games_summary

        return multi_info

    def get_account_info(self, api_check=False) -> dict[str:str]:
        # 这里可以优化以下，不过懒得弄了
        if self.d_acc_info is None:
            d_login_info = self.parse_login_info()
        else:
            d_login_info = self.d_acc_info
        if d_login_info is None:
            return None
        if d_login_info['steamid'] == '' or api_check is False:
            return d_login_info
        bans_info = None
        game_info = None
        try:
            if SteamAccount.api is None:
                SteamAccount.get_webAPI()
            if SteamAccount.api == vals.STATUS.ApiERROR.API_NET_ERROR:
                return -3, SteamAccount.api
            bans_info = self.get_games_ban()
            game_info = self.get_game_info()
        except IndexError as exp:
            self.steam_id = vals.STATUS.ApiERROR.STEAMID_NOT_FOUND
            return self.steam_id, exp
        except requests.exceptions.SSLError:
            bans_info['GameBans'] = 'Net error'
        except requests.exceptions.RequestException as exp:
            return -2, exp
        except Exception as exp:
            return -1, exp
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
