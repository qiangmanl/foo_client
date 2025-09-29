import os
import sys
from utils import (
    check_nft_env,
    compare_ports_simple,
    get_running_port_record, 
    get_sys_running_ports, 
    install_nft_env, 
    nft_table_add_port,
    nft_table_del_port, 
    save_ports_to_record
)
check_mode = os.getenv("check")

if check_mode:
    print("checking...")
#check install nft
if not check_nft_env():
    if install_nft_env():
        print("init nft env")
    else:
        print("init nft env failed", file=sys.stderr)
        exit(1)
else:
    print("nft env installed earlier")


def update(current_ports:list, record_ports:list):
    
    if not record_ports:
        # 如果没有已有端口，则全部添加
        success_added = []
        for port in current_ports:
            if nft_table_add_port(port):
                success_added.append(port)
        save_ports_to_record(success_added)

    ports_remove_need, ports_add_need  = compare_ports_simple(record_ports, current_ports)
    if check_mode:
        print(f"compare_ports_simple:nft_need_add{ports_add_need},\
                nft need remove:{ports_remove_need}")
    
    # 删除已移除的端口
    for port in ports_remove_need:
        nft_table_del_port(port)
        if check_mode:
            print(f"del table port:{port}")
        record_ports.remove(port)

    # 添加新端口
    for port in ports_add_need:
        nft_table_add_port(port)
        record_ports.append(port)
        if check_mode:
            print(f"add table port:{port}")

    # 更新文件
    save_ports_to_record(record_ports)





if __name__ == "__main__":

    current_ports = get_sys_running_ports()
    record_ports = get_running_port_record()

    if check_mode:
        print(f"currentports:{current_ports}")
        print(f"recordports:{record_ports}")
    update(current_ports, record_ports)