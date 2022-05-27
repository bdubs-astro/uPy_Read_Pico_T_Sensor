'''
The RPi Pico's temperature sensor measures the voltage of a biased bipolar diode (Vbe), 
connected to the fifth ADC channel.

Typically, Vbe = 0.706 V at 27 °C, with a slope of -1.721 mV per degree.
The ADC resolution of 16/65535 (i.e., 12 bit) equates to approx. 0.47 °C.

Resources:

timers:
https://docs.micropython.org/en/latest/rp2/quickref.html#timers
https://micropython-docs-esp32.readthedocs.io/en/esp32_doc/library/machine.Timer.html#machine-timer

enable larger fonts for the OLED display:
https://github.com/peterhinch/micropython-font-to-py
https://www.youtube.com/watch?v=bLXMVTTPFMs
https://blog.miguelgrinberg.com/post/micropython-and-the-internet-of-things-part-vi-working-with-a-screen
'''

from machine import Pin, ADC, Timer
import utime as time
from micropython import const

def disp_setup(scl_pin, sda_pin, width, height, id = 0, addr = 0x3C):
    from machine import Pin, I2C
    from ssd1306 import SSD1306_I2C
    
    i2c = I2C(id, scl=Pin(scl_pin), sda=Pin(sda_pin), freq=400000)
    oled = SSD1306_I2C(WIDTH, HEIGHT, i2c, addr)
    return oled

def disp_string (oled, x, y, str, disp_logo = True):
    import framebuf
    import writer
    import freesans20

    # Raspberry Pi logo as 32x32 bytearray
    logo = bytearray(b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00|?\x00\x01\x86@\x80\x01\x01\x80\x80\x01\x11\x88\x80\x01\x05\xa0\x80\x00\x83\xc1\x00\x00C\xe3\x00\x00~\xfc\x00\x00L'\x00\x00\x9c\x11\x00\x00\xbf\xfd\x00\x00\xe1\x87\x00\x01\xc1\x83\x80\x02A\x82@\x02A\x82@\x02\xc1\xc2@\x02\xf6>\xc0\x01\xfc=\x80\x01\x18\x18\x80\x01\x88\x10\x80\x00\x8c!\x00\x00\x87\xf1\x00\x00\x7f\xf6\x00\x008\x1c\x00\x00\x0c \x00\x00\x03\xc0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00")
     
    oled.fill(0)
    font_writer = writer.Writer(oled, freesans20, False) # disable verbose mode
    font_writer.set_textpos(x, y)
    font_writer.printstring(str)
    if disp_logo:
        fb = framebuf.FrameBuffer(logo, 32, 32, framebuf.MONO_HLSB)  # load the framebuffer
        # MONO_HLSB: monochrome, horizontally mapped - each byte occupies 8 horizontal pixels with bit 0 being the leftmost 
        oled.blit(fb, 96, 0) # blit the image from the framebuffer to the display
    oled.show()

def readT():
    # internal T sensor
    tempSensor = ADC(4) # 5th ADC channel
    Vbe = 0.706         # V
    tOffs = 27          # °C
    slope = -0.001721   # V/°C

    adcRaw = tempSensor.read_u16()
    adcVolt = adcRaw * 3.3/65535
    tC = tOffs + (adcVolt - Vbe)/slope
    return tC, adcVolt, adcRaw
    
def readISR(event):
    global ledStart
    ledStart = time.ticks_ms()
    led.high()
    
    timestamp = rtc.datetime()
    (year,month,day,xxx,hour,minute,sec,xxx) = timestamp
    timestring = '%02d:%02d:%02d, %02d/%02d/%04d: '%(hour, minute, sec, month, day, year)
    
    tC, adcVolt, adcRaw = readT()
    disp_string (oled, 5, 5, ('%.1f C' %(tC)))
    print(timestring + '%.2f°C, %.4fV, ADC: %d'%(tC, adcVolt, adcRaw))
   
# I2C OLED setup
scl_pin= const(5)
sda_pin = const(4)
WIDTH  = 128                                          
HEIGHT = 32

oled = disp_setup(scl_pin, sda_pin, WIDTH, HEIGHT)

# LED setup
ledBuiltin = 25
ledDuration = 50    # ms
led = Pin(ledBuiltin, Pin.OUT, value = 0)

timerFreq = 0.5     # timer interrupt frequency (Hz)
readSensor = Timer()

rtc = machine.RTC()

readSensor.init(freq = timerFreq, mode = Timer.PERIODIC, callback = readISR) # frequency in Hz ... could also use period in ms

while True:
    # turn off the LED
    if (led.value() == 1 and time.ticks_diff(time.ticks_ms(), ledStart) > ledDuration):
        led.low() 

