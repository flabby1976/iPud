import serial
import time
import queue
import SerialVFD
from threading import Thread


class FrontPanel(object):

    def __init__(self):

        #
        self._Tx_queue = queue.Queue()
        self.Rx_queue = queue.Queue()

        # Initialise the lcd class
        self.lcd = SerialVFD.SerialVFD(self._Tx_queue, 20, 2)

        # This will have the side effect of reseting the Arduino ...
        self._serial_port = serial.Serial(port='/dev/ttyUSB0', timeout=0)
        # ... so need to wait a couple of seconds before trying to access the port
        time.sleep(2)

        awake = False
        while not awake:
            self._serial_port.write(b'<?>')
            ch = self._serial_port.read()
            awake = (ch == '!'.encode())

        self.lcd.clear()
        self.lcd.message = "I'm ready!\niPud V0.1"

        # start the thread to manage to serial port
        serial_thread = Thread(target=self._serial_worker, daemon=True)
        serial_thread.start()

    def _serial_worker(self):

        start_marker = '<'
        end_marker = '>'

        data_started = False
        data_buf = ""
        message_complete = False

        while True:
            # Send anything in the Tx queue to the serial Tx port
            try:
                string_to_send = self._Tx_queue.get_nowait()
            except queue.Empty:
                pass
            #            time.sleep(0.1)
            else:
                string_with_markers = start_marker
                string_with_markers += string_to_send
                string_with_markers += end_marker
                self._serial_port.write(string_with_markers.encode('utf-8'))

            # If anything in serial Rx port, add bytes to incoming message buffer
            while self._serial_port.inWaiting() > 0 and not message_complete:
                x = self._serial_port.read().decode("utf-8")
                if data_started:
                    if x != end_marker:
                        data_buf = data_buf + x
                    else:
                        data_started = False
                        message_complete = True
                elif x == start_marker:
                    data_buf = ''
                    data_started = True
            # If full message in incoming message buffer, add it to the Rx queue if not full
            if message_complete:
                try:
                    self.Rx_queue.put_nowait(data_buf)
                    message_complete = False
                except queue.Full:
                    pass


if __name__ == "__main__":

    fp = FrontPanel()

    time.sleep(5)

    print("now")

    fp.lcd.clear()
    fp.lcd.message = "Well hello!!\nHow are YOU doing?"

    while True:
        try:
            mess = fp.Rx_queue.get_nowait().split()
            print(mess)
            fp.lcd.message = "Well hello!!\n" + mess
        except queue.Empty:
            time.sleep(0.1)
