# CanMV K230 Wireless OTA — Update MicroPython Code over Wi-Fi (No USB)

**Update K230 / CanMV app code wirelessly.** Change `main.py` on your PC, power-cycle the board, done — no USB cable, no re-flashing, no CanMV IDE required.

> **Keywords:** CanMV K230 OTA · K230 wireless code update · MicroPython OTA · K230 Wi-Fi deploy · remote update CanMV · K230 remote main.py · 立创天工 K230 无线更新 · 嘉楠 K230 OTA · MicroPython remote deployment

---

## Why this exists

If you have ever:

- unplugged and replugged USB **just to tweak one line** on a K230…
- deployed a board on a robot / camera / contest rig and **cannot reach the USB port**…
- wanted **ESP32-style OTA** on CanMV K230…

…this repo is for you.

Official CanMV IDE / VS Code extension talks to the board over **USB**.  
This project adds a **Wi-Fi boot-time OTA** path for **application-level** Python code (`main.py`).

| | USB IDE | **This project** |
|--|---------|------------------|
| Change code without cable | ❌ | ✅ |
| Works after the board is mounted | ❌ | ✅ |
| App-level `main.py` update | ✅ | ✅ |
| Flash firmware / bootloader | ✅ | ❌ (use USB) |

---

## How it works

```text
 PC (same Wi-Fi)                         K230 board
┌──────────────────┐   HTTP GET         ┌─────────────────────┐
│  code/main.py    │ ◄───────────────── │  boot.py            │
│  python -m       │   /main.py :8000   │    1. install pend  │
│  http.server 8000│                    │    2. ota_pull Wi-Fi│
└──────────────────┘                    │    3. run main.py   │
                                        └─────────────────────┘
```

**Boot sequence (the important part):**

1. `boot.py` runs **before** `main.py` (so `main.py` is **not locked**).
2. If a pending file exists (`/tmp/ota_main.py`, `main_pend.py`, …) → **install** it as `main.py`.
3. `ota_pull.py` connects to Wi-Fi and downloads the new `main.py`.
4. It writes to **pending names first** (avoids `EPERM` while the app is running).
5. Board reboots once → new code runs.

That “pending + install on boot” trick is what makes OTA reliable on MicroPython/CanMV FAT filesystems.

---

## Quick start

### 1) Prepare the PC (same Wi-Fi as the board)

```powershell
git clone https://github.com/<you>/canmv-k230-wireless-ota.git
cd canmv-k230-wireless-ota
# edit code\main.py  (e.g. change version text)
.\pc\serve.ps1
```

Note the PC’s LAN IP (e.g. `192.168.1.23`). Keep port **8000** open on the firewall for the local network.

### 2) First-time board setup (USB once)

1. Copy `board/ota_pull.py` and `board/boot.py` to the board as `/sdcard/ota_pull.py` and `/sdcard/boot.py`.
2. Copy `code/main.py` to `/sdcard/main.py`.
3. Edit `/sdcard/ota_pull.py`:

```python
WIFI_SSID = "YourWiFi"
WIFI_PASSWORD = "YourPassword"
PC_IP = "192.168.1.23"
```

Use CanMV IDE, CanMV for VS Code, or any MicroPython file tool.

### 3) Daily workflow — **no USB**

1. Edit `code/main.py` on the PC.  
2. Run `.\pc\serve.ps1`.  
3. **Power-cycle the K230.**  
4. The board pulls the new file and shows your new UI.

---

## Repo layout

```text
board/ota_pull.py   # Wi-Fi download + safe pending write  → copy to /sdcard/
board/boot.py       # install pending, then OTA, then main  → copy to /sdcard/
code/main.py        # example app (change freely)           → PC HTTP root / board main.py
pc/serve.ps1        # one-command static file server
```

---

## Tested hardware

- **LCKFB LSPI K230 (1G) CanMV** — firmware `K230-v1.8-8` / CanMV MicroPython  
- Other CanMV K230 boards with Wi-Fi should work if `network.WLAN` is available  
- **K230D standard firmware may not include Wi-Fi** — check your image first  

Board-side connect pattern matches official examples:

```python
sta = network.WLAN(network.STA_IF)  # or network.WLAN(0)
sta.connect(SSID, PASSWORD)
```

> Some images reject `sta.active(True)` (“Network is always active”) — this repo does **not** call `active()`.

---

## FAQ

**Why not write `main.py` directly in OTA?**  
While the app is running, `open("main.py","wb")` often fails with `EPERM`. We stage to `/tmp/ota_main.py` or `main_pend.py`, then `boot.py` installs before the app starts.

**Can I update while the board is powered without reboot?**  
You can download over Wi-Fi anytime; **displaying** the new app still needs a reboot (or your app can `exec` the new file). Boot-time install is the simple, reliable path.

**Is this firmware OTA?**  
No. Application Python only. Firmware still uses the USB flasher.

**Security**  
Local HTTP is fine for labs and contests. For production, add a token, HTTPS, or signed payloads.

**My IP changed (DHCP).**  
Update `PC_IP` in `ota_pull.py` (and push that one file over USB or a prior OTA), or give the PC a DHCP reservation.

---

## Star this if it saved your weekend

If this removed the USB cable from your K230 workflow, please ⭐ **Star** the repo — it helps other makers find it.

Issues and PRs welcome: boards, Wi-Fi modules, boards without ST7701, simpler `serve` scripts, Windows/Linux/macOS.

---

## 中文简介

**CanMV K230 无线更新 Python 代码**：电脑改 `main.py` → 板子开机用 Wi-Fi 拉取 → 自动安装并运行，**不用插 USB**。

- 适合：机器人、视觉小车、电赛、现场部署后无法拔线的场景  
- 原理：`boot.py` 在 `main.py` 启动前安装 pending 文件，再通过 HTTP 从电脑下载  
- 关键点：运行中不能覆盖 `main.py`（`EPERM`），所以先写 `main_pend.py` / `/tmp`，开机再替换  
- 边界：只更新应用代码，不替代固件烧录  

详细步骤见上文 **Quick start**。欢迎 Star / Issue / PR。

---

## License

[MIT](LICENSE)
