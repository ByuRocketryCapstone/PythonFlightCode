import globals as glb
from enum import Enum

class mt_state(Enum):
    init_st = 1
    wait_enable_st = 2
    enable_st = 3



class MotorControl:
    def __init__(self) -> None:
        self.currState = mt_state.init_st
        self.nextState = mt_state.init_st
    


    def motorInit(self) -> None:
        self.enable = False



    def motorTick(self) -> None:
        # state update, Mealy actions
        if (self.currState == mt_state.init_st):
            self.nextState = mt_state.wait_enable_st

        elif (self.currState == mt_state.wait_enable_st):
            if (self.enable): self.nextState = mt_state.enable_st
            else: self.nextState = mt_state.wait_enable_st
        
        elif (self.currState == mt_state.enable_st):
            if (not self.enable): self.nextState = mt_state.wait_enable_st
            else: self.nextState = mt_state.enable_st


        # state action, Moore actions
        if (self.currState == mt_state.init_st):
            self.motorInit()
        
        elif (self.currState == mt_state.wait_enable_st):
            pass

        elif (self.currState == mt_state.enable_st):
            self.actuateMotor()
        

        self.currState = self.nextState
    


    def actuateMotor(self) -> None:
        #FIXME: Add code here to actuate the motor
        pass