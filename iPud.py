import serial
import SerialVFD
import time
import logging

import queue
from threading import Thread

Tx_queue = queue.Queue()
Rx_queue = queue.Queue()

format = "%(asctime)s: %(message)s"
logging.basicConfig(format=format, level=logging.INFO,
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
                lcd.message = mess0 +  mess[1] +' '+ mess[2]
        except queue.Empty:
            time.sleep(0.1)


# Initialise the lcd class
lcd = SerialVFD.SerialVFD(Tx_queue, 20, 2)


# This will have the side effect of reseting the arduino
serial_port = serial.Serial(port='/dev/ttyUSB0', timeout=0)

# waitForArduino
awake = False
while not awake:
    logging.info('<?>')
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


# Print a two line message
lcd.message = "Hello\nCircuitPython"
print('*')
# Wait 5s
time.sleep(5)
lcd.clear()
print('*')
# Print two line message right to left
lcd.text_direction = lcd.RIGHT_TO_LEFT
print('*')
lcd.message = "Hello\nCircuitPython"
print('*')
# Wait 5s
time.sleep(5)
# Return text direction to left to right
lcd.text_direction = lcd.LEFT_TO_RIGHT
lcd.clear()
# Print a two line message, with column aligh
lcd.cursor_position(3, 0)
lcd.column_align = True
lcd.message = "With\ncolumn align"
# Wait 5s
time.sleep(5)
lcd.clear()
# Print a two line message, with column aligh
lcd.row = 0
lcd.column = 3
lcd.column_align = False
lcd.message = "Without\ncolumn align"
# Wait 5s
time.sleep(5)
lcd.clear()
# Display cursor
lcd.clear()
lcd.cursor = True
lcd.message = "Cursor!"
# Wait 5s
time.sleep(5)
# Display blinking cursor
lcd.clear()
lcd.blink = True
lcd.message = "Blinky Cursor!"
# Wait 5s
time.sleep(5)
lcd.blink = False
lcd.clear()
# Create message to scroll
scroll_msg = "<-- Scroll"
lcd.message = scroll_msg
# Scroll message to the left
for i in range(len(scroll_msg)):
    time.sleep(0.5)
    lcd.move_left()
lcd.clear()
lcd.message = "Going to sleep\nCya later!"
time.sleep(2)
lcd.display = False
time.sleep(2)
