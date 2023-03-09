import time
import globals as glb
from Controller import Controller


lastTick = 0


def setup():
    control = Controller(1,1,1)
    control.loadRefData(772, 275)
    print(control.getTimeIndex(0.005))


def loop():
    return
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
