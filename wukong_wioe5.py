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
  np[1] = (0, 255, 0)
  np.write()
  s = binascii.hexlify(txt)
  txt=s.decode('utf-8')
  result = uartSerialRxMonitor(f'AT+TEST=TXLRPKT, {txt}')
  np[1] = (0, 0, 0)
  np.write()
  return result

def uartSerialRxMonitor(command):
  print(command)
  uart.write(command + '\r\n')
  time.sleep(0.5)
  recv = bytes()
  while uart.any()>0:
    recv += uart.read(1)
    time.sleep(0.01)
  res=recv.decode('utf-8')
  return res.strip()

def configLoRa(freq = 868.125, SF=12, BW=125, txPR=8, rxPR = 8,
               txPower = 22, crc = "OFF", iq = "OFF", net = "OFF"):
  uartSerialRxMonitor(f'AT+TEST=RFCFG,{freq},SF{SF},{BW},{txPR},{rxPR},{txPower},{crc},{iq},{net}')

def handleIncoming():
  np[0] = (0, 255, 0)
  np[1] = (0, 0, 0)
  np.write()
  recv = bytes()
  while uart.any()>0:
    recv += uart.read(1)
    time.sleep(0.01)
  txt=recv.decode('utf-8').strip().split('\n')
  np[0] = (0, 0, 0)
  np.write()
  print(txt)
  for line in txt:
    result = regexUARTlen.match(line)
    if result != None:
      np[1] = (0, 0, 255)
      np.write()
      print(f'Incoming message at RSSI {result.group(2)}, SNR {result.group(3)}')
      oled.fill(0)
      oled.text('Wio-e5 LoRa', 1, 4)
      oled.text(f'RSSI {result.group(2)}, SNR {result.group(3)}', 1, 56)
      oled.show()
    else:
      result = regexUARTmsg.match(line)
      if result != None:
        msg = binascii.unhexlify(result.group(1))
        msg = msg.decode('utf-8').strip()
        print(msg)
        try:
          x = json.loads(msg)
          ln = 16
          for k in x.keys():
            oled.text(f'{k} {x[k]}', 1, ln)
            ln += 8
        except:
          j = int(len(msg) / 16)
          ln = 16
          for i in range(j):
            oled.text(msg[i*16:16], 1, ln)
            ln += 8
        oled.show()
        time.sleep(0.5)
        np[1] = (0, 0, 0)
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
