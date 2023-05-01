import threading
import PySimpleGUI as pSG

import layout
from steam_login import SteamLogin
from steam_account import SteamAccount


def get_window_size(window):
    size = window.TKroot.geometry()
    return size


def thread_account_table(window, account_str: str, show_table: bool):
    """ 更新账号区域
        涉及到api操作，第一次调用显示原有信息
        第二次网络查询，其实可以改到get_account 里面，不过懒得动了
    """
    steam_acc = SteamAccount(account_str)
    result = steam_acc.get_account_info(api_check=False)
    if result is None:
        return
    table_data = [[result.get(k, '') for k in layout.table_header]]
    window.write_event_value('-UPDATE-TABLE-', (table_data, show_table))
    if isinstance(account_str, tuple):
        pSG.popup_error(account_str[1])
        return
    # header = window['-TABLE-'].Widget.cget('columns')
    result = steam_acc.get_account_info(api_check=True)
    table_data = [[result.get(k, '') for k in layout.table_header]]
    window.write_event_value('-UPDATE-TABLE-', (table_data, show_table))


def login_steam(account, is_old):
    try:
        steam_login = SteamLogin()
        login_status = steam_login.login(is_old=is_old, account=account)
        if login_status is not None:
            pSG.popup_error(login_status, title='ssfndownload出错！')
    except Exception as exp:
        pSG.popup_error(exp, type(exp), title='Unknown error')


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
                """
                如果没勾选拓展则不查询消息
                account = su.get_account(account, show_table)

                with concurrent.futures.ThreadPoolExecutor() as executor:
                    # 使用线程池进行API查询
                    future = executor.submit(su.get_account, account, show_table)
                    future.add_done_callback(lambda f: update_table(f, window, show_table))
                    prev_account = account
                """
                thread = threading.Thread(target=thread_account_table, args=(window, account, show_table))
                # 表示将创建的线程设置为守护线程。守护线程是在后台运行的线程，当主线程退出时，它会被强制结束而不会完成所有的操作。
                thread.daemon = True
                thread.start()

        # 利用线程以防api查询阻塞
        elif event == '-UPDATE-TABLE-':
            table_data, visible = values[event]
            window['-TABLE-'].update(values=table_data, visible=visible)

        elif event in ('旧版登录', '新版登录'):
            if account is None:
                pSG.popup_error('请注意账号格式！！！\n账号----密码----ssfn')
                continue
            login_steam(account=account, is_old=(event == '旧版登录'))

        elif event == '-SHOW-TABLE-':
            record_s1, record_s2 = handle_show_table(values, window, with_table_size, default_size)
    window.close()


if __name__ == '__main__':
    show_window()
