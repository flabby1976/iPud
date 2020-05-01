import time

from FrontPanel import FrontPanel
from MusicPlayer import MusicPlayer
import queue

fp = FrontPanel()

fp.lcd.clear()
fp.lcd.message = "Well hello!!\nHow are YOU doing?"

mp = MusicPlayer(my_name='raspberrypi', server_ip='192.168.2.75', display=fp.lcd)

while True:
    try:
        key_press = fp.Rx_queue.get_nowait()
        mp.do_cmd(key_press)
    except queue.Empty:
        pass

    try:
        from_LMS = mp.Rx_queue.get_nowait()
        mp.do_cmd(from_LMS)
    except queue.Empty:
        time.sleep(0.1)
