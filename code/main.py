# Example app for CanMV K230 wireless OTA
# After OTA, boot.py replaces /sdcard/main.py and runs this.

import time

_screen_ok = False
try:
    import image
    from media.display import *
    from media.media import *
    Display.init(Display.ST7701, width=800, height=480, fps=60)
    MediaManager.init()
    _screen_ok = True
except Exception as e:
    print("display init skip:", e)

TITLE = "WIRELESS OTA"
LINE2 = "updated without USB"
LINE3 = "version: 1.0"

print("Hello", TITLE, LINE3)


def draw():
    if not _screen_ok:
        return
    canvas = image.Image(800, 480, image.RGB565)
    canvas.draw_rectangle(0, 0, 800, 480, color=(10, 20, 40), thickness=1, fill=True)
    canvas.draw_string_advanced(220, 140, 42, TITLE, color=(80, 220, 120))
    canvas.draw_string_advanced(220, 220, 28, LINE2, color=(220, 220, 220))
    canvas.draw_string_advanced(220, 280, 24, LINE3, color=(180, 180, 180))
    Display.show_image(canvas)


draw()
n = 0
while True:
    n += 1
    if n % 30 == 0:
        draw()
    time.sleep_ms(100)
