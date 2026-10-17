<div align="right">

**English** | [فارسی](README.fa.md)

</div>

# Server Monitor Telegram Bot

A lightweight Linux server monitor that sends a resource report to **one** Telegram user every 15 minutes.

No dependencies, no daemon, no database: a single Python script using only the standard library, scheduled by a `systemd` timer. It runs for a few seconds, sends the report, and exits, so it uses no memory between runs.

## Features

- **CPU** usage (2-second sample) and load average
- **RAM** used and available (based on `MemAvailable`, so it ignores reclaimable cache)
- **Swap** usage
- **Disk** usage and free space for any number of mount points
- Server **uptime**
- Top 3 processes by memory
- 🟢 / 🔴 status icon per metric when it crosses a warning threshold
- Reports go only to a single numeric Telegram user ID
- The bot token is kept in a root-only (`600`) env file, never in the code

## Sample report

```text
🖥 my-server
⏱ Uptime: 131d 22h 5m

🟢 CPU: 12.4% (3 cores)
   Load: 0.39 / 0.42 / 0.39
🟢 RAM: 40% — 2.15 GB free of 3.57 GB
🟢 Swap: 21% — 1.25 / 6.00 GB
🟢 Disk /: 44% — 17.8 GB free of 33.2 GB
🟢 Disk /tmp: 1% — 1.2 GB free of 1.3 GB

🔝 Top RAM:
  • python: 238 MB
  • cpsrvd: 217 MB
  • httpd: 121 MB

🕒 2026-10-17 16:32:00 +0330
```

## Requirements

- Linux with `systemd`
- Python 3.6+ (already present on most distributions)
- A Telegram bot token from [@BotFather](https://t.me/BotFather)
- Your numeric Telegram user ID (get it from [@userinfobot](https://t.me/userinfobot))

> Send `/start` to your bot once before installing. Telegram bots can't message a user who has never started them.

## Installation

```bash
git clone https://github.com/Amir-Pakdel/Server-Monitor-Telegram-Bot.git
cd Server-Monitor-Telegram-Bot
sudo ./install.sh
```

The installer asks for the bot token and your user ID, writes them to `/etc/server-monitor.env`, sends a test report, and enables the timer.

### Manual installation

```bash
sudo install -d /opt/server-monitor
sudo install -m 755 monitor.py /opt/server-monitor/
sudo install -m 644 server-monitor.service server-monitor.timer /etc/systemd/system/
sudo cp .env.example /etc/server-monitor.env && sudo chmod 600 /etc/server-monitor.env
sudo nano /etc/server-monitor.env
sudo systemctl daemon-reload
sudo systemctl enable --now server-monitor.timer
```

## Configuration

`/etc/server-monitor.env`:

| Variable | Description | Example |
|---|---|---|
| `BOT_TOKEN` | Bot token from BotFather | `123456789:AA...` |
| `CHAT_ID` | Numeric Telegram user ID that receives reports | `1146958478` |
| `DISKS` | Comma-separated mount points to report | `/,/tmp,/home` |

The warning thresholds are at the top of `monitor.py`:

```python
WARN_DISK = 85
WARN_RAM = 85
WARN_SWAP = 70
WARN_CPU = 85
```

To change the interval, edit `OnCalendar=` in `server-monitor.timer` (for example `*:0/5` for every 5 minutes), then run `systemctl daemon-reload`.

## Usage

```bash
sudo systemctl start server-monitor          # send a report right now
systemctl list-timers server-monitor.timer   # see when the next report is due
journalctl -u server-monitor -n 20           # view logs and errors
sudo systemctl disable --now server-monitor.timer   # stop reports
```

## Project structure

```text
├── monitor.py               # collects metrics and sends the report
├── server-monitor.service   # oneshot systemd service
├── server-monitor.timer     # runs the service every 15 minutes
├── install.sh               # interactive installer
└── .env.example             # configuration template
```

## Security

- Never commit your real `.env` file. It's already ignored by `.gitignore`.
- If your bot token leaks, revoke it in BotFather with `/revoke` and update `/etc/server-monitor.env`.

## Author

**Amir Pakdel** — [@Amir-Pakdel](https://github.com/Amir-Pakdel)
