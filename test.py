from steam.webapi import WebAPI
api = WebAPI(key='0F6C12E262EE5101755F668842217EE7')
steam_id = '76561198425601856'
# 获取封禁信息
#print(api.ISteamUser.GetPlayerBans(format='json', steamids=steam_id))

# 获取汇总信息
#print(api.ISteamUser.GetPlayerSummaries(steamids=steam_id))

# 获取最近游戏
#print(api.IPlayerService.GetRecentlyPlayedGames(steamids=steam_id))

# 获取拥有游戏
# https://steamapi.xpaw.me/#IPlayerService/GetRecentlyPlayedGames
#print(api.IPlayerService.GetOwnedGames(steam_id=steam_id, include_appinfo=True))

#print(api.ISteamUser.doc())

from steam.steamid import SteamID
print(api.ISteamUser.ResolveVanityURL(vanityurl="valve", url_type=2))



from steam.client import SteamClient
from steam.enums.emsg import EMsg

client = SteamClient()

@client.on(EMsg.ClientVACBanStatus)
def print_vac_status(msg):
    print("Number of VAC Bans: %s" % msg.body.numBans)

client.cli_login()

print("Logged on as: %s" % client.user.name)
print("Community profile: %s" % client.steam_id.community_url)
print("Last logon: %s" % client.user.last_logon)
print("Last logoff: %s" % client.user.last_logoff)
print("Number of friends: %d" % len(client.friends))

client.logout()