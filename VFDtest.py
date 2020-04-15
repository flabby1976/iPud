import serial
import SerialVFD
import time

ser = serial.Serial(port='/dev/ttyUSB0')

# Initialise the lcd class
lcd = SerialVFD.SerialVFD( ser, 20, 2)

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
