import steam_utils as su
import PySimpleGUI as pSG
from typing import List
# 全局字体
pSG.set_options(font='any 16')


def get_window_size(window):
    size = window.TKroot.geometry()
    return size


def create_main_layout() -> List[List[pSG.Element]]:
    steam_path = su.get_steam_path()
    return [
        [pSG.Text('steam路径：'),
         # FolderBrowse无法直接更改Multiline, 隐藏监听
         pSG.InputText(key='-P_INVISIBLE-', visible=False, enable_events=True),
         pSG.FolderBrowse()],
        [pSG.Multiline(key='-PATH-', default_text=steam_path, enable_events=True, size=(20, 3))],
    ]


def create_account_layout() -> List[List[pSG.Element]]:
    return [
        [pSG.Text('账号')],
        [pSG.Multiline(key='-ACCOUNT-',
                       default_text="123----456----ssfn6094777681074169870",
                       size=(20, 3),
                       enable_events=True
                       )],
        [pSG.Button('旧版登录', size=(10, 1)), pSG.Button('新版登录', size=(10, 1))],
    ]


def create_table_layout() -> List[List[pSG.Element]]:
    # sample_table_data = ['atsdfgty', 'wrsdftwet', 'ssfn1599340828252283245', '76561199163325654',
    #                      'GameBan']
    table_header = ['username', 'password', 'ssfn', 'steamid', 'GameBans', 'LastBan', 'OwnCsGo', 'VacBan']
    header_width = [12, 12, 25, 18, 10, 15, 10, 10]
    return [
        [pSG.Checkbox('拓展', key='-SHOW-TABLE-', default=False, enable_events=True)],
        [pSG.Table(key='-TABLE-',
                   values=[],
                   headings=table_header,
                   col_widths=header_width,
                   justification='left',
                   auto_size_columns=False,
                   num_rows=10,
                   visible=False)]
    ]


def show_window():
    layout = create_main_layout() + create_account_layout() + create_table_layout()

    # qq:1186565583
    window = pSG.Window('By saiveen', layout, resizable=True)

    # 记录变化后窗口的大小
    record_s1 = True
    default_size = None
    record_s2 = False
    with_table_size = None

    account = None
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
            account = su.parse_account(account)

            header = window['-TABLE-'].Widget.cget('columns')

            table_data = [[account.get(k, '') for k in header]]
            window['-TABLE-'].update(values=table_data, visible=True if values['-SHOW-TABLE-'] else False)

        elif event in ('旧版登录', '新版登录'):
            steam_path = values['-PATH-']
            if account is None:
                pSG.popup_error('请注意账号格式！！！\n账号----密码----ssfn')
                continue
            try:
                login_status = su.steam_login(is_old=(event == '旧版登录'),
                                              steam_path=steam_path,
                                              account=account)
                if login_status is not None:
                    pSG.popup_error(login_status, title='ssfndownload出错！')

            except Exception as exp:
                pSG.popup_error(exp, type(exp), title='Unknown error')

        elif event == '-SHOW-TABLE-':
            record_s1 = False
            # update勾选框值会直接取反
            show_table = values['-SHOW-TABLE-']
            window['-TABLE-'].update(visible=show_table)
            if show_table:
                window['-PATH-'].expand(True, True)
                window['-ACCOUNT-'].expand(True, True)
                record_s2 = True
                if with_table_size:
                    window.TKroot.geometry(with_table_size)
            else:
                window.TKroot.geometry(default_size)
                window['-PATH-'].expand(False, False)
                window['-PATH-'].Widget.config(width=20, height=3)
                window['-ACCOUNT-'].expand(False, False)
                window['-ACCOUNT-'].Widget.config(width=20, height=3)
                record_s2 = False
    window.close()


if __name__ == '__main__':
    show_window()
