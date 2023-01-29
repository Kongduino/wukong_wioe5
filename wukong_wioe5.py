# See https://twitter.com/Kongduino/status/1615538626636701698
# Basic LoRa Receiver. It doesn't do much more than sending a msg
# and display incoming messages, but that's a good place to start.

from machine import UART
import binascii, time, re, neopixel, machine, json
from ssd1306 import SSD1306_I2C

uart = UART(0, 9600)
regexUARTlen = re.compile(r'\+TEST: LEN:(\d+), RSSI:(-\d+), SNR:(-?\d+)')
regexUARTmsg = re.compile(r'\+TEST: RX "(\w+)"')
np = neopixel.NeoPixel(machine.Pin(22), 2)
i2c = machine.I2C(sda=machine.Pin(16), scl=machine.Pin(17), id=0)
oled = SSD1306_I2C(128, 64, i2c)

print('UART Wio-E5 Serial')

def sendString(txt):
  # Sends a string encoded in hexadecimal.
  np[1] = (0, 255, 0) # Neopixel #1 = Green
  np.write()
  s = binascii.hexlify(txt)
  txt=s.decode('utf-8')
  result = uartSerialRxMonitor(f'AT+TEST=TXLRPKT, {txt}')
  np[1] = (0, 0, 0) # Neopixel #1 = OFF
  np.write()
  return result

def uartSerialRxMonitor(command):
  # Sends a command, terminated by CRLF, and returns the output from the firmware.
  print(command)
  uart.write(command + '\r\n')
  time.sleep(0.5)
  recv = bytes()
  while uart.any()>0:
    recv += uart.read(1)
    time.sleep(0.01)
  res=recv.decode('utf-8')
  return res.strip()

def configLoRa(freq = 868.125, SF=12, BW=125, txPR=8, rxPR = 8, txPower = 22, crc = "OFF", iq = "OFF", net = "OFF"):
  # There are a couple of issues with the AT firmware:
  # 1. The naming `TEST` is misleading, and seems to make LoRa a 3rd-class citizen.
  #    It is after all the transport layer used by LoRaWAN, and not an afterthought.
  # 2. Coding Rate, aka C/R, is not configurable. This is not ideal, to say the least.
  #    All AT firmwares I know allow for C/R setup. No reason not to allow it.
  # 3. Bandwidth setting: while LoRaWAN only has a subset of LoRa's BW, 125, 250, 500,
  #    LoRa's full set should be enabled:
  #    {7.8, 10.4, 15.6, 20.8, 31.25, 41.7, 62.5, 125, 250, 500}
  #    This is very important when you work with LoRa and need the longest range possible
  uartSerialRxMonitor(f'AT+TEST=RFCFG,{freq},SF{SF},{BW},{txPR},{rxPR},{txPower},{crc},{iq},{net}')

def handleIncoming():
  np[0] = (0, 255, 0) # Neopixel #0 = Green
  np[1] = (0, 0, 0) # Neopixel #1 = OFF
  np.write()
  recv = bytes() # We will add bytes to recv as they come
  while uart.any()>0:
    recv += uart.read(1)
    time.sleep(0.01)
  txt=recv.decode('utf-8').strip().split('\n')
  # Split into lines for parsing
  np[0] = (0, 0, 0) # Neopixel #0 = OFF
  np.write()
  print(txt)
  for line in txt:
    # Regex recognizing the incoming text LEN sentence
    result = regexUARTlen.match(line)
    if result != None:
      np[1] = (0, 0, 255) # Neopixel #1 = Blue
      np.write()
      print(f'Incoming message at RSSI {result.group(2)}, SNR {result.group(3)}')
      oled.fill(0)
      oled.text('Wio-e5 LoRa', 1, 4)
      oled.text(f'RSSI {result.group(2)}, SNR {result.group(3)}', 1, 56)
      oled.show()
    else:
      # Regex recognizing the incoming text content sentence
      result = regexUARTmsg.match(line)
      if result != None:
        # dehex text
        msg = binascii.unhexlify(result.group(1))
        msg = msg.decode('utf-8').strip()
        print(msg)
        try:
          # we are expecting JSON
          x = json.loads(msg)
          ln = 16
          for k in x.keys():
            oled.text(f'{k} {x[k]}', 1, ln)
            ln += 8
        except:
          # If it's not JSON let's print it as is
          j = int(len(msg) / 16)
          ln = 16
          for i in range(j):
            oled.text(msg[i*16:16], 1, ln)
            ln += 8
        oled.show()
        time.sleep(0.5)
        np[1] = (0, 0, 0) # Neopixel #1 = OFF
        np.write()
    
oled.fill(0)
oled.text('Wio-e5 LoRa', 1, 4)
oled.show()

res=uartSerialRxMonitor('AT')
print(res)
time.sleep(1)
res=uartSerialRxMonitor('AT+MODE=TEST')
print(res)
time.sleep(1)
configLoRa(freq = 868.250, SF=12, BW=125)
res=uartSerialRxMonitor('AT+TEST=?')
print(res)
sendString('Hello there')
res=uartSerialRxMonitor('AT+TEST=RXLRPKT')

while True:
  if uart.any() > 0:
    handleIncoming()
