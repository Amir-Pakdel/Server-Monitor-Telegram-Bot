<div dir="rtl">

[English](README.md) | **فارسی**

# ربات تلگرام مانیتورینگ سرور

یک ابزار سبک برای مانیتورینگ سرور لینوکس که هر ۱۵ دقیقه گزارش منابع سرور را فقط برای **یک** کاربر تلگرام ارسال می‌کند.

بدون نیاز به نصب پکیج، بدون سرویس همیشه‌روشن و بدون دیتابیس: فقط یک اسکریپت پایتون با کتابخانه‌های داخلی که توسط `systemd timer` اجرا می‌شود. هر بار چند ثانیه اجرا می‌شود، گزارش را می‌فرستد و بسته می‌شود؛ پس بین اجراها هیچ رمی مصرف نمی‌کند.

## امکانات

- میزان استفاده از **پردازنده** (نمونه‌گیری ۲ ثانیه‌ای) و Load Average
- **رم** استفاده‌شده و در دسترس (بر اساس `MemAvailable`، یعنی کش قابل آزادسازی حساب نمی‌شود)
- میزان استفاده از **Swap**
- فضای استفاده‌شده و خالی **دیسک** برای هر تعداد پارتیشن
- مدت زمان روشن بودن سرور (**Uptime**)
- ۳ پروسه‌ای که بیشترین رم را مصرف می‌کنند
- نشانگر 🟢 / 🔴 برای هر مورد وقتی از حد هشدار عبور کند
- ارسال گزارش فقط به یک آیدی عددی تلگرام
- توکن ربات در یک فایل env با دسترسی فقط root (`600`) نگه‌داری می‌شود، نه داخل کد

## نمونه گزارش

</div>

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

<div dir="rtl">

## پیش‌نیازها

- لینوکس با `systemd`
- پایتون نسخه ۳.۶ یا بالاتر (روی اکثر توزیع‌ها از قبل نصب است)
- توکن ربات تلگرام از [@BotFather](https://t.me/BotFather)
- آیدی عددی تلگرام شما (از [@userinfobot](https://t.me/userinfobot) بگیرید)

> قبل از نصب، یک بار به ربات خود `/start` بفرستید. ربات تلگرام نمی‌تواند به کاربری که هرگز آن را استارت نکرده پیام بدهد.

## نصب

</div>

```bash
git clone https://github.com/Amir-Pakdel/Server-Monitor-Telegram-Bot.git
cd Server-Monitor-Telegram-Bot
sudo ./install.sh
```

<div dir="rtl">

اسکریپت نصب، توکن ربات و آیدی شما را می‌پرسد، آن‌ها را در `/etc/server-monitor.env` ذخیره می‌کند، یک گزارش تست می‌فرستد و تایمر را فعال می‌کند.

### نصب دستی

</div>

```bash
sudo install -d /opt/server-monitor
sudo install -m 755 monitor.py /opt/server-monitor/
sudo install -m 644 server-monitor.service server-monitor.timer /etc/systemd/system/
sudo cp .env.example /etc/server-monitor.env && sudo chmod 600 /etc/server-monitor.env
sudo nano /etc/server-monitor.env
sudo systemctl daemon-reload
sudo systemctl enable --now server-monitor.timer
```

<div dir="rtl">

## تنظیمات

فایل `/etc/server-monitor.env`:

| متغیر | توضیح | مثال |
|---|---|---|
| `BOT_TOKEN` | توکن ربات از BotFather | `123456789:AA...` |
| `CHAT_ID` | آیدی عددی تلگرامِ دریافت‌کننده گزارش | `1146958478` |
| `DISKS` | پارتیشن‌هایی که گزارش می‌شوند (با کاما جدا کنید) | `/,/tmp,/home` |

حدهای هشدار در ابتدای فایل `monitor.py` قرار دارند:

</div>

```python
WARN_DISK = 85
WARN_RAM = 85
WARN_SWAP = 70
WARN_CPU = 85
```

<div dir="rtl">

برای تغییر فاصله زمانی، مقدار `OnCalendar=` را در فایل `server-monitor.timer` عوض کنید (مثلاً `*:0/5` برای هر ۵ دقیقه) و سپس `systemctl daemon-reload` را اجرا کنید.

## دستورات کاربردی

</div>

```bash
sudo systemctl start server-monitor          # ارسال فوری یک گزارش
systemctl list-timers server-monitor.timer   # زمان ارسال گزارش بعدی
journalctl -u server-monitor -n 20           # مشاهده لاگ‌ها و خطاها
sudo systemctl disable --now server-monitor.timer   # توقف ارسال گزارش‌ها
```

<div dir="rtl">

## ساختار پروژه

</div>

```text
├── monitor.py               # جمع‌آوری اطلاعات و ارسال گزارش
├── server-monitor.service   # سرویس systemd از نوع oneshot
├── server-monitor.timer     # اجرای سرویس هر ۱۵ دقیقه
├── install.sh               # اسکریپت نصب تعاملی
└── .env.example             # نمونه فایل تنظیمات
```

<div dir="rtl">

## امنیت

- هرگز فایل `.env` واقعی خود را کامیت نکنید؛ این فایل از قبل در `.gitignore` قرار دارد.
- اگر توکن ربات لو رفت، در BotFather با دستور `/revoke` آن را باطل کنید و توکن جدید را در `/etc/server-monitor.env` قرار دهید.

## سازنده

**امیر پاکدل** — [@Amir-Pakdel](https://github.com/Amir-Pakdel)

</div>
