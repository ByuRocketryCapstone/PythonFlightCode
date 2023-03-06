import Logger as log
from MainSM import mainStateMachine
import time
import math
from enum import Enum

# constants 
LOG_FILE_NAME = "LogFiles/currLog.txt"
MAX_PADDLE_ANGLE = 65 * (math.pi/180)
START_TIME = time.time()

MAIN_TICK_RATE = 1/10           # tick rate of 10 Hz for the main state machine
SENSOR_TICK_RATE = 1/20         # tick rate of 10 Hz for the main state machine
MOTOR_TICK_RATE = 1/20          # tick rate of 10 Hz for the main state machine
LOG_TICK_RATE = 1/10            # tick rate of 10 Hz for the main state machine

mainSM = mainStateMachine()

logger = log.Logger(LOG_FILE_NAME)


class loglv(Enum):
    FLIGHT = 1
    TEST = 2

LOG_LEVEL = loglv.TEST

