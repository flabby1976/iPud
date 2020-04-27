import time

from FrontPanel import FrontPanel
from MusicPlayer import MusicPlayer
import queue


radio = b'Squeezebox Radio'
radio = b'raspberrypi'

mp = MusicPlayer(name=radio, server="192.168.2.75")

fp = FrontPanel()

fp.lcd.clear()
fp.lcd.message = "Well hello!!\nHow are YOU doing?"

while True:
    try:
        key_press = fp.Rx_queue.get_nowait()
        print(key_press)
        print('Current state: ' + mp.state)

        mp.do_cmd(key_press)

    except queue.Empty:
        time.sleep(0.1)
