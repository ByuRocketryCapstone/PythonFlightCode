import Logger as log
from MainSM import mainStateMachine
import time
import math
from enum import Enum

# constants 
LOG_FILE_NAME = "LogFiles/currLog.txt"
MAX_PADDLE_ANGLE = 65 * (math.pi/180)
START_TIME = time.time()

logger = log.Logger(LOG_FILE_NAME)
mainSM = mainStateMachine()
pi = 3.1415962

class loglv(Enum):
    FLIGHT = 1
    TEST = 2

LOG_LEVEL = loglv.TEST

