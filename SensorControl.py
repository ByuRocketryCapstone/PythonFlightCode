import globals as glb
from enum import Enum
from SensorData import SensorData
import time
import math
import board
from adafruit_dps310 import advanced as adv
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
        self.fakeReader = open("data1.txt", "r") # file containing fake sensor data used for testing

    
    def sensorInit(self) -> None:
        self.enable = True
        self.log_data_flag = False   #FIXME: only for first test flight, remove for full system
        self.i2c = board.I2C()
        
        # set up i2c connection to the barometer and configure it
        self.dps310 = adv.DPS310_Advanced(self.i2c)
        #self.dps310.reset()
        #self.dps310.pressure_rate = adv.Rate.RATE_128_HZ
        #self.dps310.mode = adv.Mode.CONT_PRESSURE
        #self.dps310.pressure_oversample_count = adv.SampleCount.COUNT_4
        
        # set up i2c connection to the accelerometer
        self.bno055 = adafruit_bno055.BNO055_I2C(self.i2c)
        
        # internal counter used to determine if there is a hardware error with the sensors
        self.noneCounter = 0
        
        
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
        
        
        #log state changes
        if not(self.currState == self.nextState):
            msg = "Updated sensor control state from " + str(self.currState) + " to " + str(self.nextState)
            glb.logger.queueLog(msg, glb.loglv.TEST)
        self.currState = self.nextState
    


    def updateData(self) -> None:
        newData = self.pullData() #calls the function that pulls data from sensors
        #newData = self.getFakeData() #so if you are running fake data leave this un commented if this line is uncommented then the sensor will be on but the pi wont ask them for data
        glb.dataList.append(newData) #add new sensor data to the list
        glb.dataList.pop(0) #remove oldest data from the list
        
        if self.log_data_flag:
            msg = "Sensor Data: " + newData.__str__()
            glb.logger.queueLog(msg, glb.loglv.TEST)


    # reads from the fake data file specified in the constructor for testing the system
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

    
    # reads actual data from the sensors, filters it using an FIR filter, and stores it in the global list of sensor data
    def pullData(self) -> SensorData:
        # uses board.SCL and board.SDA
        
        # pull height data and check for sensor error
        h = self.dps310.altitude
        while h == None:
            self.noneCounter += 1
            if self.noneCounter >= 16: # if the sensor returns 16 None's in a row, then it is probably disconnected
                #glb.mainSM.abort == True
                glb.logger.queueLog("More than 16 Nones DPS 310 encountered in SensorControl::pullData, sensors are not working. Moving to abort state", 1) #FIXME: implement logging level
                sd = glb.dataList[-1]
                return sd
        self.noneCounter = 0
        
        # record current time
        t = time.time() - glb.START_TIME
        
        # pull inclination angle data and check for sensor error
        vals = self.bno055.euler
        while vals[0] == None:
            self.noneCounter += 1
            if self.noneCounter >= 16: # if the sensor returns 16 None's in a row, then it is probably disconnected
                
                glb.logger.queueLog("More than 16 Nones in BNO055 Euler encountered in SensorControl::pullData, sensors are not working. Moving to abort state", 1) #FIXME: implement logging level
                #glb.mainSM.abort_st == True
                sd = glb.dataList[-1]
                return sd
        theta = math.sqrt(vals[1]**2 + vals[2]**2) # average the x and y euler angles to get the total inclination angle
        self.noneCounter = 0
        
        # pull vertical accleration data and check for sensor error
        lin_a = self.bno055.linear_acceleration
        while lin_a[0] == None:
            self.noneCounter += 1
            if self.noneCounter >= 16: # if the sensor returns 16 None's in a row, then it is probably disconnected
                
                glb.logger.queueLog("More than 16 Nones Linear Acceleration encountered in SensorControl::pullData, sensors are not working. Moving to abort state", 1) #FIXME: implement logging level
                #glb.mainSM.abort_st == True
                sd = glb.dataList[-1]
                return sd
        self.noneCounter = 0
        a = lin_a[2] # get z-component of acceleration
        a *= math.cos(theta*(math.pi/180)) # correct acceleration value to be just the vertical component
        
        # filter the raw sensor data using an FIR filter
        h, a, theta = self.filterData(h, a, theta)
        
        dt = t - glb.dataList[-1].t
        
        # calculate the current velocity by integrating the acceleration and differentiating the height
        V_deriv = (h - glb.dataList[-1].h) / dt
        V_int = ((a + glb.dataList[-1].a) / 2) * dt
        V = (V_deriv+V_int) / 2
        
        sd = SensorData(height=h, angle=theta, accel=a, time=t, velocity=V)
        return sd
    
    
    def filterData(self, h, a, theta):
        # give 50% weight to the current measured values
        filter_h = h*0.5
        filter_a = a*0.5
        filter_theta = theta*0.5
        
        # perform FIR filtering using old data points
        for i in range(glb.dataListSize):
            filter_h += glb.FIR_COEFFS[i] * glb.dataList[i].h
            filter_a += glb.FIR_COEFFS[i] * glb.dataList[i].a
            filter_theta += glb.FIR_COEFFS[i] * glb.dataList[i].theta
        
        return filter_h, filter_a, filter_theta
            
        
        


