Audio output
============

Turtle Beach usb audio sound card
Identifies as a C-Media composite device

```
pi@raspberrypi:~ $ lsusb
Bus 001 Device 004: ID 0d8c:0002 C-Media Electronics, Inc. Composite Device
Bus 001 Device 003: ID 0424:ec00 Standard Microsystems Corp. SMSC9512/9514 Fast Ethernet Adapter
Bus 001 Device 002: ID 0424:9512 Standard Microsystems Corp. SMC9512/9514 USB Hub
Bus 001 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
```

Used this guide -
https://cdn-learn.adafruit.com/downloads/pdf/usb-audio-cards-with-a-raspberry-pi.pdf

Using Rasbian stretch so only had to edit ```/usr/share/alsa/alsa.conf``` to change default audio card from 0 to 1

```
defaults.ctl.card 1
defaults.pcm.card 1
```

Also need to turn the volume up with ```alsamixer -c 1```

Then test with -

```speaker-test -c2 --test=wav -w /usr/share/sounds/alsa/Front_Center.wav```

and then -

```
sudo apt-get install mpg123
mpg123 http://bbcmedia.ic.llnwd.net/stream/bbcmedia_radio4fm_mf_p
```

Audio amplifier [Adafruit Mono 2.5W Class D Audio Amplifier - PAM8302](https://www.adafruit.com/product/2130)

BBC Radio streams http://www.suppertime.co.uk/blogmywiki/2015/04/updated-list-of-bbc-network-radio-urls/

http://www.radiofeeds.co.uk/mp3.asp

