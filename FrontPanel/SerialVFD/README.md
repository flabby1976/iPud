Code to drive the Vacuum Fluorescent Display
============================================

Functions to enable the Raspberry Pi to drive the [20T202DA2JA 20x2 Character VFD](https://www.adafruit.com/product/347). This display came from [Adafruit](https://www.adafruit.com/product/347) but is now discontinued. There are Arduino libraries [available](https://github.com/adafruit/SPI_VFD) for it, but nothing for the Pi. I had a go at hacking something together, but [ThisOldGeek](https://thisoldgeek.blogspot.com/) had already written code for it at https://thisoldgeek.blogspot.com/2013/02/spi-for-samsung-vfd-on-raspberry-pi.html. The initial code for DisplayTest.py came from his [Hello_World](https://github.com/thisoldgeek/RPi_SPI_VFD/blob/master/Hello_World.py)

Starting from Raspbian Lite, need to install ```python3-spidev``` which is not included by default.
```
sudo apt-get install python3-spidev
```

Big numbers from here - https://github.com/RalphBacon/LCD_Big_digits

