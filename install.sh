#!/usr/bin/env bash
set -euo pipefail

if [ "$(id -u)" -ne 0 ]; then
    echo "Run as root: sudo ./install.sh" >&2
    exit 1
fi

cd "$(dirname "$0")"

install -d /opt/server-monitor
install -m 755 monitor.py /opt/server-monitor/monitor.py
install -m 644 server-monitor.service /etc/systemd/system/server-monitor.service
install -m 644 server-monitor.timer /etc/systemd/system/server-monitor.timer

if [ ! -f /etc/server-monitor.env ]; then
    read -rp "Telegram bot token: " token
    read -rp "Your numeric Telegram user ID: " chat_id
    umask 077
    printf 'BOT_TOKEN=%s\nCHAT_ID=%s\nDISKS=/\n' "$token" "$chat_id" > /etc/server-monitor.env
fi
chmod 600 /etc/server-monitor.env

systemctl daemon-reload
systemctl start server-monitor.service
systemctl enable --now server-monitor.timer

echo "Installed. A test report was sent; next reports every 15 minutes."
systemctl list-timers server-monitor.timer --no-pager
