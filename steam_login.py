import os
import re
import shutil
import subprocess
import time

import requests
import winreg

loc_path = './ssfn_local'
headers = {
    'user-agent': 'Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.1)',
    'Content-Type': 'application/x-www-form-urlencoded'
}
url = r'https://ssfnbox.com/download/'
backup_url = r'http://tool.ctrl000.cc:66/ssfn/'


class SteamLogin:
    def __init__(self, steam_path=None):
        self.steam_path = None
        self.ssfn_str = None

    @staticmethod
    def get_steam_path():
        # 注册表获取steam路径
        key = winreg.OpenKeyEx(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Valve\Steam")
        return winreg.QueryValueEx(key, 'SteamPath')[0]

    def init_ssfn(self):
        # 创建本地ssfn库
        if not os.path.exists(loc_path):
            os.makedirs(loc_path)

        # 删除steam目录下的ssfn文件
        for filename in os.listdir(self.steam_path):
            if re.match(r'ssfn.*', filename):
                os.remove(os.path.join(self.steam_path, filename))

    def save_file(self, ssfn_str, ssfn_response):
        filename = self.steam_path + '/' + ssfn_str
        with open(filename, 'wb') as f:
            f.write(ssfn_response.content)

        # 保存到本地
        filename = loc_path + '/' + ssfn_str
        with open(filename, 'wb') as f:
            f.write(ssfn_response.content)
            # print(f'已成功写入文件 {filename}')

    def ssfn_download(self, ssfn_str, steam_path):
        # 因为steam路径可能会改变，不能用成员变量
        self.steam_path = steam_path

        self.ssfn_str = ssfn_str
        send_url = url + self.ssfn_str
        self.init_ssfn()

        # 判断本地库是否已经存在
        filename = loc_path + '/' + self.ssfn_str
        if os.path.exists(filename):
            shutil.copy(filename, self.steam_path)
        # 如果不存在从网上下载
        else:
            try:
                result = requests.get(send_url, headers=headers, verify=False)
                # 防止爬虫延迟获得
                # 如果没找到抛出AttributeError异常
                code = re.search(r'\?sec=\w+', result.content.decode('utf-8')).group(0)
                result.close()
                send_url = send_url + code
                ssfn_response = requests.get(send_url, headers=headers, verify=False)

            # ssfnbox未找到授权使用另一个地址
            # 一键授权逆向地址
            except AttributeError:
                try:
                    send_url = backup_url + self.ssfn_str
                    ssfn_response = requests.get(send_url, headers=headers, verify=False)
                    try:
                        # 未找到授权
                        is_404 = True if ssfn_response.content.decode('utf-8').find('Not Found') > 0 else False
                        if is_404 is True:
                            return -1
                        ssfn_response.close()
                    # 此异常代表下载到了正确文件，非“异常”，只是写法上比较简单
                    except UnicodeDecodeError:
                        pass
                except Exception as exp:
                    return exp

            self.save_file(ssfn_str, ssfn_response)
            return None

    def login(self, is_old, account, steam_path):
        subprocess.Popen('taskkill /F /IM steam.exe', creationflags=subprocess.DETACHED_PROCESS)
        # print("正在启动或者关闭steam")
        time.sleep(1)
        ssfn_ret = self.ssfn_download(account['ssfn'], steam_path)
        # 下载出错
        if ssfn_ret == -1:
            return '未找到授权！请自行将授权放到ssfn_local登录'
        # 下载异常
        elif ssfn_ret is not None:
            return ssfn_ret

        time.sleep(1)
        steam = steam_path + '/' + r"steam.exe"
        if is_old is True:
            # 老版steam
            subprocess.Popen(steam + ' -login ' + str(account['username']) + ' ' + str(account['password']))
        else:
            subprocess.Popen(
                steam + ' -windowed -bigpicture -login ' + str(account['username']) + ' ' +
                str(account['password']))
        return None
