<h1> uPy_Read_Pico_T_Sensor </h1>

<h3> Read the Raspberry Pi Pico's internal temperature sensor using a timer interrupt. Display the result using an SSD1306 OLED display. </h3>

```
read_sensor.init(freq = timer_freq, mode = Timer.PERIODIC, callback = read_ISR)
```

<br>

<img src = "./images for README/Raspberry Pi Pico pinout better.png" width = "800"/>

<br>

https://www.raspberrypi.com/documentation/microcontrollers/raspberry-pi-pico.html
