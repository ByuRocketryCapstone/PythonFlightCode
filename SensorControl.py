import globals as glb
from enum import Enum
from SensorData import SensorData
import time
import board
from adafruit_dps310.advanced import DPS310
import adafruit_bno055
import busio 



class sn_state(Enum):
    init_st = 1
    wait_enable_st = 2
    pull_data_st = 3


class SensorControl:
    def __init__(self) -> None:
        self.currState = sn_state.init_st
        self.nextState = sn_state.init_st
        self.runFakeDataFlag = False
        self.fakeReader = open("fakeData.txt", "r")
        self.fakeDataTick = 0
    

    
    def sensorInit(self) -> None:
        self.enable = True
        self.i2c = board.I2C()
        self.dps310 = DPS310(self.i2c)
        self.bno055 = adafruit_bno055.BNO055_I2C(self.i2c)


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
        # newData = self.getFakeData()
        glb.dataList.append(newData)
        glb.dataList.pop(0)
        #print(len(glb.dataList))

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
           # uses board.SCL and board.SDA
        
        h = self.dps310.altitude
        theta = self.bno055.euler
        theta = theta[1]
        #a = self.bno055.acceleration
        lin_a = self.bno055.linear_acceleration
        #print(lin_a)
        a = lin_a[2]
    
        t = time.time() - glb.START_TIME
        
        
        dt = t - glb.dataList[-1].t
        V = 0
        if (a == None):
            sd = glb.dataList[-1]
            sd.t = t
            return sd
        else:
            V_deriv = (h - glb.dataList[-1].h) / dt
            V_int = ((a + glb.dataList[-1].a) / 2) * dt
        
            V = (V_deriv+V_int) / 2
        
        sd = SensorData(height=h, angle=theta, accel=a, time=t, velocity=V)
        
        return sd


