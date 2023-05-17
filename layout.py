import PySimpleGUI as pSG

from steam_login import SteamLogin

# 全局字体
pSG.set_options(font='any 16')
multiline_size = (19, 3)


def create_main_layout() -> list[list[pSG.Element]]:
    steam_path = SteamLogin.get_steam_path()
    return [
        # [pSG.Text('steam路径：')],
        [pSG.Multiline(key='-PATH-', default_text=steam_path,
                       enable_events=True, size=multiline_size, no_scrollbar=True)],
    ]


default_account = '123----456----ssfn6094777681074169870'


def create_account_layout() -> list[list[pSG.Element]]:
    return [
        # [pSG.Text('账号')],
        [pSG.InputText(key='-P_INVISIBLE-', visible=False, enable_events=True),
         pSG.FolderBrowse('  目录  ', ),
         # , expand_x=True
         pSG.Button('登录', expand_x=True),
         # FolderBrowse无法直接更改Multiline, 隐藏监听
         ],
        [pSG.Multiline(key='-ACCOUNT-',
                       default_text=default_account,
                       size=multiline_size,
                       enable_events=True,
                       no_scrollbar=True
                       )],
    ]
