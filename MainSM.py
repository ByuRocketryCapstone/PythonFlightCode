import globals as glb
from enum import Enum


class state(Enum):
    init_st = 1
    wait_arm_st = 2
    arm_st = 3
    wait_cutoff_st = 4
    wait_apogee_st = 5
    retract_st = 6
    descent_st = 7
    done_st = 8
    abort_st = 9


class mainStateMachine:
    def __init__(self):
        self.currState = state.init_st
        self.nextState = state.init_st
        self.mainInit()

    def mainInit(self):
        self.armed = False
        self.ignition = False
        self.cutoff = False
        self.apogee = False
        self.retracted = False
        self.ground = False
        self.done = False
        self.abort = False
        self.reset = False

    def mainTick(self):

        # state update, Mealy actions
        if (self.currState == state.init_st):
            self.nextState = state.wait_arm_st

        elif (self.currState == state.wait_arm_st):
            if (self.armed): self.nextState = state.arm_st
            else: self.nextState = state.wait_arm_st
        
        elif (self.currState == state.arm_st):
            if (self.ignition): self.nextState = state.wait_cutoff_st
            else: self.nextState = state.arm_st
            
        elif (self.currState == state.wait_cutoff_st):
            if (self.cutoff): self.nextState = state.wait_apogee_st
            else: self.nextState = state.wait_cutoff_st

        elif (self.currState == state.wait_apogee_st):
            if (self.apogee): self.nextState = state.retract_st
            else: self.nextState = state.wait_apogee_st

        elif (self.currState == state.retract_st):
            if (self.retracted): self.nextState = state.descent_st
            else: self.nextState = state.retract_st

        elif (self.currState == state.descent_st):
            if (self.ground): self.nextState = state.done_st
            else: self.nextState = state.descent_st

        elif (self.currState == state.done_st):
            if(self.reset): 
                self.nextState = state.wait_arm_st
                self.mainInit()
            else: self.nextState = state.done_st

        elif (self.currState == state.abort_st):
            if(self.reset): 
                self.nextState = state.wait_arm_st
                self.mainInit()
            else: self.nextState = state.abort_st


        # state action, Moore actions
        if (self.currState == state.init_st):
            pass
        elif (self.currState == state.wait_arm_st):
            pass
        elif (self.currState == state.wait_cutoff_st):
            pass
        elif (self.currState == state.wait_apogee_st):
            pass
        elif (self.currState == state.retract_st):
            pass
        elif (self.currState == state.descent_st):
            pass
        elif (self.currState == state.done_st):
            pass
        elif (self.currState == state.abort_st):
            pass
    




