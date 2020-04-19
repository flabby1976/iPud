import serial
import SerialVFD
import time
import logging

import queue
from threading import Thread

Tx_queue = queue.Queue()
Rx_queue = queue.Queue()

logging_format = "%(asctime)s: %(message)s"
logging.basicConfig(format=logging_format, level=logging.INFO,
                    datefmt="%H:%M:%S")


def worker():
    start_marker = '<'

    end_marker = '>'
    data_started = False
    data_buf = ""
    message_complete = False

    while True:
        try:
            string_to_send = Tx_queue.get_nowait()
        except queue.Empty:
            pass
        #            time.sleep(0.1)
        else:
            string_with_markers = start_marker
            string_with_markers += string_to_send
            string_with_markers += end_marker
            serial_port.write(string_with_markers.encode('utf-8'))

        while serial_port.inWaiting() > 0 and not message_complete:
            x = serial_port.read().decode("utf-8")
            if data_started:
                if x != end_marker:
                    data_buf = data_buf + x
                else:
                    data_started = False
                    message_complete = True
            elif x == start_marker:
                data_buf = ''
                data_started = True

        if message_complete:
            try:
                #                logging.info(data_buf)
                Rx_queue.put_nowait(data_buf)
                message_complete = False
            except queue.Full:
                pass


def consumer():
    switcher = {
        'b': "Button ",
        'k': "knob "
    }
    while True:
        try:
            mess = Rx_queue.get_nowait().split()
            mess0 = switcher.get(mess[0])
            if mess0:
                lcd.message = mess0 + mess[1] + ' ' + mess[2]
        except queue.Empty:
            time.sleep(0.1)


# Initialise the lcd class
lcd = SerialVFD.SerialVFD(Tx_queue, 20, 2)

# This will have the side effect of reseting the arduino
serial_port = serial.Serial(port='/dev/ttyUSB0', timeout=0)

# waitForArduino
awake = False
while not awake:
#    logging.info('<?>')
    serial_port.write(b'<?>')
    ch = serial_port.read()
    logging.info(ch)
    awake = (ch == '!'.encode())
#    time.sleep(1)

lcd.clear()
lcd.message = "I'm ready!\nFAV1 FAV2  FAV3 FAV4"

serial_thread = Thread(target=worker, daemon=True)
serial_thread.start()
print_thread = Thread(target=consumer, daemon=True)
print_thread.start()

while True:
    time.sleep(5)
