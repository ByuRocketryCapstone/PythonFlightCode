import time
import globals as glb


lastTick = 0


def setup():
    pass


def loop():

    if (time.time() - lastTick > glb.TICK_RATE):
        glb.mainSM.mainTick()
        glb.sensorControl.sensorTick()
        glb.motorControl.motorTick()
        glb.logger.logTick()
        lastTick = 0



setup()
while(True):
    loop()
    break
