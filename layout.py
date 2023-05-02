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
        [pSG.Text('账号')],
        [pSG.Multiline(key='-ACCOUNT-',
                       default_text=default_account,
                       size=(25, 3),
                       enable_events=True
                       )],
    ]


def create_infos_layout() -> list[list[pSG.Element]]:
    left = create_path_layout() + create_account_layout()
    right = [pSG.Multiline(key='-INFOS-', default_text='联系QQ: 1186565583', size=(45, 12),
                           enable_events=True, visible=True)]
    return [
        [pSG.Column(left), pSG.Column([right])]
    ]


table_header = ['', 'username', 'password', 'ssfn', 'steamid']
header_width = [3, 12, 12, 25, 18]
table_val = [[str(i), '', '', '', ''] for i, _ in enumerate(range(1, 11), 1)]


def create_table_layout():
    table = [pSG.Table(key='-TABLE-',
                       values= table_val,
                       headings=table_header,
                       col_widths=header_width,
                       justification='center',
                       auto_size_columns=False,
                       num_rows=10,
                       expand_x=True,
                       expand_y=True,
                       enable_click_events=True,
                       tooltip='双击登录'
                       )]
    return [
        [table]
    ]
