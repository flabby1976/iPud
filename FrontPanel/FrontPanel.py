import serial
import cmd


class Dummy(cmd.Cmd):

    def cmdloop(self, intro=None):
        """Repeatedly issue a prompt, accept input, parse an initial prefix
        off the received input, and dispatch to action methods, passing them
        the remainder of the line as argument.

        """

        self.preloop()
        if intro is not None:
            self.intro = intro
        if self.intro:
            self.stdout.write(str(self.intro)+"\n")
        stop = None
        while not stop:
            if self.cmdqueue:
                line = self.cmdqueue.pop(0)
            else:
                self.stdout.write(self.prompt)
                self.stdout.flush()
                line = self.stdin.readline().decode()
                if not len(line):
                    line = 'EOF'
                else:
                    line = line.rstrip('\r\n')
            line = self.precmd(line)
            stop = self.onecmd(line)
            stop = self.postcmd(stop, line)
        self.postloop()

    def default(self, line):
      print(line)

    def do_button(self, arg):
       print(arg)

ser = serial.Serial(
 port='/dev/ttyUSB0',
 baudrate = 9600,
 parity=serial.PARITY_NONE,
 stopbits=serial.STOPBITS_ONE,
 bytesize=serial.EIGHTBITS,
 timeout=10
)

#while 1:
# x=ser.readline()
# print (x.decode())

ll = Dummy(stdin=ser, stdout=ser)
#ll.use_rawinput = False
#ll = Dummy()
ll.use_rawinput = False
ll.prompt = ">".encode()
ll.cmdloop()
