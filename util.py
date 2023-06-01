import chardet

import layout
from SteamInfo.steam_account import SteamAccount


def detect_encoding(file_path):
    with open(file_path, 'rb') as file:
        raw_data = file.read()
        result = chardet.detect(raw_data)
        return result['encoding']


def export_accounts(l_csteam_d: list[SteamAccount]):
    content = ""
    for o_acc in l_csteam_d:
        content = content + o_acc.acc_str + '\n'
    layout.open_multiline_window(default_text=content)
