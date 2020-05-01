Audio output
============

Audio out using the I2S output and this [MAX98357 I2S Amp Breakout](https://www.adafruit.com/product/3006) from Adafruit

Guide is [here](https://learn.adafruit.com/adafruit-max98357-i2s-class-d-mono-amp)

Also need to turn the volume up with ```alsamixer -c 1```

Then test with -

```speaker-test -c2 --test=wav -w /usr/share/sounds/alsa/Front_Center.wav```

and then -

```
sudo apt-get install mpg123
mpg123 http://bbcmedia.ic.llnwd.net/stream/bbcmedia_radio4fm_mf_p
```

BBC Radio streams http://www.suppertime.co.uk/blogmywiki/2015/04/updated-list-of-bbc-network-radio-urls/

http://www.radiofeeds.co.uk/mp3.asp

