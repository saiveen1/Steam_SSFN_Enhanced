DEBUG = True
loc_path = './ssfn_local'
headers = {
    'user-agent': 'Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.1)',
    'Content-Type': 'application/x-www-form-urlencoded'
}
ssfnbox_url = r'https://ssfnbox.com/download/'
l_backup_urls = [r'https://ssfn.top/ssfn/',
                 # r'https://ghproxy.com/https://raw.githubusercontent.com/teng521/ssfn/master/',
                 r'https://fastly.jsdelivr.net/gh/teng521/ssfn@master/',
                 r'http://81.68.246.116/ssfn/',
                 r'http://tool.ctrl000.cc:66/ssfn/'
                 ]


class STATUS:
    class SSFNError:
        SSFN_NOT_FOUND = 1
        SSFN_DOWNLOAD_ERROR = 2
        NET_SSL_ERROR = 3
    SSFN_DOWNLOAD_SUCCESS = 6
    WRITE_PERMISSION_ERROR = 4
    STEAM_NOT_FOUND_ERROR = 5
