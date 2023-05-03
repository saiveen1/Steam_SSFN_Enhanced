import PySimpleGUI as pSG

from steam_login import SteamLogin

# 全局字体
pSG.set_options(font='any 16')


def create_path_layout() -> list[list[pSG.Element]]:
    steam_path = SteamLogin.get_steam_path()
    return [
        [pSG.Text('steam路径：'),
         # FolderBrowse无法直接更改Multiline, 隐藏监听
         pSG.InputText(key='-P_INVISIBLE-', visible=False, enable_events=True),
         pSG.FolderBrowse()],
        [pSG.Multiline(key='-PATH-', default_text=steam_path, enable_events=True, size=(25, 3))],
    ]


default_account = '123----456----ssfn6094777681074169870'


def create_account_layout() -> list[list[pSG.Element]]:
    return [
        [pSG.Text('账号(支持多行复制)，右键登录')],
        [pSG.Multiline(key='-ACCOUNT-',
                       default_text=default_account,
                       size=(25, 3),
                       enable_events=True
                       )],
        [pSG.Button('导出账号信息', size=(15, 1))]
    ]


def create_infos_layout() -> list[list[pSG.Element]]:
    left = create_path_layout() + create_account_layout()
    right = [pSG.Multiline(key='-INFOS-', default_text='联系QQ: 1186565583', size=(54, 12),
                           enable_events=True, visible=True)]
    return [
        [pSG.Column(left), pSG.Column([right])]
    ]


table_header = ['', 'remark', 'username', 'password', 'ssfn', 'steamid']
header_width = [3, 9, 12, 12, 25, 18]


def init_table_val():
    return [[str(i), '', '', '', '', ""] for i, _ in enumerate(range(1, 50), 1)]


def create_table_layout():
    table = [pSG.Table(key='-TABLE-',
                       values=init_table_val(),
                       headings=table_header,
                       col_widths=header_width,
                       justification='center',
                       auto_size_columns=False,
                       right_click_selects=True,
                       vertical_scroll_only=True,
                       num_rows=10,
                       expand_x=True,
                       expand_y=True,
                       enable_click_events=True,
                       right_click_menu=['&Right', ['登录']],
                       tooltip='双击修改'
                       )]
    return [
        [table]
    ]


def open_multiline_window(default_text=''):
    layout = [[pSG.Multiline(default_text=default_text, size=(50, 10))],
              [pSG.Button('OK'), pSG.Button('Cancel')]]

    window = pSG.Window('修改账号信息', layout)

    while True:
        event, values = window.read()
        if event in (pSG.WIN_CLOSED, 'Cancel'):
            text = None
            break
        elif event == 'OK':
            text = values[0]  # 获取多行文本框中的文本
            break

    window.close()
    return text


