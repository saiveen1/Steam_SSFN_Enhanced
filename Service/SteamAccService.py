import concurrent
import threading
import time

import util
import os

from SteamInfo.DBManager import DBManager
from SteamInfo.steam_account import SteamAccount
from concurrent.futures import ThreadPoolExecutor

acc_count = 0
thread_pool_num = 4
db_manager = DBManager("../accounts.db")
out_lines = []
lock = threading.Lock()


def insert_account(str_acc, db_path=None):
    global acc_count
    acc = SteamAccount(str_acc, api_check=False)
    if acc.is_acc is False:
        return

    # 是否重复
    with lock:
        data = db_manager.select_data("accounts", f'''username="{acc.d_acc_info['username']}"''')
    if len(data) != 0:
        return
    acc.check_api_info()
    if acc.api_net_state == 429:
        return acc.api_net_state

    with lock:
        db_manager.insert_data("accounts", acc.d_acc_info)
        acc_count += 1
        print(f"当前正处理第{acc_count}个账号：{acc.d_acc_info['username']}")


def insert_accounts_from_file(src_file_path: str, db_path=None):
    encoding = util.detect_encoding(src_file_path)
    with open(src_file_path, 'r', encoding=encoding) as file_in:
        with concurrent.futures.ThreadPoolExecutor(max_workers=thread_pool_num) as executor:
            futures = []
            for line in file_in:
                line = line.strip()  # 去除首尾空白字符
                if line:  # 检查是否为空行
                    future = executor.submit(insert_account, line, db_path)
                    futures.append(future)

            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result:
                    if result == 429:
                        print("请求过快！查询终止，降低频率后再试！")
                        os._exit(-1)


def main():
    file_dir = r'E:\Document\账号\\'
    file_name = r'\20230613.txt'
    input_file = os.path.normpath(os.path.join(file_dir + file_name))

    db
    insert_accounts_from_file(input_file, r"")

    output_file = os.path.normpath(os.path.join(file_dir + file_name + '.out'))

    with open(output_file, 'w') as file_out:
        file_out.write("完成")


if __name__ == '__main__':
    start_time = time.time()
    main()
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"程序执行时间：{execution_time}秒")
