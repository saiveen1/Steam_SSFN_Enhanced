import threading
import PySimpleGUI as pSG

import layout
from steam_login import SteamLogin
from steam_account import SteamAccount
steam_accs = []


def get_window_size(window):
    size = window.TKroot.geometry()
    return size


def thread_account_table(window, account_str: str, api_check):
    """ 更新账号区域
        涉及到api操作，第一次调用显示原有信息
        第二次网络查询，其实可以改到get_account 里面，不过懒得动了
    """
    lines = account_str.split('\n')
    # (对象，账户字典) steam_accs[0][1] 第一个账户的字典

    for single_acc_str in lines:
        if single_acc_str != '':
            single_acc = SteamAccount(single_acc_str)
            reslut = single_acc.get_account_info()
            # 不符合账号格式
            if reslut is None:
                reslut = {'username': '格式不正确', 'password': single_acc_str,
                          'steamid': ''}
            steam_accs.append((single_acc, reslut))
    if len(steam_accs) == 0:
        return
    table_data = []
    for single_acc in steam_accs:
        row_data = [single_acc[1].get(k, '') for k in layout.table_header]
        table_data.append(row_data)
    window.write_event_value('-UPDATE-TABLE-', (table_data, False))

    if api_check:
        # header = window['-TABLE-'].Widget.cget('columns')
        accs_info = []
        for acc in steam_accs:
            if acc[1]['steamid'] != "":
                result = acc[0].get_account_info(api_check=api_check)
                if isinstance(result, tuple):
                    if result[0] == -1:
                        window['-INFOS-'].update('steamid 输入错误！')
                    elif result[0] == -2:
                        window['-INFOS-'].update('网络错误！')
                    continue
                accs_info.append(result)

        # 返回data和API Check
        window.write_event_value('-UPDATE-TABLE-', (accs_info, True))


def login_steam(account_str=None, steam_path=''):
    try:
        steam_login = SteamLogin()
        acc_dict = SteamAccount(account_str)
        acc_dict = acc_dict.get_account_info()
        if acc_dict is None:
            pSG.popup_error('请注意账号格式！！！\n账号----密码----ssfn')
            return
        login_status = steam_login.login(account=acc_dict, steam_path=steam_path)
        if login_status is not None:
            pSG.popup_error(login_status, title='ssfndownload出错！')
    except Exception as exp:
        pSG.popup_error(exp, type(exp), title='未知错误 联系qq1186565583')


def get_acc_info(data: dict) -> (str, bool):
    num_game_bans = data['NumberOfGameBans']
    last_ban = '' if num_game_bans == 0 else '上次封禁时间: '
    line = '' if num_game_bans == 0 else '\n'
    vac_ban = '是' if data['VACBanned'] is True else '否'
    number_vac_bans = '' if vac_ban == '否' else data['NumberOfVACBans']
    pubg_total, pubg_2week, cs_total, cs_2week = [None] * 4
    for d in data['games']:
        if d['appid'] == 578080:
            pubg_total = int(d['playtime_forever'] / 60)
            pubg_2week = int(d['playtime_2weeks'] / 60) if 'playtime_2weeks' in d else 0
        if d['appid'] == 730:
            cs_total = int(d['playtime_forever'] / 60)
            cs_2week = int(d['playtime_2weeks'] / 60) if 'playtime_2weeks' in d else 0
    # pubg_total = [d['playtime_forever'] for d in data if d['appid'] == 578080][0]
    csgo = '' if cs_total is None else f"CSGO总时长: {cs_total}小时\n" \
                                       f"CSGO最近两周时长: {cs_2week}小时\n"

    multi_info = f"游戏封禁：{num_game_bans}   " \
                 f"{last_ban}{data['LastBanTime']}{line}" \
                 f"Vac封禁: {vac_ban}      " \
                 f"{'' if vac_ban == '否' else 'Vac封禁个数: '}{number_vac_bans}\n" \
                 f"共{data['game_count']}个游戏\n" \
                 f"吃鸡总时长: {pubg_total}小时\n" \
                 f"吃鸡最近两周时长: {pubg_2week}小时\n" \
                 f"{csgo}" \
                 f"额外信息: {data['extra_info']}\n" \
                 f"购买信息：{data['sale_info']}"
    danger = True if num_game_bans > 0 else False
    return multi_info, danger


def show_window():
    gui_layout = layout.create_infos_layout() + layout.create_table_layout()

    window = pSG.Window('By saiveen', gui_layout, resizable=True, finalize=True)
    # 双击事件
    window["-TABLE-"].bind('<Double-Button-1>', "+-double click-")
    table_val = layout.table_val
    acc_str = None
    # 用以检测account 是否发生了变化避免每次点击都会进入函数
    prev_account = None
    accs_info_list = []

    while True:
        event, values = window.read()
        # print(event, values['-TABLE-'])
        if event is None:
            break

        if event == pSG.WIN_CLOSED:
            break

        elif event == '-P_INVISIBLE-':
            steam_path = values['-P_INVISIBLE-']
            if steam_path:
                window['-PATH-'].update(steam_path)

        elif event == '-ACCOUNT-':
            acc_str = values['-ACCOUNT-']
            if acc_str != prev_account and acc_str != layout.default_account and acc_str is not None and acc_str != '':
                thread = threading.Thread(target=thread_account_table, args=(window, acc_str, True))
                # 表示将创建的线程设置为守护线程。守护线程是在后台运行的线程，当主线程退出时，它会被强制结束而不会完成所有的操作。
                thread.daemon = True
                thread.start()

        # 利用线程以防api查询阻塞
        # 两次事件
        elif event == '-UPDATE-TABLE-':
            data, api = values[event]
            if api is False:
                for i in range(len(data)):
                    table_val[i][1:] = data[i][1:]
                window['-TABLE-'].update(values=table_val)
            else:
                if len(data) > 0:
                    for i in range(len(data)):
                        info, danger = get_acc_info(data[i])
                        accs_info_list.append((info, danger))
                        if danger:
                            window['-TABLE-'].update(row_colors=[(i, 'white', 'red')])
                        else:
                            window['-TABLE-'].update(row_colors=[(i, 'black', 'white')])
                    # 默认显示第一个
                    window['-INFOS-'].update(accs_info_list[0][0])

        # 鼠标双击，需要window 处绑定事件
        elif event == '-TABLE-+-double click-':
            pos = window['-TABLE-'].get_last_clicked_position()
            selected_acc_str = steam_accs[pos[0]][0].account_str
            # 这里不能使用acc_str，那是单个账号情况
            pSG.PopupNoTitlebar('正在启动steam客户端', auto_close=True,
                                auto_close_duration=2, button_type=5)
            login_steam(account_str=selected_acc_str, steam_path=values['-PATH-'])
        # 鼠标单机事件
        if isinstance(event, tuple):
            if event[0] == '-TABLE-':
                row = event[2][0]
                # col = event[2][1]
                try:
                    window['-INFOS-'].update(accs_info_list[row][0])
                except IndexError:
                    # 还没获取到api信息
                    pass
    window.close()


if __name__ == '__main__':
    show_window()
