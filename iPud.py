import time
from FrontPanel import FrontPanel
import queue

from pylms.server import Server

sc = Server(hostname="192.168.2.75")
sc.connect()

print("Logged in: %s" % sc.logged_in)
print("Version: %s" % sc.get_version())

print(sc.get_players())
sq = sc.get_player(b'raspberrypi')

fp = FrontPanel()


start_volume = sq.get_volume()
print("Start Volume: %d" % start_volume)

start_position = 0
knob_position = 0

switcher = {
    'b': "Button ",
    'k': "knob "
}
while True:
    try:
        mess = fp.Rx_queue.get_nowait().split()
        mess0 = switcher.get(mess[0])

        if mess0:
            if mess[0] == 'k':
                knob_position = int(mess[2])
                new_volume = start_volume + knob_position - start_position
                fp.lcd.message = "Volume: " + str(new_volume)
                sq.set_volume(new_volume)
            else:
                fp.lcd.message = mess0 + mess[1] + ' ' + mess[2]

    except queue.Empty:
        start_volume = sq.get_volume()
        start_position = knob_position
        time.sleep(0.1)
