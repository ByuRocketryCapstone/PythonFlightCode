import time
import globals as glb
from Controller import Controller


lastTick = 0


def setup():
    pass


def loop():
    if (time.time() - lastTick > glb.TICK_RATE):
        glb.mainSM.mainTick()
        glb.sensorControl.sensorTick()
        glb.motorControl.motorTick()
        glb.logger.logTick()
        lastTick = time.time()



setup()
while(True):
    loop()
    break
