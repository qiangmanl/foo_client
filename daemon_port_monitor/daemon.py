import os
import sys
import time
from utils import get_sys_running_ports, get_table_ports_from_file, add_port, save_ports_to_file, compare_lists_simple, del_port, check_nft_env, install_nft_env
port_record_file = os.getenv("port_record_file")
program_key = os.getenv("program_key")

def update(new_ports_list, existing_ports):
    
    if not existing_ports:
        # 如果没有已有端口，则全部添加
        success_added = []
        print(f'add ports: {new_ports_list}')
        for port in new_ports_list:
            if add_port(port):
                success_added.append(port)
        save_ports_to_file(success_added, port_record_file)
        return
    else:
        # 比较新旧端口
        ports_remove_need, ports_add_need = compare_lists_simple(existing_ports, new_ports_list)
        print(f'add ports: {ports_add_need}')
        print(f'del ports: {ports_remove_need}')
        
        # 删除已移除的端口
        for port in ports_remove_need:
            del_port(port)
            existing_ports.remove(port)

        # 添加新端口
        for port in ports_add_need:
            add_port(port)
            existing_ports.append(port)

        # 更新文件
        save_ports_to_file(existing_ports, port_record_file)

if __name__ == "__main__":
    
    if not check_nft_env():
        if install_nft_env():
            print("init nft env")
        else:
            print("init nft env failed", file=sys.stderr)
            exit(1)
    else:
        print("nft env installed earlier")
    if program_key:
        new_ports_list = get_sys_running_ports(program_key)
    table_ports = get_table_ports_from_file(port_record_file)
    if new_ports_list != table_ports:
        print("discovery new ports updated")
        update(new_ports_list, table_ports)
    else:
        print(f'{time.time()}daemon ticker')
