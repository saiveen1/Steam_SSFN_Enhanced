import layout
from steam_account import SteamAccount


def export_accounts(l_csteam_d: list[SteamAccount]):
    content = ""
    for o_acc in l_csteam_d:
        content = content + o_acc.acc_str + '\n'
    layout.open_multiline_window(default_text=content)
