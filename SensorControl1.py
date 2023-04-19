import globals as glb
from enum import Enum
from SensorData import SensorData
import time
import math
import board
from adafruit_dps310.advanced import DPS310
import adafruit_dps310.advanced as adv
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
        self.fakeReader = open("data1.txt", "r")
        self.fakeDataTick = 0
        #Above is the set up for the important states and the fake test data to open the file amd set the Tick 

    
    def sensorInit(self) -> None:
        self.enable = True
        self.i2c = board.I2C()
        
#         self.dps310.reset()

        
        self.dps310 = adv.DPS310_Advanced(self.i2c)
        self.dps310.pressure_rate = adv.Rate.RATE_128_HZ
        
        self.dps310.mode = adv.Mode.CONT_PRESSURE
        self.dps310.pressure_oversample_count = adv.SampleCount.COUNT_1
        self.bno055 = adafruit_bno055.BNO055_I2C(self.i2c)
        self.noneCounter = 0
        # Setting up the i2c for the sensor board and this also creates the sensor objects for both the DPS and BNO055 also sets up the none counter which will be explained later 
        
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
        newData = self.pullData() #calls the function that pulls data from sensors
        #newData = self.getFakeData() #so if you are running fake data leave this un commented if this line is uncommented then the sensor will be on but the pi wont ask them for data
        glb.dataList.append(newData)
        glb.dataList.pop(0) #add new data to the list 
        #print(len(glb.dataList))

        
        msg = "Sensor Data: " + newData.__str__()
        glb.logger.queueLog(msg, glb.loglv.TEST)
        #fake data tick rate

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
        # This is is just for the fake data where it reads the file amd then pulls out the data and creates the sd data object which the controller reads


    def pullData(self) -> SensorData:
        # uses board.SCL and board.SDA
        #implement simple averaging filter to reduce noise in sensor data
        avgNum = 1
        
        # pull and filter height data
        h = 0
        for i in range(avgNum):
            val = self.dps310.altitude
            if val == None:
                 i -= 1
                 continue
            h += val
        h/= avgNum;
        
        # record current time
        t = time.time() - glb.START_TIME
        
        # pull and filter inclination angle data
        theta = 0
        for i in range(avgNum):
            vals = self.bno055.euler
            if vals[0] == None:
                i -= 1
                continue
            theta += math.sqrt(vals[1]**2 + vals[2]**2)
        theta /= avgNum
        
        # pull and filter accleration data
        a = 0
        for i in range(avgNum):
            lin_a = self.bno055.linear_acceleration
            if lin_a[0] == None:
                i -= 1
                continue
            a += lin_a[2]
        a /= avgNum
        a *= math.cos(theta*(math.pi/180)) # correct acceleration value to be just the vertical component
        
        
        dt = t - glb.dataList[-1].t
        V = 0
            
        #Below is the none counter, this prevents the program from crashing if the sensor accidently return a "none". This also tells the system to go into retract mode so that the paddles close and the controller shuts down so it dosent try to run with broken sensors. 
        if(a == None):
            self.noneCounter += 1
            if(self.noneCounter == 16):
                glb.mainSM.abort = True                
        else:
            self.noneCounter = 0
            
                
        if (a == None):
            sd = glb.dataList[-1]
            sd.t = t
            return sd
        # This tells the PI to take the last sucessful line of data and ignore the string of nones
        else:
            V_deriv = (h - glb.dataList[-1].h) / dt
            V_int = ((a + glb.dataList[-1].a) / 2) * dt
        
            V = (V_deriv+V_int) / 2
            
            
        
        sd = SensorData(height=h, angle=theta, accel=a, time=t, velocity=V)
        
        return sd

