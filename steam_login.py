import os
import re
import shutil
import subprocess
import time

import requests
import winreg

import values


class SteamLogin:
    def __init__(self, steam_path=None):
        self.steam_path = None
        self.ssfn_str = None
        self.current_path = None

    @staticmethod
    def get_steam_path():
        # 注册表获取steam路径
        key = winreg.OpenKeyEx(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Valve\Steam")
        return winreg.QueryValueEx(key, 'SteamPath')[0]

    def init_ssfn(self):
        # 创建本地ssfn库
        if not os.path.exists(values.loc_path):
            os.makedirs(values.loc_path)

        # 删除steam目录下的ssfn文件
        for filename in os.listdir(self.steam_path):
            if re.match(r'ssfn.*', filename):
                os.remove(os.path.join(self.steam_path, filename))

    def save_ssfn_file(self, ssfn_str, ssfn_response):
        filename = self.steam_path + '/' + ssfn_str
        with open(filename, 'wb') as f:
            f.write(ssfn_response.content)

        # 保存到本地
        filename = values.loc_path + '/' + ssfn_str
        with open(filename, 'wb') as f:
            f.write(ssfn_response.content)
            # print(f'已成功写入文件 {filename}')

    def ssfn_download(self, ssfn_str, steam_path):
        # 因为steam路径可能会改变，不能用成员变量
        self.steam_path = steam_path

        self.ssfn_str = ssfn_str
        send_url = values.ssfnbox_url + self.ssfn_str
        self.init_ssfn()

        # 判断本地库是否已经存在
        filename = values.loc_path + '/' + self.ssfn_str
        ssfn_response = None
        l_status = []
        try:
            if os.path.exists(filename):
                shutil.copy(filename, self.steam_path)
        except PermissionError:
            return values.ERRORS.WRITE_PERMISSION_ERROR
        # 如果不存在从网上下载
        else:
            try:
                result = requests.get(send_url, headers=values.headers, verify=False)
                # 防止爬虫延迟获得
                # 如果没找到抛出AttributeError异常
                code = re.search(r'\?sec=\w+', result.content.decode('utf-8')).group(0)
                result.close()
                send_url = send_url + code
                ssfn_response = requests.get(send_url, headers=values.headers, verify=False)
                self.save_ssfn_file(ssfn_str, ssfn_response)
            # ssfnbox未找到授权使用另一个地址
            # 一键授权逆向地址
            except AttributeError:
                for url in values.l_backup_urls:
                    send_url = url + self.ssfn_str
                    try:
                        ssfn_response = requests.get(send_url, headers=values.headers, verify=False)
                        # 连接超时
                        if ssfn_response.status_code == 502:
                            l_status.append(values.ERRORS.SSFNError.SSFN_DOWNLOAD_ERROR)
                            continue
                        try:
                            # 未找到授权
                            is_404 = True if ssfn_response.content.decode('utf-8').find('Not Found') > 0 else False
                            if is_404 is True:
                                l_status.append(values.ERRORS.STEAM_NOT_FOUND_ERROR)
                                continue
                        # 此异常代表下载到了正确文件，非“异常”，只是写法上比较简单
                        except UnicodeDecodeError:
                            self.save_ssfn_file(ssfn_str, ssfn_response)
                            break
                    except requests.exceptions.SSLError:
                        l_status.append(values.ERRORS.SSFNError.NET_SSL_ERROR)
                        continue
                    except Exception as exp:
                        return exp

            ssfn_response.close()
            # 只返回最后一个备用网址的状态
            return None if len(l_status) == 0 else l_status[len(l_status) - 1]

    # 虽然self 里有参数path，但是前端path可能会改变，所以还是需要传递一个参数
    def login(self, d_acc_info, steam_path):
        self.steam_path = steam_path

        # # 检查sys.check 是否为True以确定是否经过了pyinstaller 打包
        # if getattr(sys, 'frozen', False):
        #     self.current_path = os.path.abspath(sys.executable)
        # else:
        #     self.current_path = os.getcwd()
        self.current_path = os.getcwd()

        subprocess.Popen('taskkill /F /IM steam.exe', creationflags=subprocess.DETACHED_PROCESS)
        time.sleep(1)
        ssfn_ret = self.ssfn_download(d_acc_info['ssfn'], self.steam_path)
        # 下载出错

        if ssfn_ret == values.ERRORS.WRITE_PERMISSION_ERROR:
            return 'ssfn写入失败，请以管理员启动！'
        elif ssfn_ret in vars(values.ERRORS.SSFNError).values() and ssfn_ret is not None:
            p = os.path.normpath(os.path.join(self.current_path, values.loc_path))
            subprocess.Popen(f'explorer {p}')
            t = '' if ssfn_ret == values.ERRORS.SSFNError.SSFN_NOT_FOUND else '备用网站连接超时，'
            return t + '未找到授权！\n请自行将授权放到ssfn_local登录'
        # 其他异常
        elif ssfn_ret is not None:
            return ssfn_ret

        time.sleep(1)

        is_old = True if os.path.exists(self.steam_path + '/' + r"steam.cfg") else False

        steam_exe = self.steam_path + '/' + r"steam.exe"
        try:
            if is_old is True:
                # 老版steam
                subprocess.Popen(steam_exe + ' -login ' + str(d_acc_info['username']) + ' ' + str(d_acc_info['password']))
            else:
                subprocess.Popen(
                    steam_exe + ' -windowed -bigpicture -login ' + str(d_acc_info['username']) + ' ' +
                    str(d_acc_info['password']))
        except FileNotFoundError:
            subprocess.Popen(f'explorer {os.path.normpath(self.steam_path)}')
            return 'steam.exe未找到，请确认路径或命名是否正确！'
