DEBUG = False
loc_path = './ssfn_local'
headers = {
    'user-agent': 'Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.1)',
    'Content-Type': 'application/x-www-form-urlencoded'
}
l_urls = [r'https://ssfnbox.com/download/',
          r'https://ssfn.top/ssfn/',
          r'https://ghproxy.com/https://raw.githubusercontent.com/teng521/ssfn/master/',
          r'https://fastly.jsdelivr.net/gh/teng521/ssfn@master/',
          r'http://81.68.246.116/ssfn/',
          r'http://tool.ctrl000.cc:66/ssfn/'
          ]
default_account = '123----456----ssfn6094777681074169870----76561199163321234....'


class STATUS:
    class SSFNError:
        SSFN_NOT_FOUND = 1
        SSFN_DOWNLOAD_ERROR = 2
        NET_SSL_ERROR = 3

    class ApiERROR:
        STEAMID_NOT_FOUND = -1

    SSFN_DOWNLOAD_SUCCESS = 6
    WRITE_PERMISSION_ERROR = 4
    STEAM_NOT_FOUND_ERROR = 5


class EVENTS:
    login = "自适应版本登录"
