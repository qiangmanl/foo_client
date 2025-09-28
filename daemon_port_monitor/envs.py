import os
import sys


daemon_dir = os.getenv("daemon_dir", "")
running_port_record_path = os.path.join(daemon_dir, "ports.txt") 
running_port_handle_path = os.path.join(daemon_dir, "handle_running_port.sh") 
nft_port_handle_path = os.path.join(daemon_dir, "handle_nft_port.sh") 
nft_env_handle_path = os.path.join(daemon_dir, "handle_nft_env.sh")
env_file_path = os.path.join(daemon_dir, "client.env")
program_key = os.getenv("program_key","")

if not daemon_dir:
    print("daemon path undefind", file=sys.stderr)
    exit(1)

if not running_port_record_path:
    print("running_port_record_path is not setting in env",file=sys.stderr)
    exit(1)
else:
    if not os.path.exists(running_port_record_path):
        open(running_port_record_path, "w").close() 
        if not os.path.exists(running_port_record_path):
            print(f"can not create {running_port_record_path}", file=sys.stderr)
            exit(1)

if not os.path.exists(env_file_path):
    open(env_file_path, "w").close() 
    if not os.path.exists(env_file_path):
        print(f"can not create {env_file_path}", file=sys.stderr)
        exit(1)

if not program_key:
    print("program_key is not setting in env",file=sys.stderr)
    exit(1)

