'''
The RPi Pico's temperature sensor measures the voltage of a biased bipolar diode (Vbe), 
connected to the fifth ADC channel.

Typically, Vbe = 0.706 V at 27 °C, with a slope of -1.721 mV per degree.
The ADC resolution of 16/65535 (i.e., 12 bit) equates to approx. 0.47 °C.

Documentation:
https://docs.micropython.org/en/latest/rp2/quickref.html#timers
https://micropython-docs-esp32.readthedocs.io/en/esp32_doc/library/machine.Timer.html#machine-timer

'''

from machine import Pin, ADC, Timer
import utime

Vbe = 0.706         # V
tOffs = 27          # °C
slope = -0.001721   # V/°C
tempSensor = ADC(4) # 5th ADC channel

ledBuiltin = 25
ledDuration = 50    # ms
led = Pin(ledBuiltin, Pin.OUT)
led.off()

readSensor = Timer()

rtc = machine.RTC()


def readISR(event):
    global ledStart
    ledStart = utime.ticks_ms()
    led.high()
    
    timestamp = rtc.datetime()
    (year,month,day,xxx,hour,minute,sec,xxx) = timestamp
    timestring = '%02d:%02d:%02d, %02d/%02d/%04d: '%(hour,minute,sec,month,day,year)
    
    adcRaw = tempSensor.read_u16()
    adcVolt = adcRaw * 3.3/65535
    tC = tOffs + (adcVolt - Vbe)/slope

    print(timestring + '%.2f°C, %.4fV, ADC: %d'%(tC,adcVolt,adcRaw))
  
  
readSensor.init(freq = 0.5, mode = Timer.PERIODIC, callback = readISR) # frequency in Hz, could also use period in ms

while True:
     if (led.value() == 1 and utime.ticks_diff(utime.ticks_ms(), ledStart) > ledDuration):
        led.low()
        
