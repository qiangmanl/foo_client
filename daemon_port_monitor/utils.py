import subprocess
import os
import sys

daemon_dir = os.getenv("daemon_dir", "")

if not daemon_dir:
    print("daemon unknow", file=sys.stderr)
    exit(1)

get_port_sh_path = os.path.join(daemon_dir, "get_sys_running_port.sh") 
op_port_sh_path = os.path.join(daemon_dir, "op_port.sh") 
nft_env_sh_path = os.path.join(daemon_dir, "nft_env.sh")

def get_sys_running_ports(key:str):
    result = subprocess.check_output([get_port_sh_path, f"{key}"], text=True)
    ports = result.strip().split()
    return ports

def get_table_ports_from_file(port_record_file):
    """
    从文件中读取列表，每行一个元素。
    如果文件不存在或为空，返回空列表。
    """
    if not os.path.exists(port_record_file):
        return []
    with open(port_record_file, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]
    return lines


def add_port(port :str)-> bool:
    result = subprocess.run([op_port_sh_path, "add", port], capture_output=True, text=True)
    if result.returncode == 0:
        return True
    return False


def compare_lists_simple(list1, list2):
    """
    比较两个列表，返回只在 list1 里和只在 list2 里的元素集合
    """
    set1, set2 = set(list1), set(list2)
    return list(set1 - set2), list(set2 - set1)

def save_ports_to_file(port_list, filename):
    """将端口列表保存到文件"""
    with open(filename, 'w', encoding='utf-8') as f:
        for port in port_list:
            f.write(f"{port}\n")


def del_port(port :str)-> bool:
    result = subprocess.run( \
        [op_port_sh_path, "del", port], \
          capture_output=True, text=True)
    if result.returncode == 0:
        return True
    return False


def check_nft_env()-> bool:
    
    # print(os.path.join(os.getenv("daemon_dir"),"nft_env.sh"))
    result = subprocess.run(\
        [nft_env_sh_path, "check"],\
              capture_output=True, text=True)
    if result.returncode == 0:
        return True
    else:
        return False

def install_nft_env()-> bool:
    result = subprocess.run(\
        [nft_env_sh_path, "install"], \
            capture_output=True, text=True)
    if result.returncode == 0:
        return True
    return False


def save_env(key: str, value: str):

    """
    
    """
  
    env_file_path = os.getenv("env_file_path", os.path.join(os.getcwd(), "client.env"))
    lines = []
    if not os.path.exists(env_file_path):
        open(env_file_path, "w").close() 
    
    with open(env_file_path, "r") as f:
        lines = f.readlines()
    for line in lines:
        if line.strip().startswith(f"{key}="):
            value = line.strip().split("=", 1)[1]
            break
    with open(env_file_path, "a") as f:
        f.write(f"{key}={value}\n")

