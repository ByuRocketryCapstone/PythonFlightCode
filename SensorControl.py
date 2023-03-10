import globals as glb
import SensorData
import adafruit_bno055
import adafruit_dps310_advanced as DPS310
import BNO055 as BNO055
import time
import board #whatever board we are using 

class SensorControl:
    def __init__(self):
        pass

    def sensorTick(self):
        pass

    def pullData(self):
        # @Jacob, insert CircuitPy code here to get sensor data, and then return a SensorData object
        i2c = board.I2C()

        dps310 = DPS310(i2c)
        bno055 = adafruit_bno055.BNO055_I2C(i2c)

        self.currHeight = dps310.altitude
        self.currAccel = bno055.linear_acceleration
        self.eulerAngle = bno055.euler




        sd = SensorData(self.currHeight,0,self.currAccel,0,0)
        return sd