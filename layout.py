import PySimpleGUI as pSG

import vals
from steam_login import SteamLogin

# 全局字体
pSG.set_options(font='any 16')
multiline_size = (22, 4)


def create_main_layout() -> list[list[pSG.Element]]:
    steam_path = SteamLogin.get_steam_path()
    return [
        [pSG.Text('steam路径：'),
         pSG.InputText(key='-P_INVISIBLE-', visible=False, enable_events=True),
         pSG.FolderBrowse(),
         ],
        [
            pSG.Multiline(key='-PATH-', default_text=steam_path,
                          enable_events=True, size=(multiline_size[0], 3), no_scrollbar=True),
        ]
    ]


def create_account_layout() -> list[list[pSG.Element]]:
    return [
        [pSG.Text('账号 QQ:1186565583')],

        [pSG.Multiline(key='-ACCOUNT-',
                       default_text=vals.default_account,
                       size=multiline_size,
                       enable_events=True,
                       no_scrollbar=True,
                       expand_x=True
                       )],
        [
            # , expand_x=True
            pSG.Button(vals.EVENTS.login, expand_x=True, size=(0, 2)),
            # FolderBrowse无法直接更改Multiline, 隐藏监听
        ],
    ]
