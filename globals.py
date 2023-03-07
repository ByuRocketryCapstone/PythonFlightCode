from Logger import Logger
from MainSM import mainStateMachine
from SensorControl import SensorControl
from MotorControl import MotorControl
import time
import math
from enum import Enum

# constants 
LOG_FILE_NAME = "LogFiles/currLog.txt"
MAX_PADDLE_ANGLE = 65 * (math.pi/180)
START_TIME = time.time()

TICK_RATE = 1/100   # tick rate of 100 Hz

mainSM = mainStateMachine()
sensorControl = SensorControl()
motorControl = MotorControl()
pi = 3.1415962

logger = Logger(LOG_FILE_NAME)


class loglv(Enum):
    FLIGHT = 1
    TEST = 2

LOG_LEVEL = loglv.TEST

