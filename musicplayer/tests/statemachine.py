# from transitions import Machine
import transitions
import re
# import json

from pylms.server import Server
# from pylms.player import Player


class RegexDict(dict):
    def get_matching(self, event):
        for key in self:
            pp = re.search(key, event)
            if pp:
                resp = self[key]
                for t in range(len(pp.groups())):
                    ss = pp.group(t+1)
                    rr = '$'+str(t+1)
                    resp = resp.replace(rr, ss)
                resp = resp.split(" ")
                return resp[0], resp[1:]
        return None


class MusicPlayer(object):
    def __init__(self):
        self.state = None

        self.knob_postion = 50

        self.sc = Server(hostname="192.168.2.75")
        self.sc.connect()

        print("Logged in: %s" % self.sc.logged_in)
        print("Version: %s" % self.sc.get_version())

        print(self.sc.get_players())

        self.sq = self.sc.get_player(b'raspberrypi')
        self.sq.set_volume(50)
        self.sq.stop()

    def set_vol(self, *args):
        print('Setting volume knob to ' + args[0])
        new_knob = int(args[0])
        current_volume = self.sq.get_volume()
        new_volume = current_volume + new_knob - self.knob_postion
        print(current_volume, new_volume, self.knob_postion)
        self.sq.set_volume(new_volume)
        self.knob_postion = new_knob

    def tune_it(self, *args):
        chan = args[0]
        if chan == '':
            chan = '0'
        print('tuning to chan ' + chan)
        self.sq.playlist_play_index(int(chan))

    # noinspection PyUnusedLocal
    @staticmethod
    def play_it(*args):
        print('playing!')
        pass

    # noinspection PyUnusedLocal
    def pause_it(self, *args):
        self.sq.pause()
        print('paused')
        pass

    # noinspection PyUnusedLocal
    def unpause_it(self, *args):
        self.sq.unpause()
        print('unpaused')
        pass

    # noinspection PyUnusedLocal
    def stop_it(self, *args):
        self.sq.stop()
        print('stopped')
        pass


mp = MusicPlayer()

states = ['idle', 'tuning', 'playing', 'paused', 'stopped']

machine = transitions.Machine(model=mp, states=states, initial='idle')

machine.add_transition(trigger='tune', source=['tuning', 'idle', 'playing', 'paused', 'stopped'],
                       dest='playing', before='tune_it')
machine.add_transition(trigger='play', source='stopped', dest='playing')
machine.add_transition(trigger='pause', source='playing', dest='paused')
machine.add_transition(trigger='stop', source=['playing', 'paused'], dest='stopped')
machine.add_transition(trigger='unpause', source='paused', dest='playing')
machine.add_transition(trigger='setvol', source='playing', dest='', after='set_vol')

machine.on_enter_playing('play_it')
machine.on_enter_paused('pause_it')
machine.on_exit_paused('unpause_it')
machine.on_enter_stopped('stop_it')

keymaps = {
    'idle': {
        'b (\\d) (\\w)': 'tune $1',
    },
    'playing': {
        'k 1 (\\d+)': 'setvol $1',
        'b (\\d) (\\w)': 'tune $1 $2',
        'b k s': 'pause',
        'b k l': 'stop'
    },
    'paused': {
        'b k s': 'unpause'
    },
    'stopped': {
        'b k l': 'play'
    }
}

# print(json.dumps(keymaps, indent=4))

key_presses = [
    'b 3 s',
    'k 1 40',
    # 'b k s',
    # 'b k s',
    # 'b k l',
    # 'b k l',
    # 'k 1 45',
    'k 1 50'
]

for key_press in key_presses:

    print('Current state: ' + mp.state)

    rrr = RegexDict(keymaps[mp.state]).get_matching(key_press)

    cmd = rrr[0]
    arg = rrr[1]

    method_to_call = getattr(mp, cmd)

    print(key_press, ' -> ', cmd, arg)

    try:
        method_to_call(*arg)
    except transitions.core.MachineError as e:
        print('Oops! ' + str(e))
