import serial
import SerialVFD
import time

import queue
from threading import Thread

Tx_queue = queue.Queue()
Rx_queue = queue.Queue()


def worker():
    start_marker = '<'
    end_marker = '>'
    data_started = False
    data_buf = ""
    message_complete = False

    # This will have the side effect of reseting the arduino
    serial_port = serial.Serial(port='/dev/ttyUSB0')
    # waitForArduino()
    # time.sleep(2)
    awake = False
    while not awake:
        serial_port.write(b'<?>')
        ch = serial_port.read()
        print(ch)
        awake = (ch == '!'.encode())
        time.sleep(1)

    while True:
        try:
            string_to_send = Tx_queue.get()
        except queue.Empty:
            pass
        else:
            string_with_markers = start_marker
            string_with_markers += string_to_send
            string_with_markers += end_marker
            serial_port.write(string_with_markers.encode('utf-8'))

        if serial_port.inWaiting() > 0 and not message_complete:
            x = serial_port.read().decode("utf-8")  # decode needed for Python3

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
                Rx_queue.put(data_buf)
                message_complete = False
            except queue.Full:
                pass


def consumer():
    while True:
        try:
            mess = Rx_queue.get()
        except queue.Empty:
            pass
        else:
            print(mess)


# Initialise the lcd class
lcd = SerialVFD.SerialVFD(Tx_queue, 20, 2)

serial_thread = Thread(target=worker)
serial_thread.start()

# Print a two line message
lcd.message = "Hello\nCircuitPython"
# Wait 5s
time.sleep(5)
lcd.clear()
# Print two line message right to left
lcd.text_direction = lcd.RIGHT_TO_LEFT
lcd.message = "Hello\nCircuitPython"
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
