import time
import globals as glb
from Controller import Controller
import traceback




# put any code here that should run just once at startup
def setup():
    pass


# put code here that runs in a loop during normal operation
def loop():
    if (time.time() - glb.lastTick > glb.TICK_RATE):
        glb.mainSM.mainTick()
        glb.sensorControl.sensorTick()
        glb.motorControl.motorTick()
        glb.logger.logTick()
        glb.lastTick = time.time()
        


try:
    setup()
    while(1):
        loop()
except:
    # retrieve and log error message
    errorMsg = traceback.format_exc()
    glb.logger.queueLog(errorMsg, 1) #FIXME: implement logging level
    glb.logger.logTick()
    print("Error occurred: " + errorMsg)
    
    # retract paddles before quitting program
    errorTime = time.time()
    glb.motorContol.retract = True
    while time.time() - errorTime > 10:
        glb.motorControl.motorTick()
    exit(0)
    




