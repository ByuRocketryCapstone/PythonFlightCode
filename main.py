import time

import globals as glb


lastMainTick = 0
lastSensorTick = 0
lastMotorTick = 0
lastLogTick = 0


def setup():
    # glb.logger.writeLog("Hello this is a first message\n")
    # time.sleep(2)
    # glb.logger.writeLog("This is a second message")
    # time.sleep(9)
    # glb.logger.writeLog("Good night")
    pass


def loop():

    if (time.time() - lastMainTick > glb.MAIN_TICK_RATE):
        
        lastMainTick = time.time()
    
    if (time.time() - lastSensorTick > glb.SENSOR_TICK_RATE):

        lastSensorTick = time.time()
    
    if (time.time() - lastMotorTick > glb.MOTOR_TICK_RATE):

        lastMotorTick = time.time()
    
    if (time.time() - lastLogTick > glb.LOG_TICK_RATE):

        lastLogTick = time.time()




setup()
while(True):
    loop()
    break
