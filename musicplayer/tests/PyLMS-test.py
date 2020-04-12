from pylms.server import Server
# from pylms.player import Player

sc = Server(hostname="192.168.2.75")
sc.connect()

print("Logged in: %s" % sc.logged_in)
print("Version: %s" % sc.get_version())
#
# print(sc.request_with_results("bbciplayer items 0 100"))

print(sc.get_players())

sq = sc.get_player(b'raspberrypi')

print("Name: %s | ref: %s | Mode: %s | Time: %s | Connected: %s | WiFi: %s" % (sq.get_name(), sq.get_ref(), sq.get_mode(), sq.get_time_elapsed(), sq.is_connected, sq.get_wifi_signal_strength()))

print(sq.get_track_title())
print(sq.get_time_remaining())
print(sq.playlist_get_info())

print(sc.search('band', mode='albums'))
