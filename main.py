import time
import globals as glb
from Controller import Controller
import traceback





def setup():
    pass


def loop():
    if (time.time() - glb.lastTick > glb.TICK_RATE):
        #glb.mainSM.mainTick()
        glb.sensorControl.sensorTick()
        glb.motorControl.motorTick()
        glb.logger.logTick()
        glb.lastTick = time.time()
        
    
    if glb.dataList[-1].a > 10:
        glb.ignition_flag = True
        glb.sensorControl.enable = True
        glb.sensorControl.log_data_flag = True
    if glb.ignition_flag == True and glb.dataList[-1].a < -5:
        glb.ignition_flag = False
        glb.CUTOFF_TIME = time.time()
        glb.coasting_flag = True
        glb.motorControl.enable = True
    if glb.coasting_flag == True and time.time() - glb.CUTOFF_TIME > 8:
        glb.motorControl.retract = True
    if glb.coasting_flag == True and time.time() - glb.CUTOFF_TIME > 300:
        glb.sensorControl.enable = False
        exit(0)
        
    
 
    
 
    #if (time.time() - glb.printTick > 1):
        #print(glb.dataList[-1].__str__())
        #glb.printTick = time.time()

try:
    setup()
    while(1):
        loop()
except:
    errorMsg = traceback.format_exc()
    glb.logger.queueLog(errorMsg, 1) #FIXME: implement logging level
    glb.logger.logTick()
    print("Error occurred: " + errorMsg)
    errorTime = time.time()
    glb.motorContol.retract = True
    while time.time() - errorTime > 10:
        glb.motorControl.motorTick()
    exit(0)
    




