import layout


def export_accounts(l_csteam_d: list[tuple[type, dict]]):
    login_info = ""
    content = ""
    for account_d in l_csteam_d:
        content = content + account_d[0].account_str + '\n'
    layout.open_multiline_window(default_text=content)
