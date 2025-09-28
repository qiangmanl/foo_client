#!/bin/bash
# install.sh

# 如果 traffic_daemon_dir 没有定义，则设置为当前目录
export traffic_daemon_dir="/opt/traffic_daemon"
: "${traffic_daemon_dir:=$(pwd)}"
echo "traffic_daemon_dir=$traffic_daemon_dir"

# 创建目录（如果不存在）
mkdir -p "$traffic_daemon_dir"

# env 文件路径
ENV_FILE="$traffic_daemon_dir/client.env"

# 生成 env 文件
cat > "$ENV_FILE" <<EOF
env_path=$ENV_FILE
table_family=inet
table_name=traffic_stats
ipaddr=$(curl -4 -s ifconfig.me)
broker_url=http://47.243.182.216:8600/report_traffic
traffic_count_path=$traffic_daemon_dir/traffic_count.txt
EOF

echo ".env 已生成: $ENV_FILE"
cat "$ENV_FILE"


if [ "$traffic_daemon_dir" != "$(pwd)" ]; then
    rm -rf "$traffic_daemon_dir/*"
    cp -r * $traffic_daemon_dir
fi
# 如果需要复制当前目录下特定文件到 traffic_daemon_dir，可以这样做
# cp -r my_folder "$traffic_daemon_dir"  # 示例，避免复制所有文件
pip install -r "requirements.txt"

cp $traffic_daemon_dir/traffic_reporter.service /etc/systemd/system/traffic_reporter.service
cp $traffic_daemon_dir/traffic_reporter.timer  /etc/systemd/system/traffic_reporter.timer
systemctl daemon-reload
systemctl disable traffic_reporter.service
systemctl enable traffic_reporter.service
systemctl stop traffic_reporter.service
systemctl start traffic_reporter.service
# systemctl status traffic_reporter.service
systemctl daemon-reload
systemctl enable --now traffic_reporter.timer
# systemctl list-timers --all
# systemctl status traffic_reporter.timer
