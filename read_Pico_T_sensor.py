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

https://codefather.tech/blog/if-name-main-python/
'''

from machine import Pin, ADC, Timer
import utime as time
from micropython import const
import ssd1306_display_module as display

def read_T():
    # internal T sensor
    temp_sensor = ADC(4) # 5th ADC channel
    Vbe = 0.706         # V
    T_offs = 27         # °C
    slope = -0.001721   # V/°C

    adc_raw = temp_sensor.read_u16()
    adc_volt = adc_raw * 3.3/65535
    T_C = T_offs + (adc_volt - Vbe)/slope
    return T_C, adc_volt, adc_raw
    
def read_ISR(event):
    global led, led_start, rtc, oled
    led_start = time.ticks_ms()
    led.high()
    
    timestamp = rtc.datetime()
    (year,month,day,xxx,hour,minute,sec,xxx) = timestamp
    timestring = '%02d:%02d:%02d, %02d/%02d/%04d: '%(hour, minute, sec, month, day, year)
    
    T_C, adc_volt, adc_raw = read_T()
    display.disp_string(oled, 5, 5, ('%.1f C' %(T_C)))
    print(timestring + '%.2f°C, %.4fV, ADC: %d'%(T_C, adc_volt, adc_raw))
   
def main():
    global led, rtc, oled
    
    # I2C OLED setup
    SCL_PIN = const(5)
    SDA_PIN = const(4)
    WIDTH  = 128                                          
    HEIGHT = 32

    oled = display.disp_setup(SCL_PIN, SDA_PIN, WIDTH, HEIGHT)

    # LED setup
    led_builtin = 25
    led_duration = 50    # ms
    led = Pin(led_builtin, Pin.OUT, value = 0)

    timer_freq = 0.5     # timer interrupt frequency (Hz)
    read_sensor = Timer()

    rtc = machine.RTC()

    read_sensor.init(freq = timer_freq, mode = Timer.PERIODIC, callback = read_ISR) # frequency in Hz ... could also use period in ms

    # display initial sensor reading
    T_C, adc_volt, adc_raw = read_T()
    display.disp_string(oled, 5, 5, ('%.1f C' %(T_C)))
    timestamp = rtc.datetime()
    (year,month,day,xxx,hour,minute,sec,xxx) = timestamp
    timestring = '%02d:%02d:%02d, %02d/%02d/%04d: '%(hour, minute, sec, month, day, year)
    print(timestring + '%.2f°C, %.4fV, ADC: %d'%(T_C, adc_volt, adc_raw))

    # loop ...
    while True:
        # turn off the LED
        if (led.value() == 1 and time.ticks_diff(time.ticks_ms(), led_start) > led_duration):
            led.low() 


if __name__ == '__main__':
    main()

