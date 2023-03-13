import globals as glb
from enum import Enum


class mn_state(Enum):
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
        self.currState = mn_state.init_st
        self.nextState = mn_state.init_st

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
        if (self.currState == mn_state.init_st):
            self.nextState = mn_state.wait_arm_st

        elif (self.currState == mn_state.wait_arm_st):
            if (self.armed): 
                self.nextState = mn_state.arm_st
                glb.sensorControl.enable = True
            else: self.nextState = mn_state.wait_arm_st
        
        elif (self.currState == mn_state.arm_st):
            if (self.ignition): self.nextState = mn_state.wait_cutoff_st
            else: self.nextState = mn_state.arm_st
            
        elif (self.currState == mn_state.wait_cutoff_st):
            if (self.cutoff): 
                self.nextState = mn_state.wait_apogee_st
                glb.motorControl.enable = True
            else: self.nextState = mn_state.wait_cutoff_st

        elif (self.currState == mn_state.wait_apogee_st):
            if (self.apogee): self.nextState = mn_state.retract_st
            else: self.nextState = mn_state.wait_apogee_st

        elif (self.currState == mn_state.retract_st):
            if (self.retracted): 
                self.nextState = mn_state.descent_st
                glb.motorControl.enable = False
            else: self.nextState = mn_state.retract_st

        elif (self.currState == mn_state.descent_st):
            if (self.ground): 
                self.nextState = mn_state.done_st
                glb.sensorControl.enable = False
            else: self.nextState = mn_state.descent_st

        elif (self.currState == mn_state.done_st):
            if(self.reset): 
                self.nextState = mn_state.wait_arm_st
                self.mainInit()
            else: self.nextState = mn_state.done_st

        elif (self.currState == mn_state.abort_st):
            if(self.reset): 
                self.nextState = mn_state.wait_arm_st
                self.mainInit()
            else: self.nextState = mn_state.abort_st



        # state action, Moore actions
        if (self.currState == mn_state.init_st):
            self.mainInit()
        elif (self.currState == mn_state.wait_arm_st):
            # Check for setting next flag
            if (0): #FIXME: Replace with code that senses when arming pin has been removed
                self.armed = True
            
            # Exectute state machine actions
            pass    
            #FIXME: Add code to set indicator LED color

        elif (self.currState == mn_state.arm_st):
            # Check for setting next flag
            if (glb.dataList[-1].V > 1):
                self.ignition = True
            
            # Exectute state machine actions
            pass    
            #FIXME: Add code to set indicator LED color

        elif (self.currState == mn_state.wait_cutoff_st):
            # Check for setting next flag
            if (glb.dataList[-1].a < 0):
                self.cutoff = True

            # Exectute state machine actions
            pass
            #FIXME: Add code to turn off LED indicator

        elif (self.currState == mn_state.wait_apogee_st):
            # Check for setting next flag
            if (glb.dataList[-1].V < 1):
                self.apogee = True

            # Exectute state machine actions
            pass
            #FIXME: Add code to enable actuating the motor
            # Add code to enable the controller

        elif (self.currState == mn_state.retract_st):
            # Check for setting next flag
            if (0): #FIXME: Replace with code that senses when the paddles are retracted
                self.retracted = True

            # Exectute state machine actions
            pass
            #FIXME: Add code to disable the controller

        elif (self.currState == mn_state.descent_st):
            # Check for setting next flag
            if (glb.dataList[-1] > -1):
                self.ground = True
            
            # Exectute state machine actions
            pass
            #FIXME: Add code to disable actuating the motor

        elif (self.currState == mn_state.done_st):
            # Check for setting next flag
            if (0): #FIXME: Replace with code that senses when the reset button has been pushed
                self.reset = True

            # Exectute state machine actions
            pass

        elif (self.currState == mn_state.abort_st):
            pass
    

        if not(self.currState == self.nextState):
            msg = "Updated motor state from " + str(self.currState) + " to " + str(self.nextState)
            glb.logger.queueLog(msg)
        self.currState = self.nextState




