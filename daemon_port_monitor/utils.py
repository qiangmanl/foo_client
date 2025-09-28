import subprocess
import os
import sys
from envs import (
    running_port_record_path, 
    nft_port_handle_path, 
    env_file_path,
    running_port_handle_path,
    nft_env_handle_path,
    program_key
)

def check_nft_env()-> bool:
    
    result = subprocess.run(\
        [nft_env_handle_path, "check"],\
              capture_output=True, text=True)
    if result.returncode == 0:
        return True
    else:
        return False
    
def install_nft_env()-> bool:
    result = subprocess.run(\
        [nft_env_handle_path, "install"], \
            capture_output=True, text=True)
    if result.returncode == 0:
        return True
    return False

def get_running_port_record():
    """
    """
    if not os.path.exists(running_port_record_path):
        print("need ports record but no prepare", file=sys.stderr)
        exit(1)
    with open(running_port_record_path, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]
    return lines

def get_sys_running_ports():
    result = subprocess.check_output([running_port_handle_path, f"{program_key}"], text=True)
    ports = result.strip().split()
    return ports

def compare_ports_simple(record_ports, current_ports):
    """
    """
    set1, set2 = set(record_ports), set(current_ports)
    return list(set1 - set2), list(set2 - set1)

def save_ports_to_record(port_list):
    """将端口列表保存到文件"""
    with open(running_port_record_path, 'w', encoding='utf-8') as f:
        for port in port_list:
            f.write(f"{port}\n")

def nft_table_add_port(port :str)-> bool:
    result = subprocess.run([nft_port_handle_path, "add", port], capture_output=True, text=True)
    if result.returncode == 0:
        return True
    return False


def nft_table_del_port(port :str)-> bool:
    result = subprocess.run( \
        [nft_port_handle_path, "del", port], \
          capture_output=True, text=True)
    if result.returncode == 0:
        return True
    return False

def save_env_hot(key: str, value: str):

    """
    
    """
    with open(env_file_path, "r") as f:
        lines = f.readlines()
    for line in lines:
        if line.strip().startswith(f"{key}="):
            value = line.strip().split("=", 1)[1]
            break
    with open(env_file_path, "a") as f:
        f.write(f"{key}={value}\n")

