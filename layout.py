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
        [pSG.Multiline(key='-PATH-', default_text=steam_path, enable_events=True, size=(20, 3))],
    ]


default_account = '123----456----ssfn6094777681074169870'


def create_account_layout() -> list[list[pSG.Element]]:
    return [
        [pSG.Text('账号')],
        [pSG.Multiline(key='-ACCOUNT-',
                       default_text=default_account,
                       size=(20, 3),
                       enable_events=True
                       )],
        [pSG.Button('旧版登录', size=(10, 1)), pSG.Button('新版登录', size=(10, 1))],
    ]


def create_infos_layout() -> list[list[pSG.Element]]:
    left = create_path_layout() + create_account_layout()
    right = [pSG.Multiline(key='-INFOS-', default_text=infos_txt, size=(42, 12),
                           enable_events=True, visible=False)]
    return [
        [pSG.Column(left), pSG.Column([right])]
    ]


"""
# 一字长蛇布局
table_header = ['username', 'password', 'ssfn', 'steamid', 'GameBans', 'LastBan', 'OwnCsGo', 'VacBan']
def create_table_layout() -> list[list[pSG.Element]]:
    table = pSG.Table(key='-TABLE-', values=[], headings=table_header,
                      col_widths=header_width, justification='left', auto_size_columns=False,
                      num_rows=10, visible=False)
    return [
        [pSG.Checkbox('拓展', key='-SHOW-TABLE-', default=False, enable_events=True)],
        [table]
    ]
"""

table_header = ['username', 'password', 'ssfn', 'steamid']
header_width = [12, 12, 25, 18, 10, 15, 10, 10]
infos_txt = ''


def create_table_layout() -> list[list[pSG.Element]]:
    table = [pSG.Table(key='-TABLE-', values=[], headings=table_header,
                       col_widths=header_width, justification='left', auto_size_columns=False,
                       num_rows=10, visible=False)]
    # multiline = [pSG.Multiline(key='-INFOS-', default_text=infos_txt, size=(60, 12),
    #                            enable_events=True, visible=False)]
    return [
        [pSG.Checkbox('拓展', key='-SHOW-TABLE-', default=False, enable_events=True)],
        [table]
        # [pSG.Column([table]), pSG.Column([multiline])]
    ]
