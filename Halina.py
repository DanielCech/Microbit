import math, ustruct, utime, microbit, neopixel
from microbit import sleep, pin0, pin1, pin2, pin8, pin12, pin13, pin14, pin15, pin16
from microbit import i2c
from random import randint

pins = {'P0': pin0, 'P1': pin1, 'P2': pin2, 'P8': pin8, 'P12': pin12, 'P13': pin13, 'P14': pin14, 'P15': pin15}
class PCA9685(object):
    def __init__(self, i2c, address = 0x40):
        self.address = address
        i2c.write(self.address, bytearray([0x00, 0x00]))  # reset not sure if needed but other libraries do it
        i2c.write(self.address, bytearray([0x01, 0x04]))
        i2c.write(self.address, bytearray([0x00, 0x01]))
        sleep(5)  # wait for oscillator
        i2c.write(self.address, bytearray([0x00]))  # write register we want to read from first
        mode1 = i2c.read(self.address, 1)
        mode1 = ustruct.unpack('<H', mode1)[0]
        mode1 = mode1 & ~0x10  # wake up (reset sleep)
        i2c.write(self.address, bytearray([0x00, mode1]))
        sleep(5)  # wait for oscillator
    def set_pwm_freq(self, freq_hz):
        prescaleval = 25000000.0  # 25MHz
        prescaleval /= 4096.0  # 12-bit
        prescaleval /= float(freq_hz)
        prescaleval -= 1
        prescale = int(math.floor(prescaleval + 0.5))
        i2c.write(self.address, bytearray([0x00]))  # write register we want to read from first
        oldmode = i2c.read(self.address, 1)
        oldmode = ustruct.unpack('<H', oldmode)[0]
        newmode = (oldmode & 0x7F) | 0x10  # sleep
        i2c.write(self.address, bytearray([0x00, newmode]))  # go to sleep
        i2c.write(self.address, bytearray([0xFE, prescale]))
        i2c.write(self.address, bytearray([0x00, oldmode]))
        sleep(5)
        i2c.write(self.address, bytearray([0x00, oldmode | 0x80]))
    def set_pwm(self, channel, on, off):
        if on is None or off is None:
            i2c.write(self.address, bytearray([0x06 + 4 * channel]))  # write register we want to read from first
            distance = i2c.read(self.address, 4)
            return ustruct.unpack('<HH', distance)
        i2c.write(self.address, bytearray([0x06 + 4 * channel, on & 0xFF]))
        i2c.write(self.address, bytearray([0x07 + 4 * channel, on >> 8]))
        i2c.write(self.address, bytearray([0x08 + 4 * channel, off & 0xFF]))
        i2c.write(self.address, bytearray([0x09 + 4 * channel, off >> 8]))
    def set_all_pwm(self, on, off):
        i2c.write(self.address, bytearray([0xFA, on & 0xFF]))
        i2c.write(self.address, bytearray([0xFB, on >> 8]))
        i2c.write(self.address, bytearray([0xFC, off & 0xFF]))
        i2c.write(self.address, bytearray([0xFD, off >> 8]))

pwm = PCA9685(i2c)
pwm.set_pwm_freq(50)

def servo(index, degree): #index:1~8,degree:0~180
    degree = (degree * 10 + 600) * 4096 // 20000
    pwm.set_pwm(index, 0, degree)

def get_UTdistance(trig, echo): #trig/echo:'P0'、'P1'、'P2'、'P8'、'P12'、'P13'、'P14'、'P15'
    pins[echo].write_digital(0)
    utime.sleep_us(2)
    pins[trig].write_digital(1)
    utime.sleep_us(15)
    pins[trig].write_digital(0)
    while(pins[echo].read_digital() == 0):
        pass
    time_start = utime.ticks_us()
    while pins[echo].read_digital():
        pass
    distance = ((utime.ticks_us() - time_start) / 10000) * 340 / 2
    distance = [distance, 300][distance > 300]
    return distance
    
while True:
    servo(1, 180)   #The PWM steering gear connected to pin S1 rotates to 180° position
    sleep(2000)
    servo(1, 0)     #The PWM steering gear connected to pin S1 rotates to the 0° position
    sleep(2000)
    
