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


# enum of the states in sensor control
class sn_state(Enum):
    init_st = 1
    wait_enable_st = 2
    pull_data_st = 3



# Class that implements the sensor control state machine. This state machine controls the operation of the barometer and acclerometer sensors during
# flight. This state machine can pull data from the actual sensors during flight, and it can also pull fake data from a file for testing.

class SensorControl:
    def __init__(self) -> None:
        self.currState = sn_state.init_st 
        self.nextState = sn_state.init_st
        
        self.fakeReader = open("data1.txt", "r")
        self.fakeDataTick = 0
        #Above is the set up for the important states and the fake test data to open the file amd set the Tick 

    
    def sensorInit(self) -> None:
        self.enable = True
        self.i2c = board.I2C() # enable I2C connection to the sensors
        
        self.dps310 = adv.DPS310_Advanced(self.i2c) # setup DPS310 barometer object
        self.dps310.pressure_rate = adv.Rate.RATE_128_HZ # set sampling rate to highest value
        self.dps310.mode = adv.Mode.CONT_PRESSURE # only take pressure data (not temperature)
        self.dps310.pressure_oversample_count = adv.SampleCount.COUNT_1 # only take one sample per refresh
        
        self.bno055 = adafruit_bno055.BNO055_I2C(self.i2c) # setup BNO055 acclerometer
        
        self.noneCounter = 0 # used for counting when the sensors return None values
        
        
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
        
        
        # log when state is changed
        if not(self.currState == self.nextState):
            msg = "Updated sensor control state from " + str(self.currState) + " to " + str(self.nextState)
            glb.logger.queueLog(msg, glb.loglv.TEST)
            
        # update state
        self.currState = self.nextState
    

    # get new sensor data and store it in the global data list (can pull from sensors or fake data file)
    def updateData(self) -> None:
        newData = self.pullData() #calls the function that pulls data from sensors
        #newData = self.getFakeData() # calls the function that pulls data from the fake data file for testing
        
        # add new data to the global list and remove old data
        glb.dataList.append(newData)
        glb.dataList.pop(0)

        # log data that was pulled
        msg = "Sensor Data: " + newData.__str__()
        glb.logger.queueLog(msg, glb.loglv.TEST)


    # get a line of data from the fake data file and return it as a Sensor Data object
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


    # get a set of data from the physical sensors
    def pullData(self) -> SensorData:
        
        # pull height data
        h = self.dps310.altitude
        while h == None: # if sensors return too many Nones in a row then they probably got disconnected, abort system
            if self.noneCounter >= 16:
                glb.mainSM.abort = True
                glb.logger.queueLog("More than 16 Nones read in pullData, moving to abort", 1) #FIXME: implement logging level
                return glb.dataList[-1]
            self.noneCounter += 1
            h = self.dps310.altitude
        self.noneCounter = 0
        
        # record current time
        t = time.time() - glb.START_TIME
        
        # pull inclination angle data
        vals = self.bno055.euler
        while vals[0] == None: # if sensors return too many Nones in a row then they probably got disconnected, abort system
            if self.noneCounter >= 16:
                glb.mainSM.abort = True
                glb.logger.queueLog("More than 16 Nones read in pullData, moving to abort", 1) #FIXME: implement logging level
                return glb.dataList[-1]
            self.noneCounter += 1
            vals = self.bno055.euler
        theta = math.sqrt(vals[1]**2 + vals[2]**2) # pythagorean average of the x and y angles gives the vertical inclination angle
        self.noneCounter = 0
        
        # pull accleration data
        a = self.bno055.linear_acceleration
        while a[0] == None: # if sensors return too many Nones in a row then they probably got disconnected, abort system
            if self.noneCounter >= 16:
                glb.mainSM.abort = True
                glb.logger.queueLog("More than 16 Nones read in pullData, moving to abort", 1) #FIXME: implement logging level
                return glb.dataList[-1]
            self.noneCounter += 1
            a = self.bno055.linear_acceleration
        a = a[2] # get z component of the acceleration (along the rocket body axis
        a *= math.cos(theta*(math.pi/180)) # correct acceleration value to be just the vertical component
        self.noneCounter = 0
        
        # do a numerical integral and derivative to calculate the current velocity
        # FIXME: implement a better integral and derivative than this. This is a first order backwards derivative and a trapezoidal integral
        dt = t - glb.dataList[-1].t
        V_deriv = (h - glb.dataList[-1].h) / dt
        V_int = ((a + glb.dataList[-1].a) / 2) * dt
        V = (V_deriv+V_int) / 2
        
        sd = SensorData(height=h, angle=theta, accel=a, time=t, velocity=V)
        return sd

