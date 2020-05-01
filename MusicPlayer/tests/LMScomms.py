import telnetlib
import urllib.parse

charset = 'utf8'


def __encode(text):
    return text.encode(charset)


def __decode(mbytes):
    return mbytes.decode(charset)


def __quote(text):
    return urllib.parse.quote(text, encoding=charset)


def __unquote(text):
    return urllib.parse.unquote(text, encoding=charset)


HOST = '192.168.2.75'
PORT = '9090'

tn = telnetlib.Telnet(host=HOST, port=PORT)

msg_list = ['current_title ?', 'title ?', 'album ?', 'artist ?', 'genre ?', 'path ?', 'remote ?']

for msg in msg_list:
    tn.write(__encode(msg + '\n'))
    response = tn.read_until(__encode('\n'))[:-1]
    response = __unquote(__decode(response))
    print(response)
