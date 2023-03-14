import globals as glb
from enum import Enum
from SensorData import SensorData
# import adafruit_bno055
# import adafruit_dps310_advanced as DPS310
# import BNO055 as BNO055
import time
# import board #whatever board we are using 

class sn_state(Enum):
    init_st = 1
    wait_enable_st = 2
    pull_data_st = 3


class SensorControl:
    def __init__(self) -> None:
        self.currState = sn_state.init_st
        self.nextState = sn_state.init_st
        self.fakeReader = open("fakeData.txt", "r")
        self.fakeDataTick = 0
    

    
    def sensorInit(self) -> None:
        self.enable = False



    def sensorTick(self) -> None:
        # state update, Mealy actions
        if (self.currState == sn_state.init_st):
            self.nextState = sn_state.wait_enable_st

        elif (self.currState == sn_state.wait_enable_st):
            if (self.enable): self.nextState = sn_state.pull_data_st
            else: self.nextState = sn_state.wait_enable_st
        
        elif (self.currState == sn_state.pull_data_st):
            if (not self.enable): self.nextState = sn_state.wait_enable_st
            else: self.nextState = sn_state.pull_data_st


        # state actions, Moore actions
        if (self.currState == sn_state.init_st):
            self.sensorInit()
        
        elif (self.currState == sn_state.wait_enable_st):
            pass

        elif (self.currState == sn_state.pull_data_st):
            self.updateData()
        

        if not(self.currState == self.nextState):
            msg = "Updated sensor control state from " + str(self.currState) + " to " + str(self.nextState)
            glb.logger.queueLog(msg, glb.loglv.TEST)
        self.currState = self.nextState
    


    def updateData(self) -> None:
        newData = self.pullData()
        glb.dataList.append(newData)
        glb.dataList.pop(0)

        self.fakeDataTick += 1
        if (self.fakeDataTick >= 10):
            msg = "Sensor Data: " + newData.__str__()
            glb.logger.queueLog(msg, glb.loglv.TEST)
            self.fakeDataTick = 0
    

    def getFakeData(self):
        line = self.fakeReader.readline()
        vals = line.split()
        t = float(vals[0])
        h = float(vals[1])
        V = float(vals[2])
        a = float(vals[3])
        theta = float(vals[4])

        sd = SensorData(height=h, velocity=V, accel=a, angle=theta, time=t)            
        return sd


    def pullData(self) -> SensorData:
        # @Jacob, insert CircuitPy code here to get sensor data, and then return a SensorData object
        sd = self.getFakeData()
        return sd
        # i2c = board.I2C()

        # dps310 = DPS310(i2c)
        # bno055 = adafruit_bno055.BNO055_I2C(i2c)

        # self.currHeight = dps310.altitude
        # self.currAccel = bno055.linear_acceleration
        # self.eulerAngle = bno055.euler




        sd = SensorData(self.currHeight,0,self.currAccel,0,0)
        return sd