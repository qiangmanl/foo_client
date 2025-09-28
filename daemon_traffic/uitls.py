
import os


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




