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


#check install nft
if not check_nft_env():
    if install_nft_env():
        print("init nft env")
    else:
        print("init nft env failed", file=sys.stderr)
        exit(1)
else:
    print("nft env installed earlier")

current_ports = get_sys_running_ports()
record_ports = get_running_port_record()

if os.getenv("check"):
    print(f"currentports:{current_ports}")

def update(current_ports:list, record_ports:list):
    
    if not record_ports:
        # 如果没有已有端口，则全部添加
        success_added = []
        print(f'add ports: {current_ports}')
        for port in current_ports:
            if nft_table_add_port(port):
                success_added.append(port)
        save_ports_to_record(success_added)
        return

    ports_remove_need, ports_add_need = compare_ports_simple(record_ports, current_ports)
    print(f'add ports: {ports_add_need}')
    print(f'del ports: {ports_remove_need}')
    
    # 删除已移除的端口
    for port in ports_remove_need:
        nft_table_del_port(port)
        record_ports.remove(port)

    # 添加新端口
    for port in ports_add_need:
        nft_table_add_port(port)
        record_ports.append(port)

    # 更新文件
    save_ports_to_record(record_ports)




