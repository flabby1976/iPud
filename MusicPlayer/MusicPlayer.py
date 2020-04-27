from pylms.server import Server
import transitions
import re


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


class MusicPlayer(transitions.Machine):

    def __init__(self, name=None, server=None):
        transitions.Machine.__init__(self, states=[])

        self.define_state_machine()

        self.knob_postion = 50

        self.sc = Server(hostname=server)
        self.sc.connect()

        print("Logged in: %s" % self.sc.logged_in)
        print("Version: %s" % self.sc.get_version())

        print(self.sc.get_players())

        self.sq = self.sc.get_player(name)
        self.sq.set_volume(50)
        self.sq.stop()

    def define_state_machine(self):

        states = ['idle', 'tuning', 'playing', 'paused', 'stopped']
        self.add_states(states)

        self.add_transition(trigger='tune', source=['tuning', 'idle', 'playing', 'paused', 'stopped'],
                            dest='playing', before='tune_it')
        self.add_transition(trigger='play', source='stopped', dest='playing')
        self.add_transition(trigger='pause', source='playing', dest='paused')
        self.add_transition(trigger='stop', source=['playing', 'paused'], dest='stopped')
        self.add_transition(trigger='unpause', source='paused', dest='playing')
        self.add_transition(trigger='setvol', source='playing', dest='', after='set_vol')

        self.on_enter_playing('play_it')
        self.on_enter_paused('pause_it')
        self.on_exit_paused('unpause_it')
        self.on_enter_stopped('stop_it')

        self.set_state('idle')

        self.keymaps = {
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


    def do_cmd(self, key_press):
        print(key_press)
        print('Current state: ' + self.state)
        rrr = RegexDict(self.keymaps[self.state]).get_matching(key_press)

        print(rrr)
        if rrr:

            cmd = rrr[0]
            arg = rrr[1]

            method_to_call = getattr(self, cmd)

            print(key_press, ' -> ', cmd, arg)

            try:
                method_to_call(*arg)
            except transitions.core.MachineError as e:
                print('Oops! ' + str(e))
        else:
            print('No keymap entry for '+key_press+' in state '+self.state)

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
    def play_it(self, *args):
        self.sq.play()
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


if __name__ == "__main__":

    import time

    mp = MusicPlayer(name=b'raspberrypi', server="192.168.2.75")

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

        print('Current state: ' + mp.state)

        time.sleep(2)

        mp.do_cmd(key_p)
