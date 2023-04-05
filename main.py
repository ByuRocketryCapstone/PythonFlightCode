import time
import globals as glb
from Controller import Controller





def setup():
    pass


def loop():
    if (time.time() - glb.lastTick > glb.TICK_RATE):
        #glb.mainSM.mainTick()
        glb.sensorControl.sensorTick()
        #glb.motorControl.motorTick()
        glb.logger.logTick()
        glb.lastTick = time.time()
 
    
 
    if (time.time() - glb.printTick > 1):
        print(glb.dataList[-1].__str__())
        glb.printTick = time.time()

setup()
while(1):#not glb.fake_data_flag):
    loop()
    


