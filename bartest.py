import time
import math
import board
from adafruit_dps310.advanced import DPS310
from adafruit_register.i2c_bit import RWBit
from adafruit_register.i2c_bits import RWBits

from adafruit_dps310 import advanced as adv

i2c = board.I2C()
dps310 = DPS310(i2c)
#DPS310_PRSCFG = 0b01110010
#DPS310_MEASCFG = 0b00000101
#dps310._pressure_osbits = DPS310_PRSCFG
#dps310._mode_bits = DPS310_MEASCFG


bob = adv.DPS310_Advanced(i2c)
bob.reset()
bob.pressure_rate = adv.Rate.RATE_128_HZ
bob.mode = adv.Mode.CONT_PRESSURE
bob.pressure_oversample_count = adv.SampleCount.COUNT_32

file = open("log.txt", "w")
t1 = time.time()

filterNum = 16

heights = []
for i in range(filterNum):
    heights.append(0)
times = []
for i in range(filterNum):
    times.append(0)
    
fir = []
for i in range(filterNum):
    fir.append(1/(2**(i+1)))
fir.append(1/(2**filterNum))
fir.pop(0)

lastVal = 0
lastT = 0
while(1):
    val = bob.altitude
    t = time.time()
    h = val
    for i in range(len(fir)):
        pass
        #h += fir[i] * heights[i];
    heights.append(h)
    heights.pop(0)
    times.append(t)
    times.pop(0)
    
    dV = (heights[-1] - heights[-2]) / (times[-1] - times[-2])
    #if abs(dV) > 0.00000001:
    print(str(time.time()-t1)+": " +str(dV))
    lastVal = val
    lastT = t
    time.sleep(0.05)
    

while(0):
    val = bob.altitude
    print(str(val-lastVal))
    lastVal = val
    time.sleep(0.01)



