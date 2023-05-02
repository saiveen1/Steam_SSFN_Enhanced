import threading
import PySimpleGUI as pSG

import layout
from steam_login import SteamLogin
from steam_account import SteamAccount


def get_window_size(window):
    size = window.TKroot.geometry()
    return size


def thread_account_table(window, account_str: str, api_check):
    """ 更新账号区域
        涉及到api操作，第一次调用显示原有信息
        第二次网络查询，其实可以改到get_account 里面，不过懒得动了
    """
    steam_acc = SteamAccount(account_str)

    # 第一次查询不要使用api，直接更新账户信息
    result = steam_acc.get_account_info(api_check=False)
    if result is None:
        return
    table_data = [[result.get(k, '') for k in layout.table_header]]
    window.write_event_value('-UPDATE-TABLE-', (table_data, False))

    if api_check and result['steamid'] != '':
        # header = window['-TABLE-'].Widget.cget('columns')
        result = steam_acc.get_account_info(api_check=api_check)
        window.write_event_value('-UPDATE-TABLE-', (result, True))


def login_steam(account_str, is_old, steam_path):
    try:
        steam_login = SteamLogin()
        account = SteamAccount(account_str)
        account = account.get_account_info()
        if account is None:
            return -1
        login_status = steam_login.login(is_old=is_old, account=account, steam_path=steam_path)
        if login_status is not None:
            pSG.popup_error(login_status, title='ssfndownload出错！')
    except Exception as exp:
        pSG.popup_error(exp, type(exp), title='未知错误 联系qq1186565583')


def handle_show_table(values, window, with_table_size, default_size):
    record_s1 = False
    # update勾选框值会直接取反
    show_table = values['-SHOW-TABLE-']
    window['-TABLE-'].update(visible=show_table)
    window['-INFOS-'].update(visible=show_table)
    if show_table:
        # window['-PATH-'].expand(True, True)
        # window['-ACCOUNT-'].expand(True, True)
        # window['-INFOS-'].expand(True, True)
        record_s2 = True
        if with_table_size:
            window.TKroot.geometry(with_table_size)
    else:
        window.TKroot.geometry(default_size)
        # window['-INFOS-'].expand(False, False)
        # window['-INFOS-'].Widget.config(width=20, height=12)
        record_s2 = False
    return record_s1, record_s2


def show_window():
    gui_layout = layout.create_infos_layout() + layout.create_table_layout()

    # qq:1186565583
    window = pSG.Window('By saiveen', gui_layout, resizable=True)

    # 记录变化后窗口的大小
    record_s1 = True
    default_size = None
    record_s2 = False
    with_table_size = None

    account = None
    # 用以检测account 是否发生了变化避免每次点击都会进入函数
    prev_account = None

    while True:
        event, values = window.read()
        print(event, values['-TABLE-'])
        if event is None:
            break

        if record_s1:
            default_size = get_window_size(window)
        if record_s2:
            with_table_size = get_window_size(window)

        if event == pSG.WIN_CLOSED:
            break

        elif event == '-P_INVISIBLE-':
            steam_path = values['-P_INVISIBLE-']
            if steam_path:
                window['-PATH-'].update(steam_path)

        elif event == '-ACCOUNT-':
            account = values['-ACCOUNT-']
            if account != prev_account and account != layout.default_account and account is not None and account != '':
                show_table = values['-SHOW-TABLE-']

                thread = threading.Thread(target=thread_account_table, args=(window, account, show_table))
                # 表示将创建的线程设置为守护线程。守护线程是在后台运行的线程，当主线程退出时，它会被强制结束而不会完成所有的操作。
                thread.daemon = True
                thread.start()

        # 利用线程以防api查询阻塞
        elif event == '-UPDATE-TABLE-':
            data, api = values[event]
            if isinstance(data, tuple):
                if data[0] == -1:
                    window['-INFOS-'].update('steamid 输入错误！')
                elif data[0] == -2:
                    window['-INFOS-'].update('网络错误！')
                continue
            if api is False or data['steamid'] == '':
                window['-TABLE-'].update(values=data)
            else:
                num_game_bans = data['NumberOfGameBans']
                last_ban = '' if num_game_bans == 0 else '上次封禁时间: '
                line = '' if num_game_bans == 0 else '\n'
                vac_ban = '是' if data['VACBanned'] is True else '否'
                number_vac_bans = '' if vac_ban == '否' else data['NumberOfVACBans']
                pubg_total, pubg_2week = [None] * 2
                for d in data['games']:
                    if d['appid'] == 578080:
                        pubg_total = d['playtime_forever']
                        pubg_2week = d['playtime_2weeks']
                # pubg_total = [d['playtime_forever'] for d in data if d['appid'] == 578080][0]
                data = f"游戏封禁：{num_game_bans}\n" \
                       f"{last_ban}{data['LastBanTime']}{line}" \
                       f"Vac封禁: {vac_ban}\n" \
                       f"{'' if vac_ban == '否' else 'Vac封禁个数: '}{number_vac_bans}\n" \
                       f"共{data['game_count']}个游戏\n" \
                       f"吃鸡总时长: {pubg_total}小时\n" \
                       f"吃鸡最近两周时长: {pubg_2week}小时"
                window['-INFOS-'].update(data)
                # window['-TABLE-'].update(row_colors=(0, 'white', 'red'))

        elif event in ('旧版登录', '新版登录'):
            result = login_steam(account_str=account, is_old=(event == '旧版登录'), steam_path=values['-PATH-'])
            if result == -1:
                pSG.popup_error('请注意账号格式！！！\n账号----密码----ssfn')
                continue

        elif event == '-SHOW-TABLE-':
            record_s1, record_s2 = handle_show_table(values, window, with_table_size, default_size)
    window.close()


if __name__ == '__main__':
    show_window()
