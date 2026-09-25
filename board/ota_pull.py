# /sdcard/ota_pull.py
# CanMV K230 / MicroPython wireless OTA — fetch main.py from PC over Wi-Fi
# Called by boot.py before main.py starts (so files are not locked).
#
# ★ Fill in WIFI_* and PC_IP before first use. Do NOT commit real passwords.

import os
import time
import socket

# ========== EDIT THESE ==========
WIFI_SSID = "YOUR_WIFI_SSID"
WIFI_PASSWORD = "YOUR_WIFI_PASSWORD"
NETWORK_TIMEOUT = 20
PC_IP = "192.168.1.100"       # PC LAN IP (same Wi-Fi as the board)
PC_PORT = 8000
REMOTE_PATH = "/main.py"
# ===============================

# Write to free names first, then boot.py installs (avoids EPERM on running main.py)
TMP_NEW = "/tmp/ota_main.py"
PENDING = "/sdcard/main_pend.py"
NEXT = "/sdcard/main_next.py"
MAIN = "/sdcard/main.py"
BAK = "/sdcard/main.py.bak"
MIN_SIZE = 32


def wifi_connect(ssid, password, timeout=20):
    import network
    try:
        sta = network.WLAN(network.STA_IF)
    except Exception:
        sta = network.WLAN(0)
    for _ in range(20):
        try:
            if sta.isconnected():
                break
        except Exception:
            pass
        time.sleep_ms(200)
    if not sta.isconnected():
        try:
            sta.connect(ssid, password)
        except Exception as e:
            print("[OTA] connect err", e)
        t0 = time.time()
        while not sta.isconnected():
            if time.time() - t0 > timeout:
                raise RuntimeError("wifi timeout status=%s" % (sta.status(),))
            time.sleep_ms(300)
    ip = sta.ifconfig()[0]
    if not ip or ip == "0.0.0.0":
        raise RuntimeError("no ip %s" % (sta.ifconfig(),))
    return sta, ip


def http_get(host, port, path, timeout=10):
    ai = socket.getaddrinfo(host, port)
    s = socket.socket()
    s.settimeout(timeout)
    try:
        s.connect(ai[0][-1])
        s.send(("GET %s HTTP/1.0\r\nHost: %s\r\n\r\n" % (path, host)).encode())
        data = b""
        while True:
            c = s.recv(4096)
            if not c:
                break
            data += c
    finally:
        try:
            s.close()
        except Exception:
            pass
    sep = data.find(b"\r\n\r\n")
    if sep < 0:
        raise RuntimeError("bad http")
    status = data[:sep].decode("utf-8", "ignore").split("\r\n")[0]
    body = data[sep + 4 :]
    if "200" not in status:
        raise RuntimeError("http " + status)
    return body


def try_write(path, body):
    try:
        try:
            os.remove(path)
        except Exception:
            pass
        f = open(path, "wb")
        n = f.write(body)
        f.close()
        print("[OTA] wrote", path, n)
        return True
    except Exception as e:
        print("[OTA] write fail", path, e)
        return False


def main():
    print("[OTA] wifi", WIFI_SSID)
    sta, ip = wifi_connect(WIFI_SSID, WIFI_PASSWORD, NETWORK_TIMEOUT)
    print("[OTA] board", ip)
    print("[OTA] get", PC_IP, PC_PORT, REMOTE_PATH)
    body = http_get(PC_IP, PC_PORT, REMOTE_PATH)
    print("[OTA] downloaded", len(body))
    if len(body) < MIN_SIZE:
        raise RuntimeError("small file")

    ok = False
    if try_write(TMP_NEW, body):
        ok = True
    if try_write(PENDING, body):
        ok = True
    if try_write(NEXT, body):
        ok = True
    if try_write(MAIN, body):
        ok = True

    if not ok:
        raise RuntimeError("all write paths failed")

    try:
        import machine
        print("[OTA] reboot to install")
        time.sleep_ms(400)
        machine.reset()
    except Exception as e:
        print("[OTA] reset skip", e)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("[OTA] FAIL", e)
