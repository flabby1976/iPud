class Serial_VFD:

    def __init__(self, serial_device, columns, lines):

        self.columns = columns
        self.lines = lines
        #  save pin numbers
        self.serial_device = serial_device

        # # Initialise the display
        # self._write8(0x33)
        # self._write8(0x32)
        # # Initialise display control
        # self.displaycontrol = _LCD_DISPLAYON | _LCD_CURSOROFF | _LCD_BLINKOFF
        # # Initialise display function
        # self.displayfunction = _LCD_4BITMODE | _LCD_1LINE | _LCD_2LINE | _LCD_5X8DOTS
        # # Initialise display mode
        # self.displaymode = _LCD_ENTRYLEFT | _LCD_ENTRYSHIFTDECREMENT
        # # Write to displaycontrol
        # self._write8(_LCD_DISPLAYCONTROL | self.displaycontrol)
        # # Write to displayfunction
        # self._write8(_LCD_FUNCTIONSET | self.displayfunction)
        # # Set entry mode
        # self._write8(_LCD_ENTRYMODESET | self.displaymode)
        
        self._cursoron = False
        self._cursorblink = False
        self._displayon = True
        
        self.clear()

        self._message = None
        self._enable = None
        self._direction = None
        # track row and column used in cursor_position
        # initialize to 0,0
        self.row = 0
        self.column = 0
        self._column_align = False

    def home(self):
        """Moves the cursor "home" to position (1, 1).
        """
        code = b'<h>'
        self.serial_device.write(code)
        time.sleep(0.003)


    def clear(self):
        """Clears everything displayed on the LCD.
        """
        code = b'<c>'
        self.serial_device.write(code)
        time.sleep(0.003)

    @property
    def column_align(self):
        """If True, message text after '\\n' starts directly below start of first
        character in message. If False, text after '\\n' starts at column zero.
        """
        return self._column_align

    @column_align.setter
    def column_align(self, enable):
        if isinstance(enable, bool):
            self._column_align = enable
        else:
            raise ValueError("The column_align value must be either True or False")

    @property
    def cursor(self):
        """True if cursor is visible. False to stop displaying the cursor.
        """
        return self._cursoron

    @cursor.setter
    def cursor(self, show):
        self._cursoron = show
        if show:
            code = '<k 1>
        else:
            code = '<k 0>
        self.serial_device.write(code.encode())

    def cursor_position(self, column, row):
        """Move the cursor to position ``column``, ``row`` for the next
        message only. Displaying a message resets the cursor position to (0, 0).

            :param column: column location
            :param row: row location
        """
        # Clamp row to the last row of the display
        if row >= self.lines:
            row = self.lines - 1
        # Clamp to last column of display
        if column >= self.columns:
            column = self.columns - 1
        
        # Set location 
        code = '<m ' + str(col) + ' ' + str(row) + '>'
        self.serial_device.write(code.encode())

        # Update self.row and self.column to match setter
        self.row = row
        self.column = column

    @property
    def blink(self):
        """
        Blink the cursor. True to blink the cursor. False to stop blinking.
        """
        return self._cursorblink

    @blink.setter
    def blink(self, blink):
        self._cursorblink = blink
        if blink:
            code = '<b 1>'
        else:
            code = '<b 0>'
        self.serial_device.write(code.encode())

    @property
    def display(self):
        """
        Enable or disable the display. True to enable the display. False to disable the display.
        """
        return self.displaycontrol & _LCD_DISPLAYON == _LCD_DISPLAYON

    @display.setter
    def display(self, enable):
        if enable:
            code = '<b 1>'
        else:
            code = '<b 0>'
        self.serial_device.write(code.encode())

    @property
    def message(self):
        """Display a string of text on the character LCD.
        Start position is (0,0) if cursor_position is not set.
        If cursor_position is set, message starts at the set
        position from the left for left to right text and from
        the right for right to left text. Resets cursor column
        and row to (0,0) after displaying the message.

        The following example displays, "Hello, world!" on the LCD.

        .. code-block:: python

            import time
            import board
            import busio
            import adafruit_character_lcd.character_lcd_i2c as character_lcd

            i2c = busio.I2C(board.SCL, board.SDA)
            lcd = character_lcd.Character_LCD_I2C(i2c, 16, 2)

            lcd.message = "Hello, world!"
            time.sleep(5)
        """
        return self._message

    @message.setter
    def message(self, message):
        self._message = message
        # Set line to match self.row from cursor_position()
        line = self.row
        # Track times through iteration, to act on the initial character of the message
        initial_character = 0
        # iterate through each character
        for character in message:
            # If this is the first character in the string:
            if initial_character == 0:
                # Start at (0, 0) unless direction is set right to left, in which case start
                # on the opposite side of the display if cursor_position not set or (0,0)
                # If cursor_position is set then starts at the specified location for
                # LEFT_TO_RIGHT. If RIGHT_TO_LEFT cursor_position is determined from right.
                # allows for cursor_position to work in RIGHT_TO_LEFT mode
                if self.displaymode & _LCD_ENTRYLEFT > 0:
                    col = self.column
                else:
                    col = self.columns - 1 - self.column
                self.cursor_position(col, line)
                initial_character += 1
            # If character is \n, go to next line
            if character == "\n":
                line += 1
                # Start the second line at (0, 1) unless direction is set right to left in
                # which case start on the opposite side of the display if cursor_position
                # is (0,0) or not set. Start second line at same column as first line when
                # cursor_position is set
                if self.displaymode & _LCD_ENTRYLEFT > 0:
                    col = self.column * self._column_align
                else:
                    if self._column_align:
                        col = self.column
                    else:
                        col = self.columns - 1
                self.cursor_position(col, line)
            # Write string to display
            else:
                self._write8(ord(character), True)
        # reset column and row to (0,0) after message is displayed
        self.column, self.row = 0, 0

    def move_left(self):
        """Moves displayed text left one column.

        The following example scrolls a message to the left off the screen.

        .. code-block:: python

            import time
            import board
            import busio
            import adafruit_character_lcd.character_lcd_i2c as character_lcd

            i2c = busio.I2C(board.SCL, board.SDA)
            lcd = character_lcd.Character_LCD_I2C(i2c, 16, 2)

            scroll_message = "<-- Scroll"
            lcd.message = scroll_message
            time.sleep(2)
            for i in range(len(scroll_message)):
                lcd.move_left()
                time.sleep(0.5)
        """
        self._write8(_LCD_CURSORSHIFT | _LCD_DISPLAYMOVE | _LCD_MOVELEFT)

    def move_right(self):
        """Moves displayed text right one column.

        The following example scrolls a message to the right off the screen.

        .. code-block:: python

            import time
            import board
            import busio
            import adafruit_character_lcd.character_lcd_i2c as character_lcd

            i2c = busio.I2C(board.SCL, board.SDA)
            lcd = character_lcd.Character_LCD_I2C(i2c, 16, 2)

            scroll_message = "Scroll -->"
            lcd.message = scroll_message
            time.sleep(2)
            for i in range(len(scroll_message) + 16):
                lcd.move_right()
                time.sleep(0.5)
        """
        self._write8(_LCD_CURSORSHIFT | _LCD_DISPLAYMOVE | _LCD_MOVERIGHT)

    @property
    def text_direction(self):
        """The direction the text is displayed. To display the text left to right beginning on the
        left side of the LCD, set ``text_direction = LEFT_TO_RIGHT``. To display the text right
        to left beginning on the right size of the LCD, set ``text_direction = RIGHT_TO_LEFT``.
        Text defaults to displaying from left to right.

        The following example displays "Hello, world!" from right to left.

        .. code-block:: python

            import time
            import board
            import busio
            import adafruit_character_lcd.character_lcd_i2c as character_lcd

            i2c = busio.I2C(board.SCL, board.SDA)
            lcd = character_lcd.Character_LCD_I2C(i2c, 16, 2)

            lcd.text_direction = lcd.RIGHT_TO_LEFT
            lcd.message = "Hello, world!"
            time.sleep(5)
        """
        return self._direction

    @text_direction.setter
    def text_direction(self, direction):
        self._direction = direction
        if direction == self.LEFT_TO_RIGHT:
            self._left_to_right()
        elif direction == self.RIGHT_TO_LEFT:
            self._right_to_left()

    def _left_to_right(self):
        # Displays text from left to right on the LCD.
        self.displaymode |= _LCD_ENTRYLEFT
        self._write8(_LCD_ENTRYMODESET | self.displaymode)

    def _right_to_left(self):
        # Displays text from right to left on the LCD.
        self.displaymode &= ~_LCD_ENTRYLEFT
        self._write8(_LCD_ENTRYMODESET | self.displaymode)

    def create_char(self, location, pattern):
        """
        Fill one of the first 8 CGRAM locations with custom characters.
        The location parameter should be between 0 and 7 and pattern should
        provide an array of 8 bytes containing the pattern. E.g. you can easily
        design your custom character at http://www.quinapalus.com/hd44780udg.html
        To show your custom character use, for example, ``lcd.message = "\x01"``

        :param location: integer in range(8) to store the created character
        :param ~bytes pattern: len(8) describes created character

        """
        # only position 0..7 are allowed
        location &= 0x7
        self._write8(_LCD_SETCGRAMADDR | (location << 3))
        for i in range(8):
            self._write8(pattern[i], char_mode=True)

    def _write8(self, value, char_mode=False):
        # Sends 8b ``value`` in ``char_mode``.
        # :param value: bytes
        # :param char_mode: character/data mode selector. False (default) for
        # data only, True for character bits.
        #  one ms delay to prevent writing too quickly.
        time.sleep(0.001)
        #  set character/data bit. (charmode = False)
        self.reset.value = char_mode
        # WRITE upper 4 bits
        self.dl4.value = ((value >> 4) & 1) > 0
        self.dl5.value = ((value >> 5) & 1) > 0
        self.dl6.value = ((value >> 6) & 1) > 0
        self.dl7.value = ((value >> 7) & 1) > 0
        #  send command
        self._pulse_enable()
        # WRITE lower 4 bits
        self.dl4.value = (value & 1) > 0
        self.dl5.value = ((value >> 1) & 1) > 0
        self.dl6.value = ((value >> 2) & 1) > 0
        self.dl7.value = ((value >> 3) & 1) > 0
        self._pulse_enable()

    def _pulse_enable(self):
        # Pulses (lo->hi->lo) to send commands.
        self.enable.value = False
        # 1microsec pause
        time.sleep(0.0000001)
        self.enable.value = True
        time.sleep(0.0000001)
        self.enable.value = False
        time.sleep(0.0000001)




