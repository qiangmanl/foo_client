#!/usr/bin/env python3

import os
import subprocess
import json
import sys
import requests
from uitls import save_env
from pydantic import BaseModel
from typing import List

class PortTraffic(BaseModel):
    port: str
    in_bytes: int
    out_bytes: int
    counts: int

class ClientTraffic(BaseModel):
    client_id: str
    ip: str
    ports: List[PortTraffic]
    
# ---------------- ENV ----------------
table_family = os.getenv("inet", "inet")
table_name = os.getenv("traffic_stats", "traffic_stats")
ip = os.getenv("ipaddr","")
client_id = os.getenv("client_id","")
broker_url = os.getenv("broker_url","")
count_path = os.getenv("traffic_count_path","") 
count: int = 0


# ---------------- UTIL ----------------
def get_myif():
    """获取公网 IP"""
    try:
        result = subprocess.run(
            ["curl","-4", "-s", "ifconfig.me"],
            capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print("获取公网 IP 失败:", e, file=sys.stderr)
        return None

if not count_path:
    print("no traffic count path",file=sys.stderr)
    exit(1)

# ---------------- INIT ----------------
if not broker_url:
    print("broker_url not defined", file=sys.stderr)
    sys.exit(1)

if not ip:
    ip = get_myif()
    if ip:
        save_env("ip", ip)
    else:
        print("can fetch to define ip", file=sys.stderr)
        sys.exit(1)

if not client_id:
    client_id = ip

if os.path.exists(count_path):
    try:
        with open(count_path, "r") as f:
            count = int(f.read())
    except ValueError:
        print("read count failed", file=sys.stderr)
        count = 0

# ---------------- NFT COUNTERS ----------------
def get_counters():
    try:
        result = subprocess.run(
            ["sudo", "nft", "-j", "list", "counters", "table", table_family, table_name],
            capture_output=True, text=True, check=True
        )
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error listing counters: {e.stderr}", file=sys.stderr)
        return {}

def reset_counters():
    try:
        subprocess.run(
            ["sudo", "nft", "reset", "counters", "table", table_family, table_name],
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Error resetting counters: {e.stderr}", file=sys.stderr)

def get_nft_counter():
    counters = get_counters()
    if counters:
        data = counters.get("nftables", [])
        if data and "metainfo" in data[0]:
            return data[1:]  # 去掉 meta
    return None

# ---------------- PAYLOAD ----------------
def get_payload(raw_traffic, ip, client_id):
    traffic = [c['counter'] for c in raw_traffic]
    ports_map = {}
    for raw in traffic:
        direction, port = raw['name'].split('_')
        if port not in ports_map:
            ports_map[port] = {"in_bytes": 0, "out_bytes": 0, "counts": count}

        if direction == 's':
            ports_map[port]["in_bytes"] = raw['bytes']
        elif direction == 'd':
            ports_map[port]["out_bytes"] = raw['bytes']

        ports_map[port]["counts"] = count

    ports = [PortTraffic(port=p, **v) for p, v in ports_map.items()]
    client = ClientTraffic(client_id=client_id, ip=ip, ports=ports)
    return client.model_dump()

def increment_count():
    global count
    count += 1
    if count_path:
        try:
            with open(count_path, "w") as f:
                f.write(str(count))
        except Exception as e:
            print(f"count failed: {e}", file=sys.stderr)

import time
# ---------------- MAIN ----------------
def main():
    try:
        raw_traffic = get_nft_counter()
        if raw_traffic and broker_url:
            payload = get_payload(raw_traffic, ip, client_id)
            reset_counters()
            increment_count()
            response = requests.post(broker_url, json=payload)
            print(f"POST Response: {response.status_code} {response.content}", flush=True)
        else:
            print(f"{time.time()} No raw_traffic data",file=sys.stderr)
    except Exception as e:
        print(f"service error: {e}", file=sys.stderr)
        sys.exit(1)
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"service error: {e}", file=sys.stderr)
