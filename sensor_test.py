import time
import board
from adafruit_dps310.advanced import DPS310
import adafruit_bno055
import busio


i2c = board.I2C()   # uses board.SCL and board.SDA

dps310 = DPS310(i2c)
bno055 = adafruit_bno055.BNO055_I2C(i2c)

last_val = 0xFFFF



while True:
    print("Temperature = %.2f *C"%dps310.temperature)
    print("Pressure = %.2f hPa"%dps310.pressure)
    print("")
    print("Temperature: {} degrees C".format(bno055.temperature))


    print("Accelerometer (m/s^2): {}".format(bno055.acceleration))
    print("Magnetometer (microteslas): {}".format(bno055.magnetic))
    print("Gyroscope (rad/sec): {}".format(bno055.gyro))
    print("Euler angle: {}".format(bno055.euler))
    print("Quaternion: {}".format(bno055.quaternion))
    print("Linear acceleration (m/s^2): {}".format(bno055.linear_acceleration))
    print("Gravity (m/s^2): {}".format(bno055.gravity))
    print()

    time.sleep(0.01)