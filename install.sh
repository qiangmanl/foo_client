#!/usr/bin/env bash
set -euo pipefail


echo "[INFO] 检查 nftables..."
if ! command -v nft >/dev/null 2>&1; then
    echo "[WARN] 未检测到 nft，准备安装..."
    if command -v apt-get >/dev/null 2>&1; then
        apt-get update -y && apt-get install -y nftables
    elif command -v dnf >/dev/null 2>&1; then
        dnf install -y nftables
    elif command -v yum >/dev/null 2>&1; then
        yum install -y nftables
    else
        echo "[ERROR] 未知包管理器，无法安装 nftables" >&2
        exit 1
    fi
else
    echo "[OK] nft 已安装: $(nft --version)"
fi

echo "[INFO] 检查 Python3..."
if ! command -v python3 >/dev/null 2>&1; then
    echo "[WARN] 未检测到 Python3，准备安装..."
    if command -v apt-get >/dev/null 2>&1; then
        apt-get update -y && apt-get install -y python3 python3-venv python3-pip
    elif command -v dnf >/dev/null 2>&1; then
        dnf install -y python3 python3-pip
    elif command -v yum >/dev/null 2>&1; then
        yum install -y python3 python3-pip
    else
        echo "[ERROR] 未知包管理器，无法安装 python3" >&2
        exit 1
    fi
else
    echo "[OK] Python3 已安装: $(python3 --version)"
fi

echo "[SUCCESS] 环境检查完成，可以继续运行服务。"


cd ./daemon_traffic
./install.sh
cd ../daemon_port_monitor 
./install.sh
cd ..

