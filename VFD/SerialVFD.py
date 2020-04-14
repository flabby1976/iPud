import time


class SerialVFD(object):

    LEFT_TO_RIGHT = 0
    RIGHT_TO_LEFT = 1

    def __init__(self, serial_device, columns, lines):

        self.columns = columns
        self.lines = lines

        #  save pin numbers
        self.serial_device = serial_device

        # Initialise the display
        awake = False
        while not awake:
          self.serial_device.write(b'<?>')
          ch = self.serial_device.read()
          print(ch)
          awake = (ch == '!'.encode())
          time.sleep(1)

        self._cursoron = False
        self._cursorblink = False
        self._display = True
        
        self.clear()

        self._message = None
        self._enable = None
        self._direction = self.LEFT_TO_RIGHT
        # track row and column used in cursor_position
        # initialize to 0,0
        self.row = 0
        self.column = 0
        self._column_align = False

    def home(self):
        """Moves the cursor "home" to position (0, 0).
        """
        self.serial_device.write(b'<h>')
        time.sleep(0.003)

    def clear(self):
        """Clears everything displayed on the LCD.
        """
        self.serial_device.write(b'<c>')
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
            self.serial_device.write(b'<k 1>')
        else:
            self.serial_device.write(b'<k 0>')

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
        code = '<m ' + str(column) + ' ' + str(row) + '>'
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
            self.serial_device.write(b'<b 1>')
        else:
            self.serial_device.write(b'<b 0>')

    @property
    def display(self):
        """
        Enable or disable the display. True to enable the display. False to disable the display.
        """
        return self._display

    @display.setter
    def display(self, enable):
        self._display = enable
        if enable:
            self.serial_device.write(b'<d 1>')
        else:
            self.serial_device.write(b'<d 0>')

    @property
    def message(self):
        """Display a string of text on the character LCD.
        Start position is (0,0) if cursor_position is not set.
        If cursor_position is set, message starts at the set
        position from the left for left to right text and from
        the right for right to left text. Resets cursor column
        and row to (0,0) after displaying the message.
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
                if self._direction == self.LEFT_TO_RIGHT:
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
                if self._direction == self.LEFT_TO_RIGHT:
                    col = self.column * self._column_align
                else:
                    if self._column_align:
                        col = self.column
                    else:
                        col = self.columns - 1
                self.cursor_position(col, line)
            # Write string to display
            else:
                code = '<p ' + character + '>'
                self.serial_device.write(code.encode())

        # reset column and row to (0,0) after message is displayed
        self.column, self.row = 0, 0

    def move_left(self):
        """Moves displayed text left one column.
        """
        self.serial_device.write(b'<s l>')

    def move_right(self):
        """Moves displayed text right one column.
        """
        self.serial_device.write(b'<s r>')

    @property
    def text_direction(self):
        """The direction the text is displayed. To display the text left to right beginning on the
        left side of the LCD, set ``text_direction = LEFT_TO_RIGHT``. To display the text right
        to left beginning on the right size of the LCD, set ``text_direction = RIGHT_TO_LEFT``.
        Text defaults to displaying from left to right.
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
        self.serial_device.write(b'<r 0>')

    def _right_to_left(self):
        # Displays text from right to left on the LCD.
        self.serial_device.write(b'<r 1>')

    def create_char(self, location, pattern):
        pass
        # """
        # Fill one of the first 8 CGRAM locations with custom characters.
        # The location parameter should be between 0 and 7 and pattern should
        # provide an array of 8 bytes containing the pattern. E.g. you can easily
        # design your custom character at http://www.quinapalus.com/hd44780udg.html
        # To show your custom character use, for example, ``lcd.message = "\x01"``

        # :param location: integer in range(8) to store the created character
        # :param ~bytes pattern: len(8) describes created character

        # """
        # # only position 0..7 are allowed
        # location &= 0x7
        # self._write8(_LCD_SETCGRAMADDR | (location << 3))
        # for i in range(8):
        # self._write8(pattern[i], char_mode=True)
