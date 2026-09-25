# /sdcard/boot.py
# CanMV K230 boot: install pending OTA payload, try wireless update, then run main.py
import os
import gc
import time


def _read(path):
    f = open(path, "rb")
    d = f.read()
    f.close()
    return d


def install_pending():
    cands = [
        "/tmp/ota_main.py",
        "/sdcard/main_pend.py",
        "/sdcard/main_next.py",
    ]
    src = None
    for p in cands:
        try:
            if os.stat(p)[6] >= 32:
                src = p
                break
        except Exception:
            pass
    if not src:
        print("[BOOT] no pending")
        return
    print("[BOOT] pending from", src, os.stat(src)[6])
    try:
        d = _read(src)
    except Exception as e:
        print("[BOOT] read fail", e)
        return
    try:
        old = _read("/sdcard/main.py")
        open("/sdcard/main.py.bak", "wb").write(old)
    except Exception:
        pass
    try:
        try:
            os.remove("/sdcard/main.py")
        except Exception:
            pass
        open("/sdcard/main.py", "wb").write(d)
        print("[BOOT] installed", len(d))
    except Exception as e:
        print("[BOOT] install fail", e)
        return
    for p in cands:
        try:
            os.remove(p)
        except Exception:
            pass


time.sleep_ms(200)
install_pending()
gc.collect()

try:
    print("[BOOT] ota")
    g = {}
    exec(open("/sdcard/ota_pull.py").read(), g)
    g["main"]()
except Exception as e:
    print("[BOOT] ota skip", e)

gc.collect()
exec(open("/sdcard/main.py").read())
