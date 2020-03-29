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
defaults.ctl.card 0
defaults.pcm.card 0
```

Also need to turn the volume up with ```alsamixer -c 1```

