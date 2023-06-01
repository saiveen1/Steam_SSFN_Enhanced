import vals
import requests


def request_state(response):
    if response.status_code == 429:
        return 429
    return None


def get_player_bans(steam_id):
    api_count = 0
    response = None
    while api_count < 4:
        if vals.apis[api_count][1] is False:
            api = vals.apis[api_count][0]
            vals.apis[api_count][1] = True
        else:
            api_count += 1
            continue
        url = f"https://api.steampowered.com/ISteamUser/GetPlayerBans/v1/" \
              f"?key={api}&steamids={steam_id}"
        try:
            response = requests.get(url)
            # print(url, response.status_code)
        except requests.exceptions.ProxyError:
            print("连接错误", url, response)
            api_count += 1
            continue
        except Exception as exp:
            print(url, response.status_code, exp)

        vals.apis[api_count][1] = False

        if response.status_code == 429:
            api_count += 1
            continue
        data = response.json()
        if len(data['players']) == 0:
            return None
        if response.status_code == 200 and 'players' in data:
            data = response.json()
            return data

    return request_state(response)


def get_owned_games(steam_id):
    api_count = 0
    response = None
    while api_count < 4:
        if vals.apis[api_count][1] is False:
            api = vals.apis[api_count][0]
            vals.apis[api_count][1] = True
        else:
            api_count += 1
            continue
        url = f"https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/" \
              f"?key={api}&steamid={steam_id}" \
              f"&include_appinfo=true" \
              f"&include_extended_appinfo=true"
        try:
            response = requests.get(url)
            # print(url, response.status_code)
        except requests.exceptions.ProxyError:
            print("连接错误", url, response)
            api_count += 1
            continue
        except Exception as exp:
            print(url, response.status_code, exp)
            api_count += 1
            continue

        vals.apis[api_count][1] = False

        if response.status_code == 429:
            api_count += 1
            print(f"{api}请求频率过快", url, response.status_code)
            continue
        data = response.json()
        if response.status_code == 200 and data['response'] != '':
            return data
    return request_state(response)
