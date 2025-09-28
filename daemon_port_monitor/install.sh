#!/bin/bash
# install.sh

# 如果 port_monitor_daemon_dir 没有定义，则设置为当前目录
export port_monitor_daemon_dir="/opt/port_monitor_daemon"
: "${port_monitor_daemon_dir:=$(pwd)}"
echo "port_monitor_daemon_dir=$port_monitor_daemon_dir"

# 创建目录（如果不存在）
mkdir -p "$port_monitor_daemon_dir"

# env 文件路径
ENV_FILE="$port_monitor_daemon_dir/client.env"

# 生成 env 文件
cat > "$ENV_FILE" <<EOF
    daemon_dir=$port_monitor_daemon_dir
    env_path=$ENV_FILE
    port_record_file=$port_monitor_daemon_dir/ports.txt
    program_key="xray"
EOF

echo ".env 已生成: $ENV_FILE"
cat "$ENV_FILE"


if [ "$port_monitor_daemon_dir" != "$(pwd)" ]; then
    rm -rf "$port_monitor_daemon_dir/*"
    cp -r * $port_monitor_daemon_dir
fi
# 如果需要复制当前目录下特定文件到 port_monitor_daemon_dir，可以这样做
# cp -r my_folder "$port_monitor_daemon_dir"  # 示例，避免复制所有文件
pip install -r "requirements.txt"

cp $port_monitor_daemon_dir/port_monitor.service /etc/systemd/system/port_monitor.service
cp $port_monitor_daemon_dir/port_monitor.timer  /etc/systemd/system/port_monitor.timer
systemctl daemon-reload
systemctl disable port_monitor.service
systemctl enable port_monitor.service
systemctl stop port_monitor.service
systemctl start port_monitor.service
# systemctl status port_monitor.service
systemctl daemon-reload
systemctl enable --now port_monitor.timer
# systemctl list-timers --all
# systemctl status port_monitor.timer
