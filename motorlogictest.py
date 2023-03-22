import board
import digitalio


cmdAngle = 1
currPaddleAngle = 5


motor_enable = digitalio.DigitalInOut(board.D12)
motor_enable.direction = digitalio.Direction.OUTPUT
        
        
motor_spin = digitalio.DigitalInOut(board.D13)
motor_spin.direction = digitalio.Direction.OUTPUT
        
limit_switch = digitalio.DigitalInOut(board.D0)
limit_switch.direction = digitalio.Direction.INPUT


led = digitalio.DigitalInOut(board.D16)
led.direction = digitalio.Direction.OUTPUT

led1 = digitalio.DigitalInOut(board.D20)
led1.direction = digitalio.Direction.OUTPUT

led2 = digitalio.DigitalInOut(board.D21)
led2.direction = digitalio.Direction.OUTPUT

while True:

        
        if (limit_switch.value == False or (limit_switch.value == True and cmdAngle > currPaddleAngle)):
            motor_enable.value = True
            
        
            if(cmdAngle > currPaddleAngle):
                motor_spin.value = True
        
            elif(cmdAngle < currPaddleAngle):
                motor_spin.value = False
            
        elif (limit_switch.value == True and cmdAngle < currPaddleAngle):
            motor_enable.value = False
            
        elif (limit_switch.value == False and (cmdAngle == currPaddleAngle)):
            motor_enable.value = False