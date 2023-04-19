import globals as glb
from Controller import Controller
from enum import Enum
import time
import board
import digitalio
import spidev


# enum of all the motor control states
class mt_state(Enum):
    init_st = 1
    wait_enable_st = 2
    check_diff_st = 3
    move_motor_st = 4
    retract_st = 5


# Class implementing the motor control state machine. This state machine controls the operation of the stepper motor to deploy or retract the paddles. It
# uses the PID controller to determine the desired angle at each time step, and an absolute value encoder to determine the current angle.

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
        self.enable = False
        self.retract = False
        self.has_angle_diff = False
        self.prevMotorAngle = 0
        self.numTurns = 0
        self.currMotorAngle = 0
        self.cmdAngle = 0
        self.currPaddleAngle = 0
        
        self.controller = Controller(glb.KP, glb.KI, glb.KD) # this is the PID controller



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
            self.stopMotor()

        elif (self.currState == mt_state.check_diff_st):
            self.updatePaddleAngle()
            self.has_angle_diff = self.checkAngleDiff()
            self.stopMotor()
            
        elif (self.currState == mt_state.move_motor_st):
            self.updatePaddleAngle()
            self.has_angle_diff = self.checkAngleDiff()
            self.actuateMotor()
        
        elif(self.currState == mt_state.retract_st):
            self.updateMotorAngle()
            self.retractPaddles()

        
        # update states
        if not(self.currState == self.nextState):
            msg = "Updated motor control state from " + str(self.currState) + " to " + str(self.nextState)
            glb.logger.queueLog(msg, glb.loglv.TEST)
        self.currState = self.nextState
    


    # checks to see if the system has achieved the desired paddle angle
    def checkAngleDiff(self) -> None:
        if abs(self.cmdAngle - self.currPaddleAngle) > 1: # values are the same if they are within 1 degree of each other
            return True
        return False
    
    
    
    def updatePaddleAngle(self):
        # Run PID controller to calculate a desired paddle angle based on current sensor data
        curr_t = glb.dataList[-1].t - glb.CUTOFF_TIME
        curr_h = self.getCurrData("h")
        curr_V = self.getCurrData("V")
        curr_a = self.getCurrData("a")
        self.cmdAngle = self.controller.calcAngle(curr_t, curr_h, curr_V, curr_a)

        # Convert the motor rotation angle to a corresponding paddle angle
        self.updateMotorAngle()
        self.currPaddleAngle = self.motorAngletoPaddleAngle(self.currMotorAngle)
    
    
    
    def motorAngletoPaddleAngle(self,motorAngle):
        # This is a third order polynomial curve fit of the paddle angle in degrees as a function of motor angle in degrees
        # We didn't want to do the kinematics, so we took data of paddle and motor angles and just curve fit it
        paddleAngle = (3*10**-11)*(motorAngle)**3 - (8*10**-7)*(motorAngle)**2 + 0.0114*(motorAngle) + 1.9741 
        return paddleAngle


    
    # get the current rotation angle of the motor from the encoder
    def updateMotorAngle(self) -> None:
        # Run spi command to retrieve encoder data
        # See AMT22 Encoder datasheet for more details on reading from encoder
        
        
        msg = [0x0, 0x0] # create message buffer
        self.spi.xfer2(msg) # perform SPI communication (reads and writes in one line)
    
        msg[0] = msg[0] & 0x3F   # Set first two checksum bits to 0 (0x3F is 0b00111111
        msg[0] <<= 8   # Left shift first response byte to pad it out to 16 bits
        pos = msg[0] | msg[1]   # Concatenate the two response bytes using bitwise OR 
        value = pos*(360/16384) # Convert encoder position to angle in degrees (max encoder value at 1 rotation is 2^14 or 16384)
        
        prev = self.prevMotorAngle - 360*self.numTurns
        
        
        # Check if motor changed from 0 to 360 or vice versa and update numTurns
        if prev > 330 and value < 30:
            self.numTurns += 1
        elif prev < 30 and value > 330:
            self.numTurns -= 1
        
        # Update angle values
        self.prevMotorAngle = self.currMotorAngle
        
        self.currMotorAngle = value + 360*self.numTurns
        glb.logger.queueLog("Motor Angle: " + str(self.currMotorAngle), 1) #FIXME: implement logging level


    # Runs the stepper motor by sending GPIO signal to the teensey 4.0
    def actuateMotor(self) -> None:        
        if (self.limit_switch.value == False):  # checks that the limit switch is not pressed
            self.motor_enable.value = True
            
            # select actuation direction based on the angle returned by the controller
            if(self.cmdAngle > self.currPaddleAngle):
                self.motor_spin.value = False
        
            elif(self.cmdAngle < self.currPaddleAngle):
                self.motor_spin.value = True
        
        # if the limit switch is pressed but it's trying to go up, then let it
        elif (self.limit_switch.value == True and self.cmdAngle > self.currPaddleAngle):
            self.motor_enable.value = True
            self.motor_spin.value = False
            
        # if the limit switch is pressed but it's trying to go down, then don't let it
        elif (self.limit_switch.value == True and self.cmdAngle < self.currPaddleAngle):
            self.motor_enable.value = False


    # set the motor enable pin low to stop it from moving
    def stopMotor(self) -> None:
        self.motor_enable.value = False

    
    # set values for the paddles to retract until the limit switch is pressed, then update the main state machine
    def retractPaddles(self):
        if(self.limit_switch.value == False): # move down while the limit switch is not pressed
            self.motor_enable.value = True
            self.motor_spin.value = True
        elif(self.limit_switch.value == True):
            self.motor_enable.value = False # stop moving
            glb.mainSM.retracted = True # tell the main state machine that the paddles are retracted
            
    
    # Gets an average of the 5 most recent sensor values of the specified type, helps to guard against noise
    def getCurrData(self, dataType):
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
        
        
