from steam.webapi import WebAPI
api = WebAPI(key='0F6C12E262EE5101755F668842217EE7')
steam_id = '76561198425601856'
# 获取封禁信息
# print(api.ISteamUser.GetPlayerBans(format='json', steamids=steam_id))


def get_games_ban(steamid):
    print(api.ISteamUser.GetPlayerBans(format='json', steamids=steam_id))


if __name__ == '__main__':
    get_games_ban('76561198425601856')