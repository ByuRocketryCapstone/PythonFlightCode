import globals as glb
from Controller import Controller
from enum import Enum

class mt_state(Enum):
    init_st = 1
    wait_enable_st = 2
    check_diff_st = 3
    move_motor_st = 4



class MotorControl:
    def __init__(self) -> None:
        self.currState = mt_state.init_st
        self.nextState = mt_state.init_st
    


    def motorInit(self) -> None:
        self.enable = False
        self.has_angle_diff = False
        self.currAngle = 0
        self.cmdAngle = 0
        self.controller = Controller(glb.KP, glb.KI, glb.KD)



    def motorTick(self) -> None:
        # state update, Mealy actions
        if (self.currState == mt_state.init_st):
            self.nextState = mt_state.wait_enable_st

        elif (self.currState == mt_state.wait_enable_st):
            if (self.enable): self.nextState = mt_state.check_diff_st
            else: self.nextState = mt_state.wait_enable_st
        
        elif (self.currState == mt_state.check_diff_st):
            if (not self.enable): self.nextState = mt_state.wait_enable_st
            elif (self.has_angle_diff): self.nextState = mt_state.move_motor_st
            else: self.nextState = mt_state.check_diff_st

        elif (self.currState == mt_state.move_motor_st):
            if (not self.enable): self.nextState = mt_state.wait_enable_st
            elif (not self.has_angle_diff): self.nextState = mt_state.check_diff_st
            else: self.nextState = mt_state.move_motor_st


        # state action, Moore actions
        if (self.currState == mt_state.init_st):
            self.motorInit()
        
        elif (self.currState == mt_state.wait_enable_st):
            pass

        elif (self.currState == mt_state.check_diff_st):
            self.updateMotorAngle()
            self.has_angle_diff = self.checkAngleDiff()
            self.stopMotor()
            
        elif (self.currState == mt_state.move_motor_st):
            self.updateMotorAngle()
            self.has_angle_diff = self.checkAngleDiff()
            self.actuateMotor()
        
        # update states
        if not(self.currState == self.nextState):
            msg = "Updated motor control state from " + str(self.currState) + " to " + str(self.nextState)
            glb.logger.queueLog(msg)
        self.currState = self.nextState
    


    def checkAngleDiff(self) -> None:
        if abs(self.cmdAngle - self.currAngle) > 0.035: # values are the same if they are within 2 degrees of each other
            return True
        return False



    def updateMotorAngle(self) -> None: 
        sd = glb.dataList[-1]
        self.cmdAngle = self.controller.calcAngle(sd.t, sd.h, sd.V, sd.a)
        #FIXME: Add code here to get the encoder value and update self.currAngle
        pass



    def actuateMotor(self) -> None:
        #FIXME: Add code here to actuate the motor
        pass



    def stopMotor(self) -> None:
        pass