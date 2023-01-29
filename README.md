# wukong_wioe5

A short demo showing how to use a [SeeedStudio Wio-e5](https://wiki.seeedstudio.com/Grove_LoRa_E5_New_Version/) with a RPi pico and an [Elecfreaks Wukong 2040](https://www.elecfreaks.com/elecfreaks-wukong2040-breakout-board-for-raspberry-pi-pico.html). It uses my fork of the [SSD1306 library for MP](https://github.com/Kongduino/ssd1306_mp).

See this [Twitter thread](https://twitter.com/Kongduino/status/1615538626636701698) for more information.

## BOM

* **Wukong 2040** by Elecfreaks
* **Raspberry Pico**
* **Wio-E5** by SeeedStudio
* **SSD1306 OLED** – by... well, many places :-) Get one with the proper pinout: `GND Vcc SCL SDA`
* **18650** battery

## The Basics

The Wukong 2040 has a couple of neat tricks: the I2C headers a 2 x male and 1 x female. Which means that not only can you connect 3 I2C devices directly, but should you have an OLED with the proper pinout, you just plop it in and are ready to go. The next sweet deal is the number of `GPIO / Vcc / GND` triplets. And since UART0 is exposed, it was child's play to connect the Wio-E5 to the Pico. There are 2 user buttons, which I am not using right now, but which could come in handy – for example here, send a PING packet on demand. The 2 neopixels are a nice thing to have – many not exactly a must have, but again for this example they come in handy to show LoRa activity.

I am not making use yet of the 4 Motor Connectors, but I will: I have two 2-wire brushless motors, and could use them to rotate a solar panel in the optimal position, based on time of day, and time of year.

A couple of other things, less vital, more in the "Oh, that's cool to have" class: the reset button, much more accessible than on the Pico; and the ON/OFF switch.

All in all, this Pico baseboard is a great addition to my toolbox, and I will be back for more! The Wio-E5 is already an old friend, so no surprises here – although I have a few complaints about it, and am planning to get them fixed, working it out with Seeed.

![demo](demo.gif)


