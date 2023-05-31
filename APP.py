import threading
import PySimpleGUI as pSG

import layout
import steam_account
import util
from steam_login import SteamLogin
from steam_account import SteamAccount
import values

l_csteam_d = []


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
            o_acc = SteamAccount(single_acc_str)
            l_csteam_d.append(o_acc)
    if len(l_csteam_d) == 0:
        return
    table_data = []
    for o_acc in l_csteam_d:
        if o_acc.d_acc_info is None:
            row_data = ['', '', '', '格式不正确']
        else:
            row_data = [o_acc.d_acc_info.get(k, '') for k in layout.table_header]
        table_data.append(row_data)
    window.write_event_value('-UPDATE-TABLE-', (table_data, False))

    if api_check:
        # header = window['-TABLE-'].Widget.cget('columns')
        accs_info = []
        result = None
        for o_acc in l_csteam_d:
            if o_acc.d_acc_info is None:
                result = o_acc.str_acc
            elif o_acc.d_acc_info['steamid'] != "":
                result = o_acc.get_account_info(api_check=api_check)
                if isinstance(result, tuple):
                    if result[0] == -1:
                        window['-INFOS-'].update('steamid 输入错误！')
                    elif result[0] in [-2, -3]:
                        window['-INFOS-'].update('网络错误！信息查询不可用！\n检查代理，加速等，重新打开软件')
                        continue
            accs_info.append(result)

        # 返回data和API Check
        window.write_event_value('-UPDATE-TABLE-', (accs_info, True))


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


def mark_danger_acc(window, danger_row: list, ok_row):
    for i in danger_row:
        window['-TABLE-'].update(row_colors=[(i, 'white', 'red')])
        # window['-TABLE-'].update(row_colors=[(i, 'black', 'white')])
    for i in ok_row:
        window['-TABLE-'].update(row_colors=[(i, 'black', 'white')])


def show_window():
    gui_layout = layout.create_infos_layout() + layout.create_table_layout()

    window = pSG.Window('By saiveen', gui_layout, resizable=True, finalize=True)
    # 双击事件
    window["-TABLE-"].bind('<Double-Button-1>', "+-double click-")

    table_val = layout.init_table_val()

    # 用以检测account 是否发生了变化避免每次点击都会进入函数
    prev_account = None
    l_api_info = []
    danger_row = []
    ok_row = []

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
            acc_str = values['-ACCOUNT-']
            if acc_str != prev_account and acc_str != layout.default_account and acc_str is not None and acc_str != '':
                # 账号区变动，初始化
                l_csteam_d.clear()
                table_val = layout.init_table_val()
                danger_row.clear()
                ok_row.clear()
                l_api_info.clear()
                window['-TABLE-'].update(values=table_val)

                prev_account = acc_str
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
                    print(i)
                    table_val[i][1:] = data[i][1:]
                window['-TABLE-'].update(values=table_val)
            else:
                if len(data) > 0:
                    for i in range(len(data)):
                        multi_info = get_multi_info(data[i])
                        l_api_info.append(multi_info)
                        for j in range(len(l_csteam_d)):
                            if l_csteam_d[j].is_danger is True:
                                danger_row.append(j)
                            else:
                                ok_row.append(j)

                    mark_danger_acc(window, danger_row, ok_row)
                    # 默认显示第一个
                    window['-INFOS-'].update(l_api_info[0])

        elif event == '导出账号信息':
            util.export_accounts(l_csteam_d)

        # 鼠标双击，需要window 处绑定事件
        elif event == '-TABLE-+-double click-':
            pos = window['-TABLE-'].get_last_clicked_position()
            index = pos[0]
            if index < 0 or index >= len(l_csteam_d):
                continue
            else:
                selected_acc_str = l_csteam_d[pos[0]].acc_str
            # 在主进程中调用函数，等待用户输入完成
            text = layout.open_multiline_window(default_text=selected_acc_str)
            if text is not None:
                l_csteam_d[index].str_acc = text
                l_csteam_d[index].get_account_info(api_check=False)
                new_row = [l_csteam_d[index].d_acc_info.get(k, '') for k in layout.table_header]
                table_val[index][1:] = new_row[1:]
                window['-TABLE-'].update(values=table_val)
                mark_danger_acc(window, danger_row, ok_row)

        elif event == '登录':
            pos = window['-TABLE-'].get_last_clicked_position()
            pSG.PopupNoTitlebar('正在启动steam客户端', auto_close=True,
                                auto_close_duration=2, button_type=5)
            login_steam(o_acc=l_csteam_d[pos[0]], steam_path=values['-PATH-'])
        # 鼠标单机事件
        if isinstance(event, tuple):
            if event[0] == '-TABLE-':
                row = event[2][0]
                # col = event[2][1]
                try:
                    # 表头
                    if row != -1:
                        window['-INFOS-'].update(l_api_info[row])
                except IndexError:  # 还没获取到api信息
                    pass
                except TypeError:  # 格式错误的账号
                    pass
    window.close()


if __name__ == '__main__':
    show_window()
