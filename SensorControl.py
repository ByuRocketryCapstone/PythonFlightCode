import globals as glb
from enum import Enum
import SensorData

class sn_state(Enum):
    init_st = 1
    wait_enable_st = 2
    pull_data_st = 3


class SensorControl:
    def __init__(self) -> None:
        self.currState = sn_state.init_st
        self.nextState = sn_state.init_st
    

    
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
        

        self.currState = self.nextState
    


    def updateData(self) -> None:
        newData = self.pullData()
        glb.dataList.append(newData)
        glb.dataList.pop(0)


    def pullData(self) -> SensorData:
        # @Jacob, insert CircuitPy code here to get sensor data, and then return a SensorData object
        sd = SensorData(0,0,0,0,0)
        return sd