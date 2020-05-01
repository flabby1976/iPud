from pylms.server import Server
import transitions
import re
from threading import Thread
import telnetlib
import queue
import urllib.parse
import json


class RegexDict(dict):
    def get_matching(self, event):
        for key in self:
            print('trying key: ', key)
            pp = re.search(key, event)
            if pp:
                resp = self[key]
                if not resp:
                    return None
                for t in range(len(pp.groups())):
                    ss = pp.group(t+1)
                    rr = '$'+str(t+1)
                    resp = resp.replace(rr, ss)
                resp = resp.split(" ")
                return resp[0], resp[1:]
        return None


def my_quote(text):
    return urllib.parse.quote(text, encoding='utf8')


def my_unquote(text):
    return urllib.parse.unquote(text, encoding='utf8')


class MusicPlayer(transitions.Machine):

    def __init__(self, my_name=None, server_ip=None, display=None):

        transitions.Machine.__init__(self, states=[])

        self.display = display
        self.server_ip = server_ip
        
        self.keymaps = None

        self.define_state_machine()

        self.Rx_queue = queue.Queue()

        self.knob_postion = 50

        server = Server(hostname=self.server_ip)
        server.connect()

        print("Logged in: %s" % server.logged_in)
        print("Version: %s" % server.get_version())

        self.my_player = server.get_player(my_name)
        self.my_player.set_volume(50)
        self.my_player.stop()

        print('My id is: ' + self.my_player.ref)

        # start the thread to manage to telnet link back to LMS
        telnet_thread = Thread(target=self._telnet_worker, daemon=True)
        telnet_thread.start()

    def _telnet_worker(self):
        self.tn = telnetlib.Telnet(host=self.server_ip, port='9090')
        self.tn.write(b'listen 1\n')

        while True:
            notification = self.tn.read_until(b'\n')[:-1]
            notification = my_unquote(notification.decode()).split()
            # only responds to notifications sent to me!
            if notification[0] == self.my_player.ref:
                # only interested in these notifications
                if notification[1] in ['playlist', 'stop', 'play', 'pause']:
                    self.Rx_queue.put_nowait(" ".join(notification[1:]))

    def define_state_machine(self):

        with open('/home/pi/iPud/MusicPlayer/statemachine.json') as json_file:
            data = json.load(json_file)
            states = data['states']
            my_transitions = data['transitions']
            self.keymaps = data['keymaps']

        self.add_states(states)
        self.add_transitions(my_transitions)

        self.set_state(data['initial state'])

    def do_cmd(self, key_press):

        if key_press:
            print('key press is: ' + key_press)
            print('Current state: ' + self.state)

            # Decode a key-press to a musicplayer statemachine trigger
            trigger = RegexDict(self.keymaps[self.state]).get_matching(key_press)

            # Returns None if no trigger associated with this key-press in this state
            if trigger:

                cmd = trigger[0]
                arg = trigger[1]

                try:
                    method_to_call = getattr(self, cmd)
                except AttributeError as e:
                    print('Oops! Trigger \"' + cmd + '\" is not defined in the state machine')
                    print(str(e))
                else:
                    print(key_press, ' -> ', cmd, arg)
                    try:
                        method_to_call(*arg)
                    except transitions.core.MachineError as e:
                        print('Oops! Transition \"' + method_to_call + '\" is not allowed in state ' + self.state)
                        print('Oops! Machine error! :' + str(e))
            else:
                print('No keymap entry for \"'+key_press+'\" in state '+self.state)
            print("New state: " + self.state)
        return

    def set_vol(self, *args):
        print('Setting volume knob to ' + args[0])
        new_knob = int(args[0])
        current_volume = self.my_player.get_volume()
        new_volume = current_volume + new_knob - self.knob_postion
        print(current_volume, new_volume, self.knob_postion)
        self.my_player.set_volume(new_volume)
        self.knob_postion = new_knob

    def tune_it(self, *args):
        chan = args[0]
        if chan == '':
            chan = '0'
        print('tuning to chan ' + chan)
        self.my_player.playlist_play_index(int(chan))

    # noinspection PyUnusedLocal
    def play_it(self, *args):
        self.my_player.play()
        self.disp_it()

    # noinspection PyUnusedLocal
    def pause_it(self, *args):
        self.my_player.pause()
        print('paused')
        pass

    # noinspection PyUnusedLocal
    def unpause_it(self, *args):
        self.my_player.unpause()
        print('unpaused')
        pass

    # noinspection PyUnusedLocal
    def stop_it(self, *args):
        self.my_player.stop()
        print('stopped')
        pass

    # noinspection PyUnusedLocal
    def disp_it(self, *args):

        self.display.clear()
        self.display.message = self.my_player.get_track_title() + "\n" + self.my_player.get_track_artist()

        print('artist: ' + self.my_player.get_track_artist())
        print('album: ' + self.my_player.get_track_album())
        print('title: ' + self.my_player.get_track_title())
        print('current_title: ' + self.my_player.get_track_current_title())


if __name__ == "__main__":

    import time

    mp = MusicPlayer(my_name='raspberrypi', server_ip="192.168.2.75")

    key_presses = [
        'b 3 s',
        'k 1 40',
        'b k s',
        'b k s',
        'b k l',
        'b k l',
        'k 1 45',
        'k 1 50'
    ]

    for key_p in key_presses:

        time.sleep(2)

        mp.do_cmd(key_p)
