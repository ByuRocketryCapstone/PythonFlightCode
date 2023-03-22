import globals as glb
from Controller import Controller
from enum import Enum
import time
import board
import digitalio
import spidev


class mt_state(Enum):
    init_st = 1
    wait_enable_st = 2
    check_diff_st = 3
    move_motor_st = 4
    retract_st = 5



class MotorControl:
    def __init__(self) -> None:
        self.currState = mt_state.init_st
        self.nextState = mt_state.init_st
    


    def motorInit(self) -> None:
        
        # enable SPI communication with the encoder
        bus = 0
        device = 0
        self.spi = spidev.SpiDev()
        self.spi.open(bus, device)
        self.spi.max_speed_hz = 500000
        self.spi.mode = 0
        
        # enable GPIO connection with the Teensy 4.0 to drive the motor
        self.motor_enable = digitalio.DigitalInOut(board.D12)
        self.motor_enable.direction = digitalio.Direction.OUTPUT
        self.motor_spin = digitalio.DigitalInOut(board.D13)
        self.motor_spin.direction = digitalio.Direction.OUTPUT
        self.limit_switch = digitalio.DigitalInOut(board.D0)
        self.limit_switch.direction = digitalio.Direction.INPUT
        
        # set up class variables
        self.enable = True
        self.retract = False
        self.has_angle_diff = False
        self.prevMotorAngle = 0
        self.numTurns = 0
        self.currMotorAngle = 0
        self.cmdAngle = 0
        self.currPaddleAngle = 0
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
            elif (self.retract): self.nextState = mt_state.retract_st
            elif (self.has_angle_diff): self.nextState = mt_state.move_motor_st
            else: self.nextState = mt_state.check_diff_st

        elif (self.currState == mt_state.move_motor_st):
            if (not self.enable): self.nextState = mt_state.wait_enable_st
            elif (self.retract): self.nextState = mt_state.retract_st
            elif (not self.has_angle_diff): self.nextState = mt_state.check_diff_st
            else: self.nextState = mt_state.move_motor_st
        
        elif (self.currState == mt_state.retract_st):
            if (not self.enable): self.nextState = mt_state.wait_enable_st


        # state action, Moore actions
        if (self.currState == mt_state.init_st):
            self.motorInit()
        
        elif (self.currState == mt_state.wait_enable_st):
            pass

        elif (self.currState == mt_state.check_diff_st):
            self.updatePaddleAngle()
            self.has_angle_diff = self.checkAngleDiff()
            self.stopMotor()
            
        elif (self.currState == mt_state.move_motor_st):
            self.updatePaddleAngle()
            self.has_angle_diff = self.checkAngleDiff()
            self.actuateMotor()
        
        elif(self.currState == mt_state.retract_st):
            self.updatePaddleAngle()
            self.retractPaddles()
        
        # update states
        if not(self.currState == self.nextState):
            msg = "Updated motor control state from " + str(self.currState) + " to " + str(self.nextState)
            glb.logger.queueLog(msg, glb.loglv.TEST)
        self.currState = self.nextState
        #print(self.currState)
    


    def checkAngleDiff(self) -> None:
        if abs(self.cmdAngle - self.currPaddleAngle) > 1: # values are the same if they are within 2 degrees of each other
            return True
        return False
    
    
    
    def updatePaddleAngle(self):
        # Run PID controller to calculate a desired paddle angle based on current sensor data
        sd = glb.dataList[-1]
        self.cmdAngle = self.controller.calcAngle(sd.t, sd.h, sd.V, sd.a)
        self.cmdAngle = 30
        
        # Convert the motor rotation angle to a corresponding paddle angle
        self.updateMotorAngle()
        self.currPaddleAngle = self.motorAngletoPaddleAngle(self.currMotorAngle)
    
    
    
    def motorAngletoPaddleAngle(self,motorAngle):
        #FIXME: Insert Connor's fun angle equation here
        paddleAngle = (3*10**-11)*(motorAngle)**3 - (8*10**-7)*(motorAngle)**2 + 0.0114*(motorAngle) + 1.9741 
        return paddleAngle



    def updateMotorAngle(self) -> None:
        # Run spi command to retrieve encoder data
        # See AMT22 Encoder datasheet
        
        
        msg = [0x0, 0x0]
        self.spi.xfer2(msg) 
    
        msg[0] = msg[0] & 0x3F   # Set first two checksum bits to 0
        msg[0] <<= 8   # Left shift first response byte to pad it out to 16 bits
        pos = msg[0] | msg[1]   # Concatenate the two response bytes using bitwise OR 
        value = pos*(360/16384)
        #print(value)
        
       
        #print("")# Convert encoder position to angle in degrees
        prev = self.prevMotorAngle - 360*self.numTurns
        
        
        # Check if motor changed from 0 to 360 or vice versa and update numTurns
        if prev > 330 and value < 30:
            self.numTurns += 1
        elif prev < 30 and value > 330:
            self.numTurns -= 1
        
        # Update angle values
        self.prevMotorAngle = self.currMotorAngle
        #print(self.prevMotorAngle)
        
        self.currMotorAngle = value + 360*self.numTurns
        glb.logger.queueLog("angle: " + str(self.currMotorAngle), 1)



    def actuateMotor(self) -> None:        
        if (self.limit_switch.value == False):  
            self.motor_enable.value = True
            
        
            if(self.cmdAngle > self.currPaddleAngle):
                self.motor_spin.value = False
        
            elif(self.cmdAngle < self.currPaddleAngle):
                self.motor_spin.value = True
            
        elif (self.limit_switch.value == True and self.cmdAngle > self.currPaddleAngle):
            self.motor_enable.value = True
            self.motor_spin.value = False
            
            
        elif (self.limit_switch.value == True and self.cmdAngle < self.currPaddleAngle):
            self.motor_enable.value = False



    def stopMotor(self) -> None:
        self.motor_enable.value = False

    
    
    def retractPaddles(self):
        if(self.limit_switch.value == False):
            self.motor_enable.value = True
            self.motor_spin.value = True
        else:
            self.motor_enable.value = False
            self.enable = False
            self.retract = False
        
        
