#!/usr/bin/env python3
"""Send a server resource report to a single Telegram user."""

import html
import json
import os
import socket
import subprocess
import time
import urllib.parse
import urllib.request

TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
DISKS = os.environ.get("DISKS", "/").split(",")

WARN_DISK = 85
WARN_RAM = 85
WARN_SWAP = 70
WARN_CPU = 85


def gib(kb):
    return kb / 1024 / 1024


def meminfo():
    info = {}
    with open("/proc/meminfo") as f:
        for line in f:
            key, val = line.split(":")
            info[key] = int(val.split()[0])
    return info


def cpu_percent(interval=2.0):
    def read():
        with open("/proc/stat") as f:
            vals = list(map(int, f.readline().split()[1:]))
        idle = vals[3] + vals[4]
        return idle, sum(vals)

    i1, t1 = read()
    time.sleep(interval)
    i2, t2 = read()
    return 100.0 * (1 - (i2 - i1) / max(t2 - t1, 1))


def uptime_text():
    with open("/proc/uptime") as f:
        sec = int(float(f.read().split()[0]))
    d, rem = divmod(sec, 86400)
    h, rem = divmod(rem, 3600)
    return f"{d}d {h}h {rem // 60}m"


def top_processes(n=3):
    out = subprocess.run(
        ["ps", "-eo", "rss,comm", "--sort=-rss", "--no-headers"],
        capture_output=True, text=True,
    ).stdout.splitlines()[:n]
    rows = []
    for line in out:
        rss, name = line.split(None, 1)
        rows.append(f"  • {html.escape(name)}: {int(rss) / 1024:.0f} MB")
    return rows


def mark(percent, limit):
    return "🔴" if percent >= limit else "🟢"


def build_report():
    m = meminfo()
    ram_total, ram_avail = m["MemTotal"], m["MemAvailable"]
    ram_used_pct = 100 * (ram_total - ram_avail) / ram_total
    swap_total, swap_free = m["SwapTotal"], m["SwapFree"]
    swap_pct = 100 * (swap_total - swap_free) / swap_total if swap_total else 0

    cpu = cpu_percent()
    load1, load5, load15 = os.getloadavg()
    cores = os.cpu_count() or 1

    lines = [
        f"🖥 <b>{html.escape(socket.gethostname())}</b>",
        f"⏱ Uptime: {uptime_text()}",
        "",
        f"{mark(cpu, WARN_CPU)} <b>CPU:</b> {cpu:.1f}% ({cores} cores)",
        f"   Load: {load1:.2f} / {load5:.2f} / {load15:.2f}",
        f"{mark(ram_used_pct, WARN_RAM)} <b>RAM:</b> {ram_used_pct:.0f}% — "
        f"{gib(ram_avail):.2f} GB free of {gib(ram_total):.2f} GB",
        f"{mark(swap_pct, WARN_SWAP)} <b>Swap:</b> {swap_pct:.0f}% — "
        f"{gib(swap_total - swap_free):.2f} / {gib(swap_total):.2f} GB",
    ]

    for path in DISKS:
        st = os.statvfs(path)
        total = st.f_blocks * st.f_frsize
        free = st.f_bavail * st.f_frsize
        used_pct = 100 * (total - st.f_bfree * st.f_frsize) / total
        lines.append(
            f"{mark(used_pct, WARN_DISK)} <b>Disk {html.escape(path)}:</b> {used_pct:.0f}% — "
            f"{free / 2**30:.1f} GB free of {total / 2**30:.1f} GB"
        )

    lines += ["", "🔝 <b>Top RAM:</b>", *top_processes()]
    lines.append(f"\n🕒 {time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    return "\n".join(lines)


def send(text):
    data = urllib.parse.urlencode({
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": "true",
    }).encode()
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    with urllib.request.urlopen(url, data=data, timeout=20) as resp:
        result = json.load(resp)
    if not result.get("ok"):
        raise RuntimeError(result)


if __name__ == "__main__":
    send(build_report())
