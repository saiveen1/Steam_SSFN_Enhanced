import threading
import PySimpleGUI as pSG

import layout
import steam_account
import vals
from steam_login import SteamLogin
from steam_account import SteamAccount


def get_window_size(window):
    size = window.TKroot.geometry()
    return size


def account_check(window, account_str: str):
    """ 更新账号区域
        涉及到api操作，第一次调用显示原有信息
        第二次网络查询，其实可以改到get_account 里面，不过懒得动了
    """
    o_acc = SteamAccount(account_str)
    window.write_event_value('-UPDATE-ACC-INFO-', o_acc)


def login_steam(o_acc: steam_account.SteamAccount, steam_path=''):
    try:
        o_steam_login = SteamLogin()
        acc_dict = o_acc.d_acc_info
        if acc_dict is None:
            pSG.popup_error('请注意账号格式！！！\n账号----密码----ssfn')
            return
        login_status = o_steam_login.login(d_acc_info=acc_dict, steam_path=steam_path)
        if login_status is not None:
            pSG.popup_error(login_status, title='文件错误')
    except Exception as exp:
        pSG.popup_error(exp, type(exp), title='未知错误 联系qq1186565583')


def show_window():
    gui_layout = [
            [pSG.Frame('', layout=layout.create_main_layout() + layout.create_account_layout())]
    ]
    window = pSG.Window('By saiveen', gui_layout, resizable=False)

    o_acc = None
    str_acc = None
    # 用以检测account 是否发生了变化避免每次点击都会进入函数
    prev_account = None

    while True:
        event, values = window.read()
        if event is None:
            break

        if event == pSG.WIN_CLOSED:
            break

        elif event == '-P_INVISIBLE-':
            steam_path = values['-P_INVISIBLE-']
            if steam_path:
                window['-PATH-'].update(steam_path)

        elif event == '-ACCOUNT-':
            str_acc = values['-ACCOUNT-']
            if str_acc != prev_account and str_acc != vals.default_account and str_acc is not None and str_acc != '':
                thread = threading.Thread(target=account_check, args=(window, str_acc))
                # 表示将创建的线程设置为守护线程。守护线程是在后台运行的线程，当主线程退出时，它会被强制结束而不会完成所有的操作。
                thread.daemon = True
                thread.start()

        # 利用线程以防api查询阻塞
        elif event == '-UPDATE-ACC-INFO-':
            o_acc = values[event]
            pSG.PopupNoTitlebar('正在启动steam客户端', auto_close=True,
                                auto_close_duration=2, button_type=5)
        elif event == vals.EVENTS.login:
            if str_acc is None:
                pSG.popup_error('请注意账号格式！！！\n账号----密码----ssfn')
                continue
            pSG.PopupNoTitlebar('正在启动steam客户端', auto_close=True,
                                auto_close_duration=2, button_type=5)
            login_steam(o_acc=o_acc, steam_path=values['-PATH-'])

    window.close()


if __name__ == '__main__':
    show_window()
