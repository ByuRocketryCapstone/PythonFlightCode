import globals as glb
from enum import Enum
import time


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
            if(self.abort == True):
                self.nextState = mn_state.abort_st
            
            elif (self.armed): 
                self.nextState = mn_state.arm_st
                glb.sensorControl.enable = True
            else: self.nextState = mn_state.wait_arm_st
        
        elif (self.currState == mn_state.arm_st):
            if(self.abort == True):
                self.nextState = mn_state.abort_st
            elif (self.ignition): self.nextState = mn_state.wait_cutoff_st
            else: self.nextState = mn_state.arm_st
            
        elif (self.currState == mn_state.wait_cutoff_st):
            if(self.abort == True):
                self.nextState = mn_state.abort_st
            elif (self.cutoff): 
                self.nextState = mn_state.wait_apogee_st
                glb.motorControl.enable = True
            else: self.nextState = mn_state.wait_cutoff_st

        elif (self.currState == mn_state.wait_apogee_st):
            if(self.abort == True):
                self.nextState = mn_state.abort_st 
            elif (self.apogee):
                self.nextState = mn_state.retract_st
                glb.motorControl.retract = True
            else: self.nextState = mn_state.wait_apogee_st

        elif (self.currState == mn_state.retract_st):
            if(self.abort == True):
                self.nextState = mn_state.abort_st
            elif (self.retracted): 
                self.nextState = mn_state.descent_st
                glb.motorControl.enable = False
            else: self.nextState = mn_state.retract_st

        elif (self.currState == mn_state.descent_st):
            if(self.abort == True):
                self.nextState = mn_state.abort_st
            elif (self.ground): 
                self.nextState = mn_state.done_st
                glb.sensorControl.enable = False
            else: self.nextState = mn_state.descent_st

        elif (self.currState == mn_state.done_st):
            if(self.abort == True):
                self.nextState = mn_state.abort_st
            elif(self.reset): 
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
            if (1): #FIXME: Replace with code that senses when arming pin has been removed
                self.armed = True
            
            # Exectute state machine actions
            pass    
            #FIXME: Add code to set indicator LED color

        elif (self.currState == mn_state.arm_st):
            # Check for setting next flag
            if (self.getChangeValue("V") > 10):
                self.ignition = True
            
            # Exectute state machine actions
            pass    
            #FIXME: Add code to set indicator LED color

        elif (self.currState == mn_state.wait_cutoff_st):
            # Check for setting next flag
            if (self.getChangeValue("a") < -2):
                self.cutoff = True
                glb.CUTOFF_TIME = time.time()

            # Exectute state machine actions
            pass
            #FIXME: Add code to turn off LED indicator

        elif (self.currState == mn_state.wait_apogee_st):
            # Check for setting next flag
            if (self.getChangeValue("V") < 5):
                self.apogee = True

            # Exectute state machine actions
            pass

        elif (self.currState == mn_state.retract_st):

            # Exectute state machine actions
            pass

        elif (self.currState == mn_state.descent_st):
            # Check for setting next flag
            if (self.getChangeValue("V") > -2):
                self.ground = True
            
            # Exectute state machine actions
            pass

        elif (self.currState == mn_state.done_st):
            # Check for setting next flag
            if (0): #FIXME: Replace with code that senses when the reset button has been pushed
                self.reset = True

            # Exectute state machine actions
            pass

        elif (self.currState == mn_state.abort_st):
            glb.motorControl.retract = True
            
            pass
    

        if not(self.currState == self.nextState):
            msg = "Updated main state from " + str(self.currState) + " to " + str(self.nextState)
            glb.logger.queueLog(msg, glb.loglv.TEST)
        self.currState = self.nextState
        
    
    # Gets an average of the 5 most recent sensor values of the specified type, helps to guard against noise
    def getChangeValue(self, dataType):
        val = 0
        avgNum = 5
        
        if dataType == "V":
            for i in range(1,avgNum+1):
                val += glb.dataList[-i].V
            val /= avgNum
        elif dataType == "a":
            for i in range(1,avgNum+1):
                val += glb.dataList[-i].a
            val /= avgNum
        elif dataType == "h":
            for i in range(1,avgNum+1):
                val += glb.dataList[-i].h
            val /= avgNum
        elif dataType == "t":
            for i in range(1,avgNum+1):
                val += glb.dataList[-i].t
            val /= avgNum
        else:
            print("Specified dataType not recognized: " + str(dataType))
        
        return val
            




